from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..utilities.users_utils import require_manage_restaurant_access, require_read_restaurant_access, require_restaurant_creation_access, require_system_roles

from ..db.session import get_session
from ..models.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate, ApprovalStatus
from ..models.user import SystemRole, User


router = APIRouter(prefix="/restaurants", tags=["Restaurants"])

@router.post("/", response_model=Restaurant, status_code=status.HTTP_201_CREATED)
async def create_restaurant(restaurant: RestaurantCreate, session: Session = Depends(get_session), current_user: User = Depends(require_restaurant_creation_access())):
    """
    Creates a new restaurant in the database.
    """
    new_restaurant = Restaurant.model_validate(restaurant)
    session.add(new_restaurant)
    session.commit()
    session.refresh(new_restaurant)
    return new_restaurant

@router.get("/", response_model=list[Restaurant])
async def get_restaurants(session: Session = Depends(get_session), current_user: User = Depends(require_system_roles(SystemRole.SUPERADMIN))):
    """
    Fetches all restaurants from the database.
    """
    restaurants = session.exec(select(Restaurant)).all()
    return restaurants

@router.get("/{restaurant_id}", response_model=Restaurant)
async def get_restaurant(restaurant_id: int, session: Session = Depends(get_session), current_user: User = Depends(require_read_restaurant_access())):
    """
    Fetches a restaurant by ID from the database.
    """
    restaurant = session.exec(select(Restaurant).where(Restaurant.id == restaurant_id)).first()
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    return restaurant

@router.put("/{restaurant_id}", response_model=Restaurant)
async def update_restaurant(restaurant_id: int, updated_restaurant: RestaurantUpdate, session: Session = Depends(get_session), current_user: User = Depends(require_manage_restaurant_access())):
    """
    Updates a restaurant's information in the database.
    """
    existing_restaurant = session.exec(select(Restaurant).where(Restaurant.id == restaurant_id)).first()
    if not existing_restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

    for key, value in updated_restaurant.model_dump(exclude_unset=True).items():
        setattr(existing_restaurant, key, value)

    session.add(existing_restaurant)
    session.commit()
    session.refresh(existing_restaurant)
    return existing_restaurant

@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_restaurant(restaurant_id: int, session: Session = Depends(get_session), current_user: User = Depends(require_manage_restaurant_access())):
    """
    Deletes a restaurant by ID from the database.
    """
    restaurant = session.exec(select(Restaurant).where(Restaurant.id == restaurant_id)).first()
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

    session.delete(restaurant)
    session.commit()
    return None


# ==================== Admin Endpoints ====================

@router.get("/admin/pending", response_model=list[Restaurant])
async def get_pending_restaurants(
    session: Session = Depends(get_session), 
    current_user: User = Depends(require_system_roles(SystemRole.SUPERADMIN))
):
    """
    Admin only: Get all restaurants awaiting approval.
    """
    restaurants = session.exec(
        select(Restaurant).where(Restaurant.approval_status == ApprovalStatus.PENDING)
    ).all()
    return restaurants


@router.post("/{restaurant_id}/approve", response_model=Restaurant)
async def approve_restaurant(
    restaurant_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_system_roles(SystemRole.SUPERADMIN))
):
    """
    Admin only: Approve a restaurant registration.
    """
    restaurant = session.exec(select(Restaurant).where(Restaurant.id == restaurant_id)).first()
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    
    restaurant.approval_status = ApprovalStatus.APPROVED
    session.add(restaurant)
    session.commit()
    session.refresh(restaurant)
    return restaurant


@router.post("/{restaurant_id}/reject", response_model=Restaurant)
async def reject_restaurant(
    restaurant_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_system_roles(SystemRole.SUPERADMIN))
):
    """
    Admin only: Reject a restaurant registration.
    """
    restaurant = session.exec(select(Restaurant).where(Restaurant.id == restaurant_id)).first()
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    
    restaurant.approval_status = ApprovalStatus.REJECTED
    session.add(restaurant)
    session.commit()
    session.refresh(restaurant)
    return restaurant


@router.post("/{restaurant_id}/suspend", response_model=Restaurant)
async def suspend_restaurant(
    restaurant_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_system_roles(SystemRole.SUPERADMIN))
):
    """
    Admin only: Suspend a restaurant.
    """
    restaurant = session.exec(select(Restaurant).where(Restaurant.id == restaurant_id)).first()
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    
    restaurant.approval_status = ApprovalStatus.SUSPENDED
    session.add(restaurant)
    session.commit()
    session.refresh(restaurant)
    return restaurant