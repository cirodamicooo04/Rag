from llama_index.core import Settings
from transformers import AutoTokenizer
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI

from app.core.config import EMBEDDING_MODEL, LLM_MODEL, LM_STUDIO_BASE_URL

tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL)
embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)
llm = OpenAI(model=LLM_MODEL,api_base=LM_STUDIO_BASE_URL,api_key="not_needed",temperature=0.02,context_window=4096,is_chat_model=True)

Settings.llm = llm
Settings.embed_model=embed_model