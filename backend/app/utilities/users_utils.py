from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from ..db.session import get_session

from ..models.membership import Membership, OrgRole

from ..models.user import SystemRole, User
from .auth_utils import decode_access_token
from fastapi.security import OAuth2PasswordBearer

# Initialize OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


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

def require_system_roles(*roles: SystemRole):
    def dependency(current_user: User = Depends(get_current_user)):
        if current_user.system_role not in roles:
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