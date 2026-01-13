from fastapi import Depends, HTTPException, status, Request
from sqlmodel import Session, select
from typing import Optional

from ..db.session import get_session

from ..models.membership import Membership, OrgRole

from ..models.user import SystemRole, User
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


# --- Dependency to get the current authenticated user ---
async def get_current_user(
    token: str = Depends(get_token_from_cookie_or_header),
    session: Session = Depends(get_session)
) -> User:
    """
    Dependency function to get the current authenticated user from a JWT token.
    Accepts token from httpOnly cookie or Authorization header.
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

def require_system_roles(*roles: SystemRole):
    def dependency(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return current_user
    return dependency


def require_org_roles(*roles: OrgRole):
    def dependency(
        restaurant_id: int,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
    ):
        membership = session.exec(
            select(Membership).where(
                Membership.user_id == current_user.id,
                Membership.restaurant_id == restaurant_id
            )
        ).first()
        if not membership or membership.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        return current_user
    return dependency

def require_org_or_system_roles(*, system_roles: list[SystemRole] = None, org_roles: list[OrgRole] = None):
    """
    Allows access if user has a matching system role OR a matching org role for a given restaurant.
    """
    system_roles = system_roles or []
    org_roles = org_roles or []

    def dependency(
        restaurant_id: int,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session),
    ):
        # System-level access always overrides
        if current_user.role in system_roles:
            return current_user

        # Check org membership (restaurant-level)
        membership = session.exec(
            select(Membership).where(
                Membership.user_id == current_user.id,
                Membership.restaurant_id == restaurant_id,
            )
        ).first()

        if not membership or membership.role not in org_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to perform this action.",
            )

        return current_user

    return dependency

# Access control shortcuts

def require_restaurant_creation_access():
    """
    Only system superadmins can create restaurants.
    """
    return require_system_roles(SystemRole.SUPERADMIN)

def require_manage_restaurant_access():
    """
    Can create, update, or delete a restaurant.
    """
    return require_org_or_system_roles(
        system_roles=[SystemRole.SUPERADMIN],
        org_roles=[OrgRole.RESTAURANT_ADMIN],
    )


def require_edit_menu_access():
    """
    Can edit menu items, prices, etc.
    """
    return require_org_or_system_roles(
        system_roles=[SystemRole.SUPERADMIN],
        org_roles=[OrgRole.RESTAURANT_ADMIN, OrgRole.EMPLOYEE],
    )


def require_read_restaurant_access():
    """
    Can view restaurant details (read-only).
    """
    return require_org_or_system_roles(
        system_roles=[SystemRole.SUPERADMIN],
        org_roles=[OrgRole.RESTAURANT_ADMIN, OrgRole.EMPLOYEE],
    )
