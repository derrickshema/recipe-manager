# Lifespan event for database initialization
from fastapi import FastAPI
from sqlmodel import SQLModel
from .db.database import engine
from .routes import recipe_routes, restaurant_routes, auth_routes, admin_routes, upload_routes
from fastapi.middleware.cors import CORSMiddleware

async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

# Create FastAPI app instance with lifespan event
app = FastAPI(lifespan=lifespan)

# Set up CORS middleware for cross-origin requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers for different functionalities
app.include_router(auth_routes.router)
app.include_router(restaurant_routes.router)
app.include_router(recipe_routes.router)
app.include_router(admin_routes.router)
app.include_router(upload_routes.router)
