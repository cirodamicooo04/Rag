from pydantic import BaseModel


class DocumentDTO(BaseModel):
    file_hash: str
    file_name:str
    file_type:str
    status:str
    total_chunks: int
    indexed_chunks: int
    quarantined_chunks: int

    class Config:
        from_attributes = True