from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
from fastapi import HTTPException, status

# Import centralized settings
from ..config import settings

# ---Password Hashing---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"])

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

# ---Token Generation---
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire  = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> dict:
    """Verify a JWT token and return the payload."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.JWTError:
         # This catches various JWT errors like invalid signature, expired token, etc.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}, # Standard header for OAuth2
        )


# ---Password Reset Tokens---
RESET_TOKEN_EXPIRE_MINUTES = 60  # 1 hour

def create_password_reset_token(email: str) -> str:
    """
    Create a JWT token for password reset.
    
    Uses a different 'purpose' claim to distinguish it from access tokens.
    This prevents someone from using a reset token as an auth token.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": email,
        "purpose": "password_reset",  # Important: distinguishes from access tokens
        "exp": expire
    }
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_password_reset_token(token: str) -> str | None:
    """
    Verify a password reset token and return the email.
    
    Returns:
        The email address if token is valid, None otherwise.
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Verify this is actually a password reset token
        if payload.get("purpose") != "password_reset":
            return None
        
        email: str = payload.get("sub")
        return email
        
    except jwt.JWTError:
        return None


# ---Email Verification Tokens---
VERIFICATION_TOKEN_EXPIRE_HOURS = 24  # 24 hours

def create_email_verification_token(email: str) -> str:
    """
    Create a JWT token for email verification.
    
    Uses a 'purpose' claim to distinguish from other token types.
    """
    expire = datetime.now(timezone.utc) + timedelta(hours=VERIFICATION_TOKEN_EXPIRE_HOURS)
    
    to_encode = {
        "sub": email,
        "purpose": "email_verification",
        "exp": expire
    }
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_email_verification_token(token: str) -> str | None:
    """
    Verify an email verification token and return the email.
    
    Returns:
        The email address if token is valid, None otherwise.
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Verify this is actually an email verification token
        if payload.get("purpose") != "email_verification":
            return None
        
        email: str = payload.get("sub")
        return email
        
    except jwt.JWTError:
        return None


# ---Staff Invitation Tokens---
INVITATION_TOKEN_EXPIRE_DAYS = 7  # 7 days

def create_staff_invitation_token(email: str, restaurant_id: int, role: str) -> str:
    """
    Create a JWT token for staff invitation.
    
    The token encodes the email, restaurant_id, and role so that
    when the user registers or accepts, we know which restaurant to add them to.
    """
    expire = datetime.now(timezone.utc) + timedelta(days=INVITATION_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        "sub": email,
        "restaurant_id": restaurant_id,
        "role": role,
        "purpose": "staff_invitation",
        "exp": expire
    }
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_staff_invitation_token(token: str) -> dict | None:
    """
    Verify a staff invitation token and return the payload.
    
    Returns:
        A dict with email, restaurant_id, and role if valid, None otherwise.
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Verify this is actually a staff invitation token
        if payload.get("purpose") != "staff_invitation":
            return None
        
        return {
            "email": payload.get("sub"),
            "restaurant_id": payload.get("restaurant_id"),
            "role": payload.get("role")
        }
        
    except jwt.JWTError:
        return None