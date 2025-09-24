from sqlmodel import Session
from .database import engine

# generator function to create a new session
def get_session():
    # Create a new session with the database engine
    with Session(engine) as session:
        # Yield the session for use in route handlers
        # This allows for dependency injection in FastAPI
        # code after the yield will run after the request is processed
        yield session