from llama_index.core import Document, StorageContext, VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client.http.models import FilterSelector, Filter, PointIdsList, MatchValue, FieldCondition

from app.core.config import COLLECTION_NAME
from app.core.db_clients import qdrant_client
from app.db.models import Chunk


def index(chunks: list[Chunk]):
    llama_docs = []
    for c in chunks:
        llama_docs.append(
            Document(text=c.text,
                     doc_id=c.chunk_id,
                     metadata={
                         "file_hash": c.document_hash,
                         "index": c.chunk_index,
                         "page": c.page,
                         "title": c.title,
                         "category": c.category,
                         "source_url": c.source_url,
                         "scraping_date": c.scraping_date,
                         "scope": c.scope,
                         "security_status": "safe",
                     }))

    client = qdrant_client
    vector_store = QdrantVectorStore(client=client, collection_name=COLLECTION_NAME)

    #Indica a lama index di usare Qdrant come vector store
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    print("Creazione indice...")
    index = (VectorStoreIndex.from_documents(llama_docs, storage_context=storage_context, show_progress=True))

    return index

def clean_index():
    client = qdrant_client
    #client.delete(collection_name=COLLECTION_NAME, points_selector=FilterSelector(filter=Filter(must=[])))
    client.delete_collection(collection_name=COLLECTION_NAME)

def remove_index(file_hash: str):
    client = qdrant_client
    client.delete(collection_name=COLLECTION_NAME, points_selector=Filter(must=[FieldCondition(key="file_hash",match=MatchValue(value=file_hash))]))
