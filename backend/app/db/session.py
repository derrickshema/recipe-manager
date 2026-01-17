"""
Database Session Management Module

This module provides the session dependency for FastAPI routes.
A session is like a "workspace" for database operations - it tracks
changes, handles transactions, and ensures data consistency.

Architecture:
    FastAPI Route
         │
         ▼
    get_session() ──► Creates Session ──► Executes queries ──► Auto-closes
         │
         └── Injected via: Depends(get_session)
"""

from sqlmodel import Session
from .database import engine


def get_session():
    """
    Dependency function that provides a database session to FastAPI routes.
    
    This is a generator function (uses 'yield' instead of 'return'):
    1. BEFORE yield: Creates a new session
    2. YIELD: Hands session to the route handler
    3. AFTER yield: Automatically closes session (even if errors occur)
    
    Usage in routes:
        @router.get("/items")
        def get_items(session: Session = Depends(get_session)):
            return session.exec(select(Item)).all()
    
    The 'with' statement ensures the session is properly closed,
    and any uncommitted changes are rolled back if an error occurs.
    """
    with Session(engine) as session:
        yield session
