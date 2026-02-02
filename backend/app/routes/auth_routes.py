# auth_routes.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select
import os

from ..utilities.auth import get_current_user
from ..db.session import get_session
from ..models.user import User, UserCreate, UserRead, SystemRole, UserLogin
from ..models.membership import Membership, OrgRole
from ..models.restaurant import Restaurant, RestaurantOwnerRegistration
from pydantic import BaseModel, EmailStr
from ..utilities.auth_utils import verify_password, hash_password, create_access_token, create_password_reset_token, verify_password_reset_token, create_email_verification_token, verify_email_verification_token
from ..utilities.email import send_password_reset_email, send_verification_email

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
    Sends a verification email to confirm the user's email address.
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
        email_verified=False,  # New users start with unverified email
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

    # Send verification email
    if db_user.email:
        verification_token = create_email_verification_token(db_user.email)
        email_sent = send_verification_email(db_user.email, verification_token, db_user.first_name)
        if email_sent:
            print(f"Verification email sent to {db_user.email}")
        else:
            print(f"WARNING: Failed to send verification email to {db_user.email}")
    else:
        print(f"WARNING: User {db_user.username} has no email, skipping verification email")

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
    
    # Create the owner user account with RESTAURANT_OWNER system role
    db_user = User(
        username=registration_data.username,
        hashed_password=hashed_password,
        email=registration_data.email,
        first_name=registration_data.first_name,
        last_name=registration_data.last_name,
        role=SystemRole.RESTAURANT_OWNER,  # Restaurant owners get RESTAURANT_OWNER role
        email_verified=False,  # New users start with unverified email
    )
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    # Create the restaurant
    db_restaurant = Restaurant(
        restaurant_name=registration_data.restaurant_name,
        cuisine_type=registration_data.cuisine_type,
        address=registration_data.address,
        phone=registration_data.restaurant_phone
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
    
    # Send verification email
    if db_user.email:
        verification_token = create_email_verification_token(db_user.email)
        email_sent = send_verification_email(db_user.email, verification_token, db_user.first_name)
        if email_sent:
            print(f"Verification email sent to {db_user.email}")
        else:
            print(f"WARNING: Failed to send verification email to {db_user.email}")
    else:
        print(f"WARNING: User {db_user.username} has no email, skipping verification email")
    
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

    # DEVELOPMENT MODE: Email verification check disabled for testing
    # In production, uncomment this block to require email verification
    # if not user.email_verified and user.role != SystemRole.SUPERADMIN:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Please verify your email before logging in. Check your inbox for the verification link.",
    #     )

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


# --- Password Reset Request/Response Models ---
class ForgotPasswordRequest(BaseModel):
    """Request body for forgot password endpoint."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Request body for reset password endpoint."""
    token: str
    new_password: str


# --- Forgot Password Endpoint ---
@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    session: Session = Depends(get_session)
):
    """
    Initiates the password reset process.
    
    Sends a password reset email if the email exists in the system.
    For security, always returns success even if email doesn't exist
    (prevents email enumeration attacks).
    """
    # Find user by email
    user = session.exec(select(User).where(User.email == request.email)).first()
    
    if user:
        # Generate password reset token
        reset_token = create_password_reset_token(user.email)
        
        # Send the reset email
        email_sent = send_password_reset_email(user.email, reset_token)
        
        if not email_sent:
            # Log the error but don't expose it to user
            print(f"Failed to send password reset email to {user.email}")
    
    # Always return success to prevent email enumeration
    # An attacker shouldn't be able to determine if an email exists
    return {
        "message": "If an account with that email exists, a password reset link has been sent."
    }


# --- Reset Password Endpoint ---
@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    session: Session = Depends(get_session)
):
    """
    Resets the user's password using a valid reset token.
    
    The token must be:
    1. Valid (not tampered with)
    2. Not expired (1 hour limit)
    3. Have the correct purpose claim
    """
    # Verify the token
    email = verify_password_reset_token(request.token)
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token. Please request a new password reset."
        )
    
    # Find the user
    user = session.exec(select(User).where(User.email == email)).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token. Please request a new password reset."
        )
    
    # Validate new password (basic validation - you can make this stricter)
    if len(request.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long."
        )
    
    # Update the password
    user.hashed_password = hash_password(request.new_password)
    session.add(user)
    session.commit()
    
    return {
        "message": "Password has been reset successfully. You can now log in with your new password."
    }


# --- Email Verification Request/Response Models ---
class VerifyEmailRequest(BaseModel):
    """Request body for email verification endpoint."""
    token: str


class ResendVerificationRequest(BaseModel):
    """Request body for resending verification email."""
    email: EmailStr


# --- Verify Email Endpoint ---
@router.post("/verify-email")
async def verify_email(
    request: VerifyEmailRequest,
    session: Session = Depends(get_session)
):
    """
    Verifies a user's email address using the verification token.
    
    The token must be:
    1. Valid (not tampered with)
    2. Not expired (24 hour limit)
    3. Have the correct purpose claim
    """
    # Verify the token
    email = verify_email_verification_token(request.token)
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification link. Please request a new verification email."
        )
    
    # Find the user
    user = session.exec(select(User).where(User.email == email)).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification link. Please request a new verification email."
        )
    
    # Check if already verified
    if user.email_verified:
        return {
            "message": "Email is already verified. You can log in to your account."
        }
    
    # Mark email as verified
    user.email_verified = True
    session.add(user)
    session.commit()
    
    return {
        "message": "Email verified successfully! You can now log in to your account."
    }


# --- Resend Verification Email Endpoint ---
@router.post("/resend-verification")
async def resend_verification_email(
    request: ResendVerificationRequest,
    session: Session = Depends(get_session)
):
    """
    Resends the verification email to a user who hasn't verified yet.
    
    For security, always returns success even if email doesn't exist
    (prevents email enumeration attacks).
    """
    # Find user by email
    user = session.exec(select(User).where(User.email == request.email)).first()
    
    if user and not user.email_verified:
        # Generate new verification token
        verification_token = create_email_verification_token(user.email)
        
        # Send the verification email
        email_sent = send_verification_email(user.email, verification_token, user.first_name)
        
        if not email_sent:
            print(f"Failed to send verification email to {user.email}")
    
    # Always return success to prevent email enumeration
    return {
        "message": "If an account with that email exists and is not yet verified, a verification link has been sent."
    }