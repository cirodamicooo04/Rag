from datasets import load_dataset

from llama_index.core import Document, StorageContext, VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore

from app.core.config import GUARDRAILS_COLLECTION, HF_TOKEN
from app.core.db_clients import qdrant_client


def get_guardrail_documents():
    necent_data = load_dataset("Necent/llm-jailbreak-prompt-injection-dataset", split="train", streaming=True, token=HF_TOKEN)

    documents = []

    for row in necent_data.take(3000):
        documents.append(Document(
            text=row["prompt"],
            metadata={"category": "jailbreak", "source": "necent"}
        ))

    return documents

def run_indexing():
    docs = get_guardrail_documents()

    vector_store = QdrantVectorStore(client=qdrant_client, collection_name=GUARDRAILS_COLLECTION)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    VectorStoreIndex.from_documents(docs, storage_context=storage_context, show_progress=True)


