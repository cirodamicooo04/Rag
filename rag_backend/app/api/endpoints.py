import shutil
from pathlib import Path

from fastapi import FastAPI, APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import UPLOAD_DIR
from app.core.utils import sha256_file, deterministic_chunk_id
from app.crud import crud_docs
from app.db.database import get_db
from app.schemas.document import DocumentDTO
from app.services import ingester, chunker, indexer, query

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
            chunks = chunker.semantic_chunk(doc.text)

            for i, text_content in enumerate(chunks):
                chunk_id = deterministic_chunk_id(doc.file_hash,0,i)

                crud_docs.create_chunk(db,chunk_id=chunk_id, doc_hash=doc.file_hash, text=text_content, index=i)

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

    if not chunks_to_index:
        return {"message": "No chunks to index"}

    try:
        indexer.index(chunks_to_index)

        for c in chunks_to_index:
            crud_docs.mark_chunk_as_indexed(db, c.chunk_id)

    except Exception as e:
        print(f"Error indexing chunks: {e}")
        raise HTTPException(status_code=500, detail="Error indexing chunks")

    return {"message": "Chunks indexed successfully"}

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