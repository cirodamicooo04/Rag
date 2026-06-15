from app.db.database import SessionLocal
from app.crud.crud_docs import get_document_by_hash

db = SessionLocal()
doc_hash = "bf0169462dfe853b8642f2de444eb9f0f919faae03f738988ca222e3bd1fe559"
doc = get_document_by_hash(db, doc_hash)
if doc:
    print(f"Found: {doc.file_name}, hash: {doc.file_hash}")
else:
    print("Not found via SQLAlchemy")
db.close()
