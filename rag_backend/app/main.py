from fastapi import FastAPI

from app.api.endpoints import router
from app.core.config import UPLOAD_DIR
from app.db.database import engine
from app.db import models

import app.core.ml_models

#Creo tabelle se non esistono
models.Base.metadata.create_all(bind=engine)

#Creo la cartella docs per i file caricati
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="RAG")

app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"status": "online", "version": "v1"}