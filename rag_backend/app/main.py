from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.endpoints import router
from app.core.config import UPLOAD_DIR, INITIALIZE_GUARDRAILS_DB
from app.db.database import engine
from app.db import models

import app.core.ml_models
from app.services import populate_guardrails

#Creo tabelle se non esistono
models.Base.metadata.create_all(bind=engine)

#Creo la cartella docs per i file caricati
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    if INITIALIZE_GUARDRAILS_DB:
        populate_guardrails.run_indexing()

    yield

app = FastAPI(title="RAG", lifespan=lifespan)

app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"status": "online", "version": "v1"}
