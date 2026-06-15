from app.schemas.utils import CamelModel


class QuarantinedChunksDTO(CamelModel):
    chunk_id: str
    chunk_index: int
    security_status: str
    security_reason: str | None = None
    text: str


class QuarantinedDocumentDTO(CamelModel):
    file_hash: str
    quarantined_chunks: list[QuarantinedChunksDTO]

