# Lifespan event for database initialization
from fastapi import FastAPI
from sqlmodel import SQLModel
from .db.database import engine
from app.models import user, restaurant, recipe  # Import all models

async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

# Create FastAPI app instance with lifespan event
app = FastAPI(lifespan=lifespan)