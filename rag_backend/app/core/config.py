from pathlib import Path

BASE_DIR : Path = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "docs"

EMBEDDING_MODEL = "intfloat/multilingual-e5-base"
MAX_TOKENS = 480
OVERLAP_TOKENS = 80

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "rag_collection"

LLM_MODEL = "gpt-3.5-turbo" #nome falso per ingannare la libreria
LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
TOP_K = 5