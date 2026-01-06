"""
Script to create the initial superadmin user.
Run this once during initial setup:

1. Create a .env file in the backend directory with:
   SUPERADMIN_USERNAME=your_admin
   SUPERADMIN_PASSWORD=your_secure_password
   SUPERADMIN_EMAIL=admin@yourcompany.com

2. Run: python create_superadmin.py
"""
import os
import sys
from dotenv import load_dotenv
from sqlmodel import Session, select
from app.db.session import engine

# Import all models to ensure relationships are properly configured
from app.models.user import User, SystemRole
from app.models.restaurant import Restaurant
from app.models.membership import Membership
from app.models.recipe import Recipe
from app.utilities.auth_utils import hash_password

def create_superadmin():
    """Create the first superadmin user if none exists."""
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get credentials from environment variables (REQUIRED)
    admin_username = os.getenv("SUPERADMIN_USERNAME")
    admin_password = os.getenv("SUPERADMIN_PASSWORD")
    admin_email = os.getenv("SUPERADMIN_EMAIL")
    
    # Validate that all required environment variables are set
    missing_vars = []
    if not admin_username:
        missing_vars.append("SUPERADMIN_USERNAME")
    if not admin_password:
        missing_vars.append("SUPERADMIN_PASSWORD")
    if not admin_email:
        missing_vars.append("SUPERADMIN_EMAIL")
    
    if missing_vars:
        print("❌ Error: Missing required environment variables in .env file:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create a .env file in the backend directory with:")
        print("   SUPERADMIN_USERNAME=your_admin")
        print("   SUPERADMIN_PASSWORD=your_secure_password")
        print("   SUPERADMIN_EMAIL=admin@yourcompany.com")
        sys.exit(1)
    
    # Validate password strength
    if len(admin_password) < 8:
        print("❌ Error: Password must be at least 8 characters long")
        sys.exit(1)
    
    with Session(engine) as session:
        # Check if superadmin already exists
        existing_admin = session.exec(
            select(User).where(User.role == SystemRole.SUPERADMIN)
        ).first()
        
        if existing_admin:
            print(f"⚠️  Superadmin already exists: {existing_admin.username}")
            print(f"   Email: {existing_admin.email}")
            print(f"   ID: {existing_admin.id}")
            return
        
        # Create new superadmin
        superadmin = User(
            username=admin_username,
            email=admin_email,
            first_name="System",
            last_name="Administrator",
            hashed_password=hash_password(admin_password),
            role=SystemRole.SUPERADMIN
        )
        
        session.add(superadmin)
        session.commit()
        session.refresh(superadmin)
        
        print("✅ Superadmin created successfully!")
        print(f"   Username: {superadmin.username}")
        print(f"   Email: {superadmin.email}")
        print(f"   ID: {superadmin.id}")
        print(f"\n🔒 Keep your .env file secure and never commit it to git!")

if __name__ == "__main__":
    create_superadmin()
