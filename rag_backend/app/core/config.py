from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR : Path = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "docs"

EMBEDDING_MODEL = "intfloat/multilingual-e5-base"
MAX_TOKENS = 480
OVERLAP_TOKENS = 80

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "rag_collection"
GUARDRAILS_COLLECTION = "input_guardrails"

LLM_MODEL = "gpt-3.5-turbo" #nome falso per ingannare la libreria
LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_LLM_MODEL = "openai/gpt-oss-120b"
GROQ_INTENT_CLASSIFIER_MODEL = "llama-3.1-8b-instant"
GROQ_OUTPUT_JUDGE_MODEL = "openai/gpt-oss-20b"

TOP_K = 5

INITIALIZE_GUARDRAILS_DB = False
STRUCTURED_PROMPT = True

#LLM GUARD
LLM_GUARD_MODEL = "meta-llama/Llama-Prompt-Guard-2-86M"

#INPUT PIPELINE CONTROLS
NORMALIZATION_QUERY = True
SEMANTIC_SIMILARITY_CONTROL = False
SECURITY_TRESHOLD = 0.85
LLM_GUARD_CONTROL = True
INTENT_CLASSIFIER_CONTROL = True

#DOCUMENT PIPELINE CONTROLS
NORMALIZATION_DOCUMENT = True
LLAMA_GUARD_DOCUMENT_SCAN = True
UNTRUSTED_CONTEXT_SYSTEM_PROMPT = True

#OUTPUT PIPELINE CONTROLS
LLM_JUDGE_CONTROL = True




HF_TOKEN = os.getenv("HF_TOKEN")