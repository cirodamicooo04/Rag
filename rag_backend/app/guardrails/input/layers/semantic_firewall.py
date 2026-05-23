from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore

from app.core.config import GUARDRAILS_COLLECTION, SECURITY_TRESHOLD
from app.core.db_clients import qdrant_client


def is_safe_query(query: str) -> bool:
    vector_store = QdrantVectorStore(client=qdrant_client,collection_name=GUARDRAILS_COLLECTION)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    retriever = index.as_retriever(similarity_top_k=5)

    nodes = retriever.retrieve(query)

    if not nodes:
        return True

    best_node = nodes[0]

    if best_node.score > SECURITY_TRESHOLD:
        print(f"Guardrail blocked query from score: {best_node.score:.3f}")
        return False

    return True