from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR : Path = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "docs"

INITIALIZE_GUARDRAILS_DB = False

#============================================================

#KEYCLOAK
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8089")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "rag-system")
KEYCLOAK_ISSUER = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}"
KEYCLOAK_JWKS_URL = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/certs"

#============================================================

#URL AND MODELS
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "rag_collection")

LLM_GUARD_MODEL = os.getenv("LLM_GUARD_MODEL", "meta-llama/Llama-Prompt-Guard-2-86M")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_LLM_MODEL = "openai/gpt-oss-120b"
GROQ_INTENT_CLASSIFIER_MODEL = "openai/gpt-oss-20b"
GROQ_OUTPUT_JUDGE_MODEL = "openai/gpt-oss-20b"
GROQ_DOCUMENT_CLASSIFIER_MODEL = "openai/gpt-oss-20b"

HF_TOKEN = os.getenv("HF_TOKEN")

#============================================================

#INDEXING
EMBEDDING_MODEL = "intfloat/multilingual-e5-base"
TOP_K = 5

#CHUNKING
MAX_TOKENS = 480
OVERLAP_TOKENS = 80


#============================================================

#DEFENSE LAYERS

#SYSTEM PROMPT
STRUCTURED_PROMPT = True
UNTRUSTED_CONTEXT_SYSTEM_PROMPT = True

#INPUT PIPELINE CONTROLS
NORMALIZATION_QUERY = True
LLM_GUARD_CONTROL = True
INTENT_CLASSIFIER_CONTROL = True

#DOCUMENT PIPELINE CONTROLS
NORMALIZATION_DOCUMENT = True
DOCUMENT_CLASSIFIER  = True

#OUTPUT PIPELINE CONTROLS
LLM_JUDGE_CONTROL = True




