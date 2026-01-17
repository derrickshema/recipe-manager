"""
Database Configuration Module

This module sets up the SQLModel/SQLAlchemy database engine.
The engine is the core interface to the database - it manages
the connection pool and executes all database operations.
"""

import os
from sqlmodel import create_engine
from dotenv import load_dotenv

# Load environment variables from .env file into os.environ
# This allows us to keep sensitive config (like DB credentials) out of code
load_dotenv()

# Get the database connection string from environment
# Format: postgresql://username:password@host:port/database_name
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the SQLAlchemy engine - this is the starting point for all DB operations
# - echo=True: Logs all SQL statements to console (helpful for debugging, disable in production)
# - The engine manages a pool of database connections for efficiency
engine = create_engine(DATABASE_URL, echo=True)
