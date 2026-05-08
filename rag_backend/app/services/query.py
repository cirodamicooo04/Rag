from typing import List
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore

from app.core.config import COLLECTION_NAME, TOP_K
from app.core.db_clients import qdrant_client
from app.core.ml_models import llm

def build_prompt(context_chunks: List[str], query: str) -> str:
    context = "\n\n".join(context_chunks)
    return f"""
Sei l'assistente virtuale ufficiale del Corso di Studi / Laurea in Informatica dell'Università della Calabria.
Il tuo compito è fornire informazioni precise, aggiornate e cordiali basandoti esclusivamente sui documenti forniti.

Regole obbligatorie:
1. Non utilizzare conoscenze esterne.
2. Non inventare date o teorie.
3. Se il contesto è insufficiente, dichiaralo esplicitamente.
4. Se la domanda è generica, fornisci un riassunto dei punti principali presenti nel contesto
5. Mantieni struttura chiara e tono analitico.

CONTESTO:
{context}

DOMANDA:
{query}

RISPOSTA:
""".strip()


def get_answer(user_query: str):
    vector_store = QdrantVectorStore(client=qdrant_client,collection_name=COLLECTION_NAME)

    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    retriever = index.as_retriever(similarity_top_k=TOP_K)
    nodes = retriever.retrieve(f"query: {user_query}")

    if not nodes:
        return "Nessun risultato trovato."

    context_chunks = [n.node.text for n in nodes]

    full_prompt = build_prompt(context_chunks, user_query)
    response = llm.complete(full_prompt)

    return response.text