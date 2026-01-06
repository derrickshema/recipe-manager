"""
Update superadmin password.
Use this if you forgot the password or need to change it.

Usage: python update_superadmin_password.py
"""
import os
import sys
from dotenv import load_dotenv
from sqlmodel import Session, select
from app.db.session import engine

# Import all models
from app.models.user import User, SystemRole
from app.models.restaurant import Restaurant
from app.models.membership import Membership
from app.models.recipe import Recipe
from app.utilities.auth_utils import hash_password

def update_superadmin_password():
    """Update the superadmin password from .env file."""
    
    # Load environment variables
    load_dotenv()
    
    new_password = os.getenv("SUPERADMIN_PASSWORD")
    
    if not new_password:
        print("❌ Error: SUPERADMIN_PASSWORD not found in .env file")
        sys.exit(1)
    
    with Session(engine) as session:
        # Find superadmin
        superadmin = session.exec(
            select(User).where(User.role == SystemRole.SUPERADMIN)
        ).first()
        
        if not superadmin:
            print("❌ No superadmin found in database!")
            print("   Run: python create_superadmin.py")
            sys.exit(1)
        
        # Update password
        superadmin.hashed_password = hash_password(new_password)
        session.add(superadmin)
        session.commit()
        
        print("✅ Superadmin password updated successfully!")
        print(f"   Username: {superadmin.username}")
        print(f"   Email: {superadmin.email}")
        print(f"\n   You can now log in with the password from your .env file")

if __name__ == "__main__":
    update_superadmin_password()
