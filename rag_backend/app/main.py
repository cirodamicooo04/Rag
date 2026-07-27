from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.admin_endpoints import router
from app.api.user_endpoints import user_router
from app.core.config import UPLOAD_DIR, INITIALIZE_GUARDRAILS_DB
from app.db.database import engine
from app.db import models

import app.core.ml_models
from app.services import populate_guardrails

#Creo tabelle se non esistono
models.Base.metadata.create_all(bind=engine)

#Creo la cartella docs per i file caricati
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="RAG")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"status": "online", "version": "v1"}
