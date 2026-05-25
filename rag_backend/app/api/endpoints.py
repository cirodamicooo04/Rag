import shutil
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import UPLOAD_DIR, NORMALIZATION_DOCUMENT, DOCUMENT_CLASSIFIER
from app.core.utils import sha256_file, deterministic_chunk_id
from app.crud import crud_docs
from app.db.database import get_db
from app.schemas.document import DocumentDTO
from app.schemas.quarantined_documents_detail import QuarantinedDocumentDTO, QuarantinedChunksDTO
from app.services import ingester, chunker, indexer, query
from app.services.document_parser import remove_document_header, parse_document_metadata
from app.guardrails.document.layers.normalizer import normalize_document_text
from app.guardrails.document.layers.document_classifier import DocumentCategory, classify_document

router = APIRouter()

last_conversation = {}


@router.post("/upload")
async def upload_document(file: UploadFile = File(...) ,db: Session = Depends(get_db)):
    temp_path = UPLOAD_DIR / Path(file.filename).name

    try:
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while saving file: {e}")

    file_hash = sha256_file(temp_path)

    existing = crud_docs.get_document_by_hash(db, file_hash)
    if existing:
        try:
            temp_path.unlink()
        except Exception as e:
            print(f"Error while deleting temp file: {e}")

        raise HTTPException(status_code=409,detail="Document already exists")

    extension = Path(temp_path).suffix.lower()
    new_document = crud_docs.create_document(db, file_hash, file.filename, str(temp_path), extension)

    return {"message": "Document uploaded successfully", "filename": new_document.file_name, "hash": new_document.file_hash}




@router.post("/ingest")
async def ingest_documents(db: Session = Depends(get_db)):
    docs_to_process = (crud_docs.get_documents_by_status(db, status="LOADED"))
    error_while_ingesting = False

    for doc in docs_to_process:
        try:
            extracted_text = ingester.process_document(Path(doc.file_path))
            if NORMALIZATION_DOCUMENT:
                extracted_text = normalize_document_text(extracted_text)

            crud_docs.update_document_text(db, doc.file_hash, extracted_text, new_status="INGESTED")
        except Exception as e:
            crud_docs.update_document_status(db, doc.file_hash, new_status="ERROR")
            print(f"Error processing document {doc.file_hash}: {e}")
            error_while_ingesting = True

    if error_while_ingesting:
        raise HTTPException(status_code=500, detail="Error while ingesting some documents")


    return {"message": "Documents processed successfully"}


@router.post("/chunk")
async def make_chunks(db: Session = Depends(get_db)):
    docs_to_process = crud_docs.get_documents_by_status(db, status="INGESTED")
    error_while_chunking = False

    for doc in docs_to_process:
        try:
            document_metadata = parse_document_metadata(doc.text)
            clean_document_text = remove_document_header(doc.text)

            chunks = chunker.semantic_chunk(clean_document_text)

            for i, text_content in enumerate(chunks):
                chunk_id = deterministic_chunk_id(doc.file_hash,0,i)

                crud_docs.create_chunk(db,chunk_id=chunk_id, doc_hash=doc.file_hash, text=text_content, index=i, title=document_metadata.get("title"), scope=document_metadata.get("scope"), category=document_metadata.get("category"), source_url=document_metadata.get("source_url"), scraping_date=document_metadata.get("scraping_date"))


            crud_docs.update_document_status(db, doc.file_hash, new_status="CHUNKED")
        except Exception as e:
            crud_docs.update_document_status(db, doc.file_hash, new_status="ERROR_CHUNKING")
            print(f"Error processing document {doc.file_hash}: {e}")
            error_while_chunking = True

    if error_while_chunking:
        raise HTTPException(status_code=500, detail="Error while chunking some documents")

    return {"message": "Chunking completed"}

@router.post("/index")
async def index_chunks(db: Session = Depends(get_db)):
    chunks_to_index = crud_docs.get_unindexed_chunks(db)

    indexed_count = 0
    quarantined_count = 0
    affected_documents = set()

    if not chunks_to_index:
        return {"message": "No chunks to index"}

    try:
        safe_chunks = []
        for chunk in chunks_to_index:
            affected_documents.add(chunk.document_hash)
            if DOCUMENT_CLASSIFIER:
                guard_decision = classify_document(chunk.text)
                if guard_decision.category in {DocumentCategory.MALICIOUS, DocumentCategory.UNKNOWN}:
                    crud_docs.mark_chunk_as_quarantined(
                        db,
                        chunk,
                        reason=guard_decision.reason
                    )

                    quarantined_count += 1
                    print(
                        f"Chunk {chunk.chunk_id} quarantined. "
                        f"Confidence={guard_decision.confidence}, "
                    )
                    continue

            safe_chunks.append(chunk)

        if safe_chunks:
            indexer.index(safe_chunks)
            for chunk in safe_chunks:
                crud_docs.mark_chunk_as_indexed(db, chunk)
                indexed_count += 1

    except Exception as e:
        print(f"Error indexing chunks: {e}")
        raise HTTPException(status_code=500, detail="Error indexing chunks")
    finally:
        for document_hash in affected_documents:
            crud_docs.update_document_index_status(db, document_hash)

    return {
        "message": "Indexing completed",
        "indexed_chunks": indexed_count,
        "quarantined_chunks": quarantined_count,
        "affected_documents": len(affected_documents),
    }

