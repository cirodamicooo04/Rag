from llama_index.core import Settings
from transformers import AutoTokenizer
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.llms.groq import Groq

from app.core.config import EMBEDDING_MODEL, GROQ_LLM_MODEL, GROQ_API_KEY, GROQ_INTENT_CLASSIFIER_MODEL
tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL)
embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)
llm = Groq(model=GROQ_LLM_MODEL, api_key=GROQ_API_KEY, temperature=0.02)
intent_classifier_llm = Groq(model=GROQ_INTENT_CLASSIFIER_MODEL, api_key=GROQ_API_KEY, temperature=0)




Settings.llm = llm
Settings.embed_model=embed_model