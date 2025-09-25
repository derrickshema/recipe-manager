# auth_routes.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
import os
from ..db.session import get_session
from ..models.user import User, UserCreate, UserLogin, UserRead, Token # Import new models
from ..utilities.auth_utils import verify_password, hash_password, create_access_token, decode_access_token

# Initialize OAuth2PasswordBearer
# tokenUrl specifies the endpoint where clients can obtain a token (login)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

router = APIRouter(prefix="/auth", tags=["Authentication"])

# --- Dependency to get the current authenticated user ---
async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    """
    Dependency function to get the current authenticated user from a JWT token.
    This function will be used in protected routes.
    """
    payload = decode_access_token(token) # Decodes and validates the token
    username: str = payload.get("sub") # Get the 'sub' (subject) claim, which is our username

    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch the user from the database
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found in database",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# --- User Registration Endpoint ---
@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, session: Session = Depends(get_session)):
    """
    Registers a new user.
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
    db_user = User(
    username=user_in.username,
    hashed_password=hashed_password,
    email=user_in.email,
    first_name=user_in.first_name,
    last_name=user_in.last_name,
    role=user_in.role,
    restaurant_id=user_in.restaurant_id,
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

# --- Login Endpoint ---
@router.post("/token", response_model=Token)
async def login_for_access_token(
    login: UserLogin,
    session: Session = Depends(get_session)
):
    """
    Authenticates a user and returns a JWT access token.
    """
    user = session.exec(select(User).where(User.username == login.username)).first()
    if not user or not verify_password(login.password, user.hashed_password):
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