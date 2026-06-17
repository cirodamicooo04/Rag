from pydantic import ConfigDict

from app.db.models import Document
from app.schemas.utils import CamelModel


class DocumentDTO(CamelModel):
    file_hash: str
    file_name:str
    file_type:str
    status:str
    total_chunks: int = 0
    indexed_chunks: int = 0
    quarantined_chunks: int = 0

    model_config = ConfigDict(from_attributes=True)

def to_document_dto(doc: Document):
    return DocumentDTO.model_validate(doc)