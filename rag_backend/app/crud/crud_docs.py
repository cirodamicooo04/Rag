from app.db.models import Chunk, Conversation

from app.db.models import Document


def get_documents_by_status(db, status):
    return  db.query(Document).filter(Document.status == status).all()

def get_all_documents(db):
    return db.query(Document).all()

def update_document_text(db, file_hash, extracted_text, new_status):
    db.query(Document).filter(Document.file_hash == file_hash).update({"text": extracted_text, "status": new_status})
    db.commit()

def get_document_by_hash(db, file_hash):
    return db.query(Document).filter(Document.file_hash == file_hash).first()

def create_document(db, file_hash, file_name, file_path, file_type):
    document = Document(file_hash=file_hash, file_name=file_name, file_path=file_path, file_type=file_type)
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def create_chunk(db, chunk_id, doc_hash, text, index):
    chunk = Chunk(chunk_id=chunk_id,document_hash=doc_hash,text=text,chunk_index=index)
    db.add(chunk)
    db.commit()
    db.refresh(chunk)
    return chunk

def update_document_status(db, file_hash, new_status):
    db.query(Document).filter(Document.file_hash == file_hash).update({"status": new_status})
    db.commit()

def get_unindexed_chunks(db):
    return db.query(Chunk).filter(Chunk.indexed == False).all()

def mark_chunk_as_indexed(db, chunk_id):
    db.query(Chunk).filter(Chunk.chunk_id == chunk_id).update({"indexed": True})
    db.commit()

def save_conversation(db, user_query, response):
    new_conv = Conversation(question=user_query, answer=response)
    db.add(new_conv)
    db.commit()
    db.refresh(new_conv)
    return new_conv

def get_all_conversations(db):
    return db.query(Conversation).all()

def get_conversation(id, db):
    return db.query(Conversation).filter(Conversation.id == id).first()


def delete_conversation(id, db):
    db.query(Conversation).filter(Conversation.id == id).delete()
    db.commit()