# auth_routes.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
import os

from ..utilities.auth import get_current_user
from ..db.session import get_session
from ..models.user import User, UserCreate, UserRead, Token, SystemRole, UserLogin
from ..models.membership import Membership, OrgRole
from ..models.restaurant import Restaurant, RestaurantOwnerRegistration
from ..utilities.auth_utils import verify_password, hash_password, create_access_token

# Cookie configuration
COOKIE_NAME = "access_token"
COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 7 days in seconds
COOKIE_SECURE = os.getenv("ENVIRONMENT", "development") == "production"  # True in production
COOKIE_SAMESITE = "lax"  # "strict" blocks cross-site, "lax" allows top-level navigation
COOKIE_HTTPONLY = True  # Prevents JavaScript access
COOKIE_PATH = "/"

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
    
    # Set default system role if not provided (default to CUSTOMER for public registration)
    system_role = user_in.role if user_in.role else SystemRole.CUSTOMER
    
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

# --- Restaurant Owner Registration Endpoint ---
@router.post("/register/restaurant-owner", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_restaurant_owner(
    registration_data: RestaurantOwnerRegistration,
    session: Session = Depends(get_session)
):
    """
    Registers a new restaurant owner with restaurant details.
    Creates: User (owner) + Restaurant + Membership (owner as restaurant_admin)
    """
    # Check if username already exists
    existing_user = session.exec(select(User).where(User.username == registration_data.username)).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    # Check if email already exists
    existing_email_user = session.exec(select(User).where(User.email == registration_data.email)).first()
    if existing_email_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Hash the password
    hashed_password = hash_password(registration_data.password)
    
    # Create the owner user account with USER system role
    db_user = User(
        username=registration_data.username,
        hashed_password=hashed_password,
        email=registration_data.email,
        first_name=registration_data.first_name,
        last_name=registration_data.last_name,
        role=SystemRole.RESTAURANT_OWNER  # Restaurant owners get RESTAURANT_OWNER role
    )
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    # Create the restaurant
    db_restaurant = Restaurant(
        restaurant_name=registration_data.restaurant_name
    )
    
    session.add(db_restaurant)
    session.commit()
    session.refresh(db_restaurant)
    
    # Create membership linking owner to restaurant with RESTAURANT_ADMIN role
    membership = Membership(
        user_id=db_user.id,
        restaurant_id=db_restaurant.id,
        role=OrgRole.RESTAURANT_ADMIN
    )
    
    session.add(membership)
    session.commit()
    
    return db_user

# --- Login Endpoint ---
@router.post("/token")
async def login_for_access_token(
    response: Response,
    credentials: UserLogin,
    session: Session = Depends(get_session)
):
    """
    Authenticates a user and sets an httpOnly cookie with the JWT.
    Returns user profile (token is in cookie, not response body).
    Accepts JSON: {"username": "...", "password": "..."}
    """
    username = credentials.username
    password = credentials.password
    
    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create the access token
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")))
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    # Set httpOnly cookie instead of returning token in body
    response.set_cookie(
        key=COOKIE_NAME,
        value=access_token,
        max_age=COOKIE_MAX_AGE,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path=COOKIE_PATH,
    )
    
    # Return user profile (frontend needs user data, not the token)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "message": "Login successful"
    }


# --- Logout Endpoint ---
@router.post("/logout")
async def logout(response: Response):
    """
    Logs out user by clearing the httpOnly cookie.
    """
    response.delete_cookie(
        key=COOKIE_NAME,
        path=COOKIE_PATH,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
    )
    return {"message": "Logged out successfully"}


# --- Protected Endpoint Example (for testing auth) ---
@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Retrieves the current authenticated user's information.
    Requires a valid JWT in the Authorization header or cookie.
    """
    return current_user