@router.post("/ask")
async def ask_query(question: str):
    if not question.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        answer = query.get_answer(question)

        global last_conversation
        last_conversation = {"question": question, "answer": answer}

        return {"answer": answer}
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Error processing query")

@router.get("/docs")
async def get_document_status(db: Session = Depends(get_db)):
    docs = crud_docs.get_all_documents(db)

    result = []

    for doc in docs:
        total_chunks = len(doc.chunks)
        indexed_chunks = sum(1 for chunk in doc.chunks if chunk.indexed)
        quarantined_chunks = sum(1 for chunk in doc.chunks if chunk.security_status == "QUARANTINED")

        result.append(
            DocumentDTO(file_hash=doc.file_hash,
                        file_name=doc.file_name,
                        file_type=doc.file_type,
                        status=doc.status,
                        total_chunks=total_chunks,
                        indexed_chunks=indexed_chunks,
                        quarantined_chunks=quarantined_chunks
            )
        )

    return result

@router.get("/docs/{doc_hash}/security_summary")
async def get_document_security_summary(doc_hash: str, db: Session = Depends(get_db)):
    document = crud_docs.get_document_by_hash(db, doc_hash)
    if not document:
        raise HTTPException(status_code=404, detail=f"Document with hash: {doc_hash} not found")

    chunks = crud_docs.get_quarantined_chunks_by_doc_hash(db, doc_hash)

    return QuarantinedDocumentDTO(
        file_hash=doc_hash,
        quarantined_chunks=[
            QuarantinedChunksDTO(
                chunk_id=chunk.chunk_id,
                chunk_index=chunk.chunk_index,
                security_status=chunk.security_status,
                security_reason=chunk.security_reason,
                text_preview=chunk.text
            )
            for chunk in chunks
        ]
    )

@router.post("/chunks/{chunk_id}/approve")
async def approve_chunk(chunk_id: str, db: Session = Depends(get_db)):
    chunk = crud_docs.get_chunk_by_id(db, chunk_id)
    if not chunk:
        raise HTTPException(status_code=404, detail=f"Chunk with id: {chunk_id} not found")

    if chunk.security_status != "QUARANTINED":
        raise HTTPException(status_code=400, detail=f"Chunk with id: {chunk_id} is not quarantined")

    try:
        indexer.index([chunk])
        crud_docs.mark_chunk_as_indexed(db, chunk)
        crud_docs.update_document_index_status(db, chunk.document_hash) #Aggiorno lo stato del documento padre
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error indexing chunk: {e}")

    return {"message": "Chunk approved and indexed successfully"}

@router.post("/docs/{doc_hash}/approve")
async def approve_document(doc_hash: str, db: Session = Depends(get_db)):
    document = crud_docs.get_document_by_hash(db, doc_hash)
    if not document:
        raise HTTPException(status_code=404, detail=f"Document with hash: {doc_hash} not found")

    if document.status not in ["PARTIALLY_INDEXED","REJECTED_SECURITY"]:
        raise HTTPException(status_code=400, detail=f"Document with hash: {doc_hash} is not partially indexed or rejected security")

    doc_chunks = document.chunks
    chunks_to_approve = [chunk for chunk in doc_chunks if chunk.security_status == "QUARANTINED"]

    if not chunks_to_approve:
        raise HTTPException(status_code=400, detail=f"Document with hash: {doc_hash} has no quarantined chunks")

    try:
        indexer.index(chunks_to_approve)
        for chunk in chunks_to_approve:
            crud_docs.mark_chunk_as_indexed(db, chunk)
        crud_docs.update_document_index_status(db, doc_hash)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error indexing chunks: {e}")

    return {"message": "Document approved and indexed successfully"}



@router.post("/save-last")
async def save_last_conversation(db: Session = Depends(get_db)):
    global last_conversation
    crud_docs.save_conversation(db, last_conversation["question"], last_conversation["answer"])
    return {"message": "Conversation saved successfully"}

@router.get("/saved-conversations")
async def get_saved_conversations(db: Session = Depends(get_db)):
    return crud_docs.get_all_conversations(db)

@router.delete("/delete-conversations/{id}")
def delete_conversation(id: int, db: Session = Depends(get_db)):
    conversation = crud_docs.get_conversation(id,db)

    if conversation is None:
        raise HTTPException(status_code=404, detail=f"Conversation with id: {id} not found")

    crud_docs.delete_conversation(id,db)
    return {"message": "Conversation deleted successfully"}

@router.post("/reset-dataset")
def reset_dataset(db: Session = Depends(get_db)):
    directory = Path(UPLOAD_DIR)
    #Svuoto cartella docs
    if directory.exists():
        for elemento in directory.iterdir():
            if elemento.name == ".gitkeep":
                continue
            elemento.unlink()

    #Cancello tutti i documenti salvati
    crud_docs.delete_dataset(db)

    #Svuoto il dataset vettoriale
    indexer.clean_index()
    return {"message": "Dataset reset successfully"}

@router.delete("/delete-document/{doc_hash}")
def delete_document(doc_hash: str,db: Session = Depends(get_db)):
    document = crud_docs.get_document_by_hash(db, doc_hash)
    if not document:
        raise HTTPException(status_code=404, detail=f"Document with hash: {doc_hash} not found")

    indexed_chunks = crud_docs.get_indexed_chunks_by_doc_hash(db, doc_hash)

    try:
        if indexed_chunks: #Ci sono chunks indicizzati
            indexer.remove_index(doc_hash) #Rimuovo dall'index
        crud_docs.delete_document(db, doc_hash)
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {e}")
