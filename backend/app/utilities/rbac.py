"""
Role-Based Access Control (RBAC) Module

This module handles authorization - determining WHAT the user can do.
It provides role-checking dependencies for FastAPI routes.

Two layers of roles:
- SystemRole: App-wide roles (superadmin, customer, restaurant_owner)
- OrgRole: Restaurant-specific roles (admin, employee)
"""

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from ..db.session import get_session
from ..models.membership import Membership, OrgRole
from ..models.user import SystemRole, User
from .auth import get_current_user


def require_system_roles(*roles: SystemRole):
    """
    Requires the user to have one of the specified system-wide roles.
    """
    def dependency(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return current_user
    return dependency


async def require_superadmin(current_user: User = Depends(get_current_user)):
    """Ensure the current user is a superadmin."""
    if current_user.role != SystemRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires superadmin privileges"
        )
    return current_user


def require_org_roles(*roles: OrgRole):
    """
    Requires the user to have one of the specified roles within a restaurant.
    """
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


# ============================================
# Access Control Shortcuts
# ============================================

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
