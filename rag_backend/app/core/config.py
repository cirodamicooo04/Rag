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
TOP_K = 5

INITIALIZE_GUARDRAILS_DB = False
STRUCTURED_PROMPT = True
SEMANTIC_SIMILARITY_CONTROL = True
SECURITY_TRESHOLD = 0.86

HF_TOKEN = os.getenv("HF_TOKEN")