from app.db.models import Chunk, Conversation, BlockedRequest, ConversationMessage

from app.db.models import Document


def get_documents_by_status(db, status):
    return  db.query(Document).filter(Document.status == status).all()

def get_all_documents(db,hashes=None):
    query = db.query(Document)

    if hashes and len(hashes) > 0:
        query = query.filter(Document.file_hash.in_(hashes))

    return query.all()

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

def create_document_for_processing(db, file_hash, file_name, file_path, file_type):
    document = Document(file_hash=file_hash, file_name=file_name, file_path=file_path, file_type=file_type, status="PROCESSING")
    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def create_chunk(db, chunk_id, doc_hash, text, index, title, scope, category, source_url, scraping_date):
    chunk = Chunk(chunk_id=chunk_id,document_hash=doc_hash,text=text,chunk_index=index, title=title, scope=scope, category=category, source_url=source_url, scraping_date=scraping_date)
    db.add(chunk)
    db.commit()
    db.refresh(chunk)
    return chunk

def update_document_status(db, file_hash, new_status):
    db.query(Document).filter(Document.file_hash == file_hash).update({"status": new_status})
    db.commit()

def get_unindexed_chunks(db):
    return db.query(Chunk).filter(Chunk.indexed == False).filter(Chunk.security_status == "PENDING").all()

def mark_chunk_as_indexed(db, chunk):
    db.query(Chunk).filter(Chunk.chunk_id == chunk.chunk_id).update({"indexed": True, "security_status": "SAFE", "security_reason": "Passed scan or manually approved"})
    db.commit()

def create_conversation(db, user_id, title):
    conversation = Conversation(user_id=user_id, title=title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation

def delete_dataset(db):
    db.query(Document).delete()
    db.query(Chunk).delete()
    db.commit()


def mark_chunk_as_quarantined(db, chunk, reason):
    db.query(Chunk).filter(Chunk.chunk_id == chunk.chunk_id).update({"indexed": False,"security_status": "QUARANTINED","security_reason": reason})
    db.commit()

def update_document_index_status(db, document_hash):
    chunks = (db.query(Chunk).filter(Chunk.document_hash == document_hash).all())

    document = (db.query(Document).filter(Document.file_hash == document_hash).first())

    if not document:
        return None

    if not chunks:
        db.query(Document).filter(Document.file_hash == document_hash).delete()
        db.commit()
        return None

    indexed_count = sum(1 for c in chunks if c.indexed)
    quarantined_count = sum(1 for c in chunks if c.security_status == "QUARANTINED")
    pending_count = sum(1 for c in chunks if c.security_status == "PENDING")

    if pending_count > 0:
        document.status = "CHUNKED"

    elif indexed_count == len(chunks):
        document.status = "INDEXED"

    elif indexed_count > 0 and quarantined_count > 0:
        document.status = "PARTIALLY_INDEXED"

    elif indexed_count == 0 and quarantined_count > 0:
        document.status = "REJECTED_SECURITY"

    else:
        document.status = "CHUNKED"

    db.commit()
    db.refresh(document)

    return document

def save_blocked_request(db, user_id, original_query, final_query, blocked_stage, blocked_by, reason):
    new_blocked_request = BlockedRequest(user_id=user_id, original_query=original_query, final_query=final_query, blocked_stage=blocked_stage, blocked_by=blocked_by, reason=reason)
    db.add(new_blocked_request)
    db.commit()


def get_indexed_chunks_by_doc_hash(db, doc_hash):
    return db.query(Chunk).filter(Chunk.document_hash == doc_hash).filter(Chunk.indexed == 1).all()


def delete_document(db, doc_hash):
    document = db.query(Document).filter(Document.file_hash == doc_hash).first()
    if document:
        db.delete(document)
    db.commit()


def get_quarantined_chunks_by_doc_hash(db, doc_hash):
    return db.query(Chunk).filter(Chunk.document_hash == doc_hash).filter(Chunk.security_status == "QUARANTINED").all()


def get_chunk_by_id(db, chunk_id):
    return db.query(Chunk).filter(Chunk.chunk_id == chunk_id).first()


def get_logs(db):
    return db.query(BlockedRequest).all()

def clear_logs(db):
    db.query(BlockedRequest).delete()
    db.commit()

def delete_log(db, id):
    db.query(BlockedRequest).filter(BlockedRequest.id == id).delete()
    db.commit()

def get_log_by_id(db, id):
    return db.query(BlockedRequest).filter(BlockedRequest.id == id).first()

def save_conversation_messages(db, id, messages):
    for message in messages:
        new_conv_message = ConversationMessage(conversation_id=id,role=message.role,sequence_number=message.sequence_number, content=message.content)
        db.add(new_conv_message)
    db.commit()


def get_saved_conversations(db, param):
    return db.query(Conversation).filter(Conversation.user_id == param).all()


def get_saved_conversation_by_id(db, id):
    return db.query(Conversation).filter(Conversation.id == id).first()


def delete_conversation_by_id(db, id):
    conversation = db.query(Conversation).filter(Conversation.id == id).first()

    if conversation:
        db.delete(conversation)
        db.commit()


def delete_chunk(db, chunk_id):
    chunk = db.query(Chunk).filter(Chunk.chunk_id == chunk_id).first()
    if chunk:
        db.delete(chunk)
        db.commit()