from fastapi import FastAPI

from app.api.endpoints import router
from app.db.database import engine
from app.db import models

import app.core.ml_models

#Creo tabelle se non esistono
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="RAG")

app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"status": "online", "version": "v1"}