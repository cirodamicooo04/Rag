from pathlib import Path
from app.core.config import NORMALIZATION_DOCUMENT, DOCUMENT_CLASSIFIER
from app.core.utils import deterministic_chunk_id
from app.crud import crud_docs
from app.db.database import SessionLocal
from app.guardrails.document.layers.document_classifier import DocumentCategory, classify_document
from app.guardrails.document.layers.normalizer import normalize_document_text
from app.services import ingester, chunker, indexer
from app.services.document_parser import remove_document_header, parse_document_metadata

def process_document_pipeline(file_hash: str, temp_path_str: str):
    db = SessionLocal()
    try:
        doc = crud_docs.get_document_by_hash(db, file_hash)
        if not doc:
            return

        extracted_text = ingester.process_document(Path(temp_path_str))
        if NORMALIZATION_DOCUMENT:
            extracted_text = normalize_document_text(extracted_text)
        crud_docs.update_document_text(db, file_hash, extracted_text, new_status="INGESTED")

        document_metadata = parse_document_metadata(extracted_text)
        clean_document_text = remove_document_header(extracted_text)
        chunks = chunker.semantic_chunk(clean_document_text)

        safe_chunks = []
        for i, text_content in enumerate(chunks):
            chunk_id = deterministic_chunk_id(file_hash, 0, i)
            chunk = crud_docs.create_chunk(
                db, 
                chunk_id=chunk_id, 
                doc_hash=file_hash, 
                text=text_content, 
                index=i, 
                title=document_metadata.get("title"), 
                scope=document_metadata.get("scope"), 
                category=document_metadata.get("category"), 
                source_url=document_metadata.get("source_url"), 
                scraping_date=document_metadata.get("scraping_date")
            )

            if DOCUMENT_CLASSIFIER:
                guard_decision = classify_document(chunk.text)
                if guard_decision.category in {DocumentCategory.MALICIOUS, DocumentCategory.UNKNOWN}:
                    crud_docs.mark_chunk_as_quarantined(db, chunk, reason=guard_decision.reason)
                    continue

            safe_chunks.append(chunk)

        crud_docs.update_document_status(db, file_hash, new_status="CHUNKED")

        if safe_chunks:
            indexer.index(safe_chunks)
            for chunk in safe_chunks:
                crud_docs.mark_chunk_as_indexed(db, chunk)

        crud_docs.update_document_index_status(db, file_hash)

    except Exception as e:
        crud_docs.update_document_status(db, file_hash, new_status="ERROR")
        print(f"Error processing document {file_hash}: {e}")
    finally:
        db.close()
        # Elimina il file temporaneo alla fine del processo per non intasare l'hard disk
        path_to_delete = Path(temp_path_str)
        if path_to_delete.exists():
            try:
                path_to_delete.unlink()
            except Exception as e:
                print(f"Errore durante l'eliminazione del file temporaneo {temp_path_str}: {e}")
