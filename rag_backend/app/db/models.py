from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base

class Document(Base):
    __tablename__ = 'documents'

    file_hash = Column(String, primary_key=True, index=True)
    file_name = Column(String)
    file_path = Column(String)
    file_type = Column(String)
    text = Column(Text, nullable=True)
    status = Column(String, default="LOADED")

    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

class Chunk(Base):
    __tablename__ = 'chunks'
    chunk_id = Column(String, primary_key=True, index=True)
    document_hash = Column(String, ForeignKey('documents.file_hash',  ondelete='CASCADE'))
    text = Column(Text)
    chunk_index = Column(Integer)
    indexed = Column(Boolean, default=False)
    security_status = Column(String, default="PENDING")
    security_reason = Column(String, nullable=True)
    page = Column(Integer, default=0)
    title = Column(String, nullable=True)
    category = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    scope = Column(String, nullable=True)
    scraping_date = Column(String)



    #Permette di fare chunks.document per risalire al file originale
    document = relationship("Document", back_populates="chunks")

class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text)
    answer = Column(Text)