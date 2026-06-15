from pydantic import BaseModel


class DocumentDTO(BaseModel):
    fileHash: str
    fileName:str
    file_type:str
    status:str
    totalChunks: int
    indexedChunks: int
    quarantinedChunks: int

    class Config:
        from_attributes = True