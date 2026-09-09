from app.core.config import QDRANT_URL
from qdrant_client import QdrantClient

qdrant_client = QdrantClient(QDRANT_URL)