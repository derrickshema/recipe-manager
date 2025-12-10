# auth_routes.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
import os

from ..utilities.users_utils import get_current_user
from ..db.session import get_session
from ..models.user import User, UserCreate, UserRead, Token, SystemRole
from ..models.membership import Membership, OrgRole
from ..utilities.auth_utils import verify_password, hash_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

# --- User Registration Endpoint ---
@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, session: Session = Depends(get_session)):
    """
    Registers a new user with both system role and optional organization role.
    """
    # Check if username already exists
    existing_user = session.exec(select(User).where(User.username == user_in.username)).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    # Check if email already exists (if provided)
    if user_in.email:
        existing_email_user = session.exec(select(User).where(User.email == user_in.email)).first()
        if existing_email_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Hash the password before storing
    hashed_password = hash_password(user_in.password)
    
    # Set default system role if not provided
    system_role = user_in.role if user_in.role else SystemRole.USER
    
    db_user = User(
        username=user_in.username,
        hashed_password=hashed_password,
        email=user_in.email,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        role=system_role,
        # Remove restaurant_id from User model as it will be handled through Membership
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    # If organization role and restaurant_id are provided, create a membership
    if user_in.org_role and user_in.restaurant_id:
        membership = Membership(
            user_id=db_user.id,
            restaurant_id=user_in.restaurant_id,
            role=user_in.org_role
        )
        session.add(membership)
        session.commit()

    return db_user

# --- Login Endpoint ---
@router.post("/token", response_model=Token)
async def login_for_access_token(
    credentials: dict,
    session: Session = Depends(get_session)
):
    """
    Authenticates a user and returns a JWT access token.
    Accepts JSON: {"username": "...", "password": "..."}
    """
    username = credentials.get("username")
    password = credentials.get("password")
    
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required"
        )
    
    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}, # Standard header for OAuth2
        )

    # Create the access token
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))) # Default to 30 minutes if not set
    access_token = create_access_token(
        data={"sub": user.username}, # 'sub' claim identifies the user
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Protected Endpoint Example (for testing auth) ---
@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Retrieves the current authenticated user's information.
    Requires a valid JWT in the Authorization header.
    """
    return current_user