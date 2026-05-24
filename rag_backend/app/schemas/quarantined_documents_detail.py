from pydantic import BaseModel

class QuarantinedChunksDTO(BaseModel):
    chunk_id: str
    chunk_index: int
    security_status: str
    security_reason: str | None = None
    text_preview: str

class QuarantinedDocumentDTO(BaseModel):
    file_hash: str
    quarantined_chunks: list[QuarantinedChunksDTO]

