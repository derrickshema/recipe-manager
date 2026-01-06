"""
Admin routes for system administrators.
Superadmins can manage users and approve restaurants.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, or_
from typing import List

from ..db.session import get_session
from ..models.user import User, SystemRole, UserRead
from ..models.restaurant import Restaurant, RestaurantRead, ApprovalStatus
from ..utilities.users_utils import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])


# --- Dependency: Require Superadmin Role ---
async def require_superadmin(current_user: User = Depends(get_current_user)):
    """Ensure the current user is a superadmin."""
    if current_user.role != SystemRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires superadmin privileges"
        )
    return current_user


# --- User Management ---
@router.get("/users", response_model=List[UserRead])
async def list_all_users(
    role: SystemRole | None = Query(None, description="Filter by role"),
    current_user: User = Depends(require_superadmin),
    session: Session = Depends(get_session)
):
    """List all users in the system. Superadmin only."""
    query = select(User)
    
    if role:
        query = query.where(User.role == role)
    
    users = session.exec(query).all()
    return users


@router.get("/users/{user_id}", response_model=UserRead)
async def get_user_details(
    user_id: int,
    current_user: User = Depends(require_superadmin),
    session: Session = Depends(get_session)
):
    """Get detailed information about a specific user. Superadmin only."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/users/{user_id}/suspend")
async def suspend_user(
    user_id: int,
    current_user: User = Depends(require_superadmin),
    session: Session = Depends(get_session)
):
    """Suspend a user account. Superadmin only."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role == SystemRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot suspend another superadmin"
        )
    
    user.role = SystemRole.SUSPENDED
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {"message": f"User {user.username} has been suspended", "user": user}


@router.patch("/users/{user_id}/unsuspend")
async def unsuspend_user(
    user_id: int,
    restore_role: SystemRole,
    current_user: User = Depends(require_superadmin),
    session: Session = Depends(get_session)
):
    """Unsuspend a user account and restore their role. Superadmin only."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role != SystemRole.SUSPENDED:
        raise HTTPException(status_code=400, detail="User is not suspended")
    
    if restore_role == SystemRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot promote users to superadmin via this endpoint"
        )
    
    user.role = restore_role
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {"message": f"User {user.username} has been unsuspended", "user": user}


# --- Restaurant Management ---
@router.get("/restaurants", response_model=List[RestaurantRead])
async def list_all_restaurants(
    approval_status: ApprovalStatus | None = Query(None, description="Filter by approval status"),
    current_user: User = Depends(require_superadmin),
    session: Session = Depends(get_session)
):
    """List all restaurants. Superadmin only."""
    query = select(Restaurant)
    
    if approval_status:
        query = query.where(Restaurant.approval_status == approval_status)
    
    restaurants = session.exec(query).all()
    return restaurants


@router.get("/restaurants/pending", response_model=List[RestaurantRead])
async def list_pending_restaurants(
    current_user: User = Depends(require_superadmin),
    session: Session = Depends(get_session)
):
    """List all restaurants pending approval. Superadmin only."""
    restaurants = session.exec(
        select(Restaurant).where(Restaurant.approval_status == ApprovalStatus.PENDING)
    ).all()
    return restaurants


@router.patch("/restaurants/{restaurant_id}/approve")
async def approve_restaurant(
    restaurant_id: int,
    current_user: User = Depends(require_superadmin),
    session: Session = Depends(get_session)
):
    """Approve a restaurant registration. Superadmin only."""
    restaurant = session.get(Restaurant, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    if restaurant.approval_status != ApprovalStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Restaurant is already {restaurant.approval_status}"
        )
    
    restaurant.approval_status = ApprovalStatus.APPROVED
    session.add(restaurant)
    session.commit()
    session.refresh(restaurant)
    
    return {
        "message": f"Restaurant '{restaurant.restaurant_name}' has been approved",
        "restaurant": restaurant
    }


@router.patch("/restaurants/{restaurant_id}/reject")
async def reject_restaurant(
    restaurant_id: int,
    reason: str | None = None,
    current_user: User = Depends(require_superadmin),
    session: Session = Depends(get_session)
):
    """Reject a restaurant registration. Superadmin only."""
    restaurant = session.get(Restaurant, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    if restaurant.approval_status != ApprovalStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Restaurant is already {restaurant.approval_status}"
        )
    
    restaurant.approval_status = ApprovalStatus.REJECTED
    session.add(restaurant)
    session.commit()
    session.refresh(restaurant)
    
    return {
        "message": f"Restaurant '{restaurant.restaurant_name}' has been rejected",
        "reason": reason,
        "restaurant": restaurant
    }


@router.patch("/restaurants/{restaurant_id}/suspend")
async def suspend_restaurant(
    restaurant_id: int,
    current_user: User = Depends(require_superadmin),
    session: Session = Depends(get_session)
):
    """Suspend a restaurant. Superadmin only."""
    restaurant = session.get(Restaurant, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    restaurant.approval_status = ApprovalStatus.SUSPENDED
    session.add(restaurant)
    session.commit()
    session.refresh(restaurant)
    
    return {
        "message": f"Restaurant '{restaurant.restaurant_name}' has been suspended",
        "restaurant": restaurant
    }


# --- Dashboard Stats ---
@router.get("/stats")
async def get_admin_dashboard_stats(
    current_user: User = Depends(require_superadmin),
    session: Session = Depends(get_session)
):
    """Get statistics for admin dashboard. Superadmin only."""
    
    # Count users by role
    total_customers = len(session.exec(
        select(User).where(User.role == SystemRole.CUSTOMER)
    ).all())
    
    total_owners = len(session.exec(
        select(User).where(User.role == SystemRole.RESTAURANT_OWNER)
    ).all())
    
    suspended_users = len(session.exec(
        select(User).where(User.role == SystemRole.SUSPENDED)
    ).all())
    
    # Count restaurants by status
    pending_restaurants = len(session.exec(
        select(Restaurant).where(Restaurant.approval_status == ApprovalStatus.PENDING)
    ).all())
    
    approved_restaurants = len(session.exec(
        select(Restaurant).where(Restaurant.approval_status == ApprovalStatus.APPROVED)
    ).all())
    
    suspended_restaurants = len(session.exec(
        select(Restaurant).where(Restaurant.approval_status == ApprovalStatus.SUSPENDED)
    ).all())
    
    return {
        "users": {
            "customers": total_customers,
            "restaurant_owners": total_owners,
            "suspended": suspended_users,
            "total": total_customers + total_owners
        },
        "restaurants": {
            "pending": pending_restaurants,
            "approved": approved_restaurants,
            "suspended": suspended_restaurants,
            "total": pending_restaurants + approved_restaurants + suspended_restaurants
        }
    }
