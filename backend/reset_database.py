"""
Reset database - Drop all tables and recreate them.
WARNING: This will delete ALL data! Only use in development.

Usage: python reset_database.py
"""
import sys
import os
from sqlmodel import SQLModel
from app.db.session import engine

# Import all models to ensure tables are created
from app.models.user import User
from app.models.restaurant import Restaurant
from app.models.membership import Membership
from app.models.recipe import Recipe

def reset_database():
    """Drop all tables and recreate them."""
    
    # Production safety check
    environment = os.getenv("ENVIRONMENT", "development")
    if environment.lower() in ["production", "prod"]:
        print("❌ ERROR: Cannot reset database in PRODUCTION environment!")
        print("   Set ENVIRONMENT=development to use this script.")
        sys.exit(1)
    
    # Confirm action
    print("⚠️  WARNING: This will DELETE ALL DATA in the database!")
    print(f"   Current environment: {environment}")
    print("   This action cannot be undone.")
    response = input("\nAre you sure you want to continue? Type 'yes' to confirm: ")
    
    if response.lower() != 'yes':
        print("❌ Database reset cancelled.")
        sys.exit(0)
    
    print("\n🗑️  Dropping all tables...")
    SQLModel.metadata.drop_all(engine)
    print("✅ All tables dropped.")
    
    print("\n📦 Creating fresh tables...")
    SQLModel.metadata.create_all(engine)
    print("✅ All tables created.")
    
    print("\n✨ Database reset complete!")
    print("   You can now run: python create_superadmin.py")

if __name__ == "__main__":
    reset_database()
