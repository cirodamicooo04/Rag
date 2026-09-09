from pathlib import Path
import os
try:
    from dotenv import load_dotenv
except ImportError:  # environment variables still work without a .env loader
    def load_dotenv():
        return False

load_dotenv()


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

BASE_DIR : Path = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "docs"

#============================================================

#KEYCLOAK
KEYCLOAK_URL = "http://localhost:8089"
KEYCLOAK_REALM = "rag-system"
KEYCLOAK_ISSUER = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}"
KEYCLOAK_JWKS_URL = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/certs"

#============================================================

#URL AND MODELS
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "rag_collection"

LLM_GUARD_MODEL = "meta-llama/Llama-Prompt-Guard-2-86M"
LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_LLM_MODEL = "openai/gpt-oss-120b"
GROQ_INTENT_CLASSIFIER_MODEL = "llama-3.1-8b-instant"
GROQ_OUTPUT_JUDGE_MODEL = "openai/gpt-oss-20b"
GROQ_DOCUMENT_CLASSIFIER_MODEL = "openai/gpt-oss-20b"
GROQ_CONTEXT_CONSISTENCY_MODEL = "openai/gpt-oss-20b"

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

#RETRIEVAL PIPELINE CONTROLS
CONTEXT_CONSISTENCY_CONTROL = _env_bool("CONTEXT_CONSISTENCY_CONTROL", True)

#ASP CONTROL PLANE
# ASP orchestration mode: veto | orchestrator.
# In orchestrator mode ASP selects the next RAG action; Python only executes it.
# In veto mode the Python cascade decides and ASP may only downgrade the outcome
# to block / human_review.
ASP_MODE = os.getenv("ASP_MODE", "orchestrator").strip().lower()

ASP_RAG_CONFIDENCE_THRESHOLD = 60  # min confidence (0-100) to auto-trust a RAG_QUERY
ASP_OUTPUT_CONFIDENCE_THRESHOLD = 60  # min confidence (0-100) to trust a SAFE output label
ASP_MIN_RETRIEVAL_SCORE = 55
ASP_MIN_DOCUMENT_TRUST = 50
ASP_MIN_USABLE_CHUNKS = 1
ASP_MAX_RETRIEVAL_ATTEMPTS = 2
ASP_MAX_GENERATION_ATTEMPTS = 2
ASP_CONTEXT_CONTRADICTION_CONFIDENCE = 0.80

# Account-risk window feeding recent_security_events/1.  Only security-relevant
# blocks count: a topical refusal (out_of_scope) is not a security event.
ASP_SECURITY_EVENT_WINDOW_HOURS = 24
