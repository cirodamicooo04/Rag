from pydantic import BaseModel


class DocumentDTO(BaseModel):
    file_name:str
    file_type:str
    status:str

    class Config:
        from_attributes = True