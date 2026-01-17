"""
Authentication Module

This module handles user authentication - determining WHO the user is.
It extracts and validates JWT tokens from cookies or headers.
"""

from fastapi import Depends, HTTPException, status, Request
from sqlmodel import Session, select
from typing import Optional

from ..db.session import get_session
from ..models.user import User
from .auth_utils import decode_access_token
from fastapi.security import OAuth2PasswordBearer

# Cookie name for httpOnly auth cookie
COOKIE_NAME = "access_token"

# Initialize OAuth2PasswordBearer (still used for Swagger docs, but optional in actual auth)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


def get_token_from_cookie_or_header(
    request: Request,
    token_from_header: Optional[str] = Depends(oauth2_scheme)
) -> str:
    """
    Extract JWT token from httpOnly cookie OR Authorization header.
    Priority: Cookie first (for SSR requests from SvelteKit), then header (for API clients).
    """
    # Try to get token from httpOnly cookie first
    token_from_cookie = request.cookies.get(COOKIE_NAME)
    
    if token_from_cookie:
        return token_from_cookie
    
    if token_from_header:
        return token_from_header
    
    # No token found in either location
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    token: str = Depends(get_token_from_cookie_or_header),
    session: Session = Depends(get_session)
) -> User:
    """
    Dependency function to get the current authenticated user from a JWT token.
    Accepts token from httpOnly cookie or Authorization header.
    """
    payload = decode_access_token(token)  # Decodes and validates the token
    username: str = payload.get("sub")  # Get the 'sub' (subject) claim, which is our username

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
