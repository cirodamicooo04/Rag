from fastapi import FastAPI

from app.db.database import engine
from app.db import models

#Creo tabelle se non esistono
models.Base.metadata.create_all(bind=engine)