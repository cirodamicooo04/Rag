from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class Document(Base):
    __tablename__ = 'documents'

    file_hash = Column(String, primary_key=True, index=True)
    file_name = Column(String)
    file_path = Column(String)
    file_type = Column(String)
    text = Column(Text, nullable=True)
    status = Column(String, default="LOADED")

class Chunk(Base):
    __tablename__ = 'chunks'
    chunk_id = Column(String, primary_key=True, index=True)
    document_hash = Column(String, ForeignKey('documents.file_hash'), ondelete='CASCADE')
    text = Column(Text)
    chunk_index = Column(Integer)
    indexed = Column(Boolean, default=False)
    page = Column(Integer, default=0)

    #Permette di fare chunks.document per risalire al file originale
    document = relationship("Document", back_populates="chunks")