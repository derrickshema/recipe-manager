"""
Database Configuration Module

This module sets up the SQLModel/SQLAlchemy database engine.
The engine is the core interface to the database - it manages
the connection pool and executes all database operations.
"""

from sqlmodel import create_engine

# Import centralized settings
# This validates DATABASE_URL exists at startup (not at 3am when something breaks!)
from ..config import settings

# Create the SQLAlchemy engine - this is the starting point for all DB operations
# - echo: Logs all SQL statements (DEBUG mode = helpful, production = too noisy)
# - The engine manages a pool of database connections for efficiency
engine = create_engine(
    settings.DATABASE_URL, 
    echo=settings.DEBUG  # Only log SQL in debug mode
)
