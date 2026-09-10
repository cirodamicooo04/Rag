from app.core.config import QDRANT_URL
from qdrant_client import QdrantClient, AsyncQdrantClient

qdrant_client = QdrantClient(QDRANT_URL)
async_qdrant_client = AsyncQdrantClient(QDRANT_URL)