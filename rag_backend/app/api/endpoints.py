import shutil
from pathlib import Path

from fastapi import FastAPI, APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import UPLOAD_DIR, NORMALIZATION_DOCUMENT, LLAMA_GUARD_DOCUMENT_SCAN
from app.core.utils import sha256_file, deterministic_chunk_id
from app.crud import crud_docs
from app.db.database import get_db
from app.schemas.document import DocumentDTO
from app.services import ingester, chunker, indexer, query
from app.services.document_parser import remove_document_header, parse_document_metadata
from app.guardrails.document.layers.normalizer import normalize_document_text
from app.guardrails.document.layers.llm_guard import classify_chunk

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
    quarantined_chunks_count = 0

    if not chunks_to_index:
        return {"message": "No chunks to index"}

    try:
        safe_chunks = []

        if LLAMA_GUARD_DOCUMENT_SCAN:
            for c in chunks_to_index:
                guard_decision = classify_chunk(c.text)
                if not guard_decision.is_safe:
                    crud_docs.mark_chunk_as_quarantined(db, c.chunk_id)
                    quarantined_chunks_count += 1

                    print(f"Chunk {c.chunk_id} marked as quarantined. - Score: {guard_decision.score}")
                else:
                    safe_chunks.append(c)

            if not safe_chunks:
                return {"message": "All chunks to index marked as quarantined. No chunks indexed."}

            chunks_to_index = safe_chunks


        indexer.index(chunks_to_index)

        for c in chunks_to_index:
            crud_docs.mark_chunk_as_indexed(db, c.chunk_id)

    except Exception as e:
        print(f"Error indexing chunks: {e}")
        raise HTTPException(status_code=500, detail="Error indexing chunks")

    return {"message": f"Chunks indexed successfully with {quarantined_chunks_count} quarantined chunks "}

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

@router.get("/docs", response_model=list[DocumentDTO])
async def get_document_status(db: Session = Depends(get_db)):
    return crud_docs.get_all_documents(db)

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
