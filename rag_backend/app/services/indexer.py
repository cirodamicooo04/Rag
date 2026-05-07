import json
from chunk import Chunk
from pathlib import Path

from llama_index.core import Document, StorageContext, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore

from app.core.config import COLLECTION_NAME
from app.core.db_clients import qdrant_client
from app.core.ml_models import embed_model
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
                         "page": c.page
                     }))

    client = qdrant_client
    vector_store = QdrantVectorStore(client=client, collection_name=COLLECTION_NAME)

    #Indica a lama index di usare Qdrant come vector store
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    print("Creazione indice...")
    index = (VectorStoreIndex.from_documents(llama_docs, storage_context=storage_context, show_progress=True))

    return index