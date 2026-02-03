from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..utilities.auth import get_current_user
from ..utilities.rbac import require_manage_restaurant_access, require_read_restaurant_access, require_restaurant_creation_access, require_system_roles

from ..db.session import get_session
from ..models.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate, ApprovalStatus
from ..models.membership import Membership
from ..models.user import SystemRole, User
from ..config import settings


router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.get("/my", response_model=list[Restaurant])
async def get_my_restaurants(
    session: Session = Depends(get_session), 
    current_user: User = Depends(get_current_user)
):
    """
    Get all restaurants the current user has membership to.
    Returns restaurants based on the user's memberships.
    """
    # Get user's memberships with restaurant IDs
    memberships = session.exec(
        select(Membership).where(Membership.user_id == current_user.id)
    ).all()
    
    if not memberships:
        return []
    
    # Get all restaurants for these memberships
    restaurant_ids = [m.restaurant_id for m in memberships]
    restaurants = session.exec(
        select(Restaurant).where(Restaurant.id.in_(restaurant_ids))
    ).all()
    
    return restaurants


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


@router.get("/approved", response_model=list[Restaurant])
async def get_approved_restaurants(
    session: Session = Depends(get_session),
    search: str | None = None,
    cuisine: str | None = None
):
    """
    Public endpoint: Fetches all approved restaurants.
    No authentication required - customers can browse without logging in.
    
    Query Parameters:
    - search: Search by restaurant name (case-insensitive partial match)
    - cuisine: Filter by cuisine type (case-insensitive partial match)
    """
    query = select(Restaurant).where(Restaurant.approval_status == ApprovalStatus.APPROVED)
    
    if search:
        query = query.where(Restaurant.restaurant_name.ilike(f"%{search}%"))
    
    if cuisine:
        query = query.where(Restaurant.cuisine_type.ilike(f"%{cuisine}%"))
    
    restaurants = session.exec(query).all()
    return restaurants


@router.get("/approved/{restaurant_id}", response_model=Restaurant)
async def get_approved_restaurant(
    restaurant_id: int,
    session: Session = Depends(get_session)
):
    """
    Public endpoint: Fetches a specific approved restaurant by ID.
    No authentication required - customers can view restaurant details without logging in.
    """
    restaurant = session.exec(
        select(Restaurant).where(
            Restaurant.id == restaurant_id,
            Restaurant.approval_status == ApprovalStatus.APPROVED
        )
    ).first()
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found or not available"
        )
    
    return restaurant


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


# ==================== Membership Management ====================

from pydantic import BaseModel
from ..models.membership import OrgRole

class MembershipResponse(BaseModel):
    id: int
    user_id: int
    restaurant_id: int
    role: OrgRole
    user_email: str | None = None
    user_name: str | None = None

class AddMemberRequest(BaseModel):
    email: str
    role: OrgRole

class UpdateMembershipRequest(BaseModel):
    role: OrgRole

class InviteStaffRequest(BaseModel):
    email: str
    role: OrgRole


@router.get("/{restaurant_id}/memberships", response_model=list[MembershipResponse])
async def get_memberships(
    restaurant_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_manage_restaurant_access())
):
    """
    Get all memberships for a restaurant.
    Only restaurant admins and system admins can view memberships.
    """
    memberships = session.exec(
        select(Membership).where(Membership.restaurant_id == restaurant_id)
    ).all()
    
    result = []
    for m in memberships:
        user = session.exec(select(User).where(User.id == m.user_id)).first()
        result.append(MembershipResponse(
            id=m.id,
            user_id=m.user_id,
            restaurant_id=m.restaurant_id,
            role=m.role,
            user_email=user.email if user else None,
            user_name=f"{user.first_name} {user.last_name}" if user else None
        ))
    
    return result


@router.post("/{restaurant_id}/memberships", response_model=MembershipResponse, status_code=status.HTTP_201_CREATED)
async def add_member(
    restaurant_id: int,
    request: AddMemberRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_manage_restaurant_access())
):
    """
    Add a member to a restaurant by email.
    Only restaurant admins and system admins can add members.
    """
    # Find user by email
    user = session.exec(select(User).where(User.email == request.email)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found with this email")
    
    # Check if membership already exists
    existing = session.exec(
        select(Membership).where(
            Membership.user_id == user.id,
            Membership.restaurant_id == restaurant_id
        )
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a member of this restaurant")
    
    # Create membership
    membership = Membership(
        user_id=user.id,
        restaurant_id=restaurant_id,
        role=request.role
    )
    session.add(membership)
    session.commit()
    session.refresh(membership)
    
    return MembershipResponse(
        id=membership.id,
        user_id=membership.user_id,
        restaurant_id=membership.restaurant_id,
        role=membership.role,
        user_email=user.email,
        user_name=f"{user.first_name} {user.last_name}"
    )


@router.put("/{restaurant_id}/memberships/{membership_id}", response_model=MembershipResponse)
async def update_membership(
    restaurant_id: int,
    membership_id: int,
    request: UpdateMembershipRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_manage_restaurant_access())
):
    """
    Update a member's role.
    Only restaurant admins and system admins can update roles.
    """
    membership = session.exec(
        select(Membership).where(
            Membership.id == membership_id,
            Membership.restaurant_id == restaurant_id
        )
    ).first()
    if not membership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found")
    
    membership.role = request.role
    session.add(membership)
    session.commit()
    session.refresh(membership)
    
    user = session.exec(select(User).where(User.id == membership.user_id)).first()
    
    return MembershipResponse(
        id=membership.id,
        user_id=membership.user_id,
        restaurant_id=membership.restaurant_id,
        role=membership.role,
        user_email=user.email if user else None,
        user_name=f"{user.first_name} {user.last_name}" if user else None
    )


@router.delete("/{restaurant_id}/memberships/{membership_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    restaurant_id: int,
    membership_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_manage_restaurant_access())
):
    """
    Remove a member from a restaurant.
    Only restaurant admins and system admins can remove members.
    Cannot remove yourself.
    """
    membership = session.exec(
        select(Membership).where(
            Membership.id == membership_id,
            Membership.restaurant_id == restaurant_id
        )
    ).first()
    if not membership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found")
    
    # Prevent removing yourself
    if membership.user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove yourself from the restaurant")
    
    session.delete(membership)
    session.commit()
    return None


# ==================== Staff Invitations ====================

from ..utilities.auth_utils import create_staff_invitation_token, verify_staff_invitation_token
from ..utilities.email import send_staff_invitation_email

class InvitationResponse(BaseModel):
    message: str
    email: str

class AcceptInvitationRequest(BaseModel):
    token: str

class InvitationInfoResponse(BaseModel):
    email: str
    restaurant_id: int
    restaurant_name: str
    role: str
    valid: bool


@router.post("/{restaurant_id}/invite", response_model=InvitationResponse)
async def invite_staff(
    restaurant_id: int,
    request: InviteStaffRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_manage_restaurant_access())
):
    """
    Invite a user to join a restaurant by email.
    Sends an invitation email with a secure link.
    Works for both existing and new users.
    """
    # Get the restaurant
    restaurant = session.exec(select(Restaurant).where(Restaurant.id == restaurant_id)).first()
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    
    # Check if user already exists and is already a member
    existing_user = session.exec(select(User).where(User.email == request.email)).first()
    if existing_user:
        existing_membership = session.exec(
            select(Membership).where(
                Membership.user_id == existing_user.id,
                Membership.restaurant_id == restaurant_id
            )
        ).first()
        if existing_membership:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="User is already a member of this restaurant"
            )
    
    # Create invitation token
    invitation_token = create_staff_invitation_token(
        email=request.email,
        restaurant_id=restaurant_id,
        role=request.role.value
    )
    
    # Send invitation email
    inviter_name = f"{current_user.first_name} {current_user.last_name}"
    email_sent = send_staff_invitation_email(
        to=request.email,
        invitation_token=invitation_token,
        restaurant_name=restaurant.restaurant_name,
        role=request.role.value,
        inviter_name=inviter_name
    )
    
    # In development, log the invitation link if email fails
    if not email_sent:
        invite_link = f"{settings.FRONTEND_URL}/accept-invitation?token={invitation_token}"
        print(f"\n{'='*60}")
        print(f"EMAIL FAILED - Use this link to accept invitation:")
        print(f"Email: {request.email}")
        print(f"Link: {invite_link}")
        print(f"{'='*60}\n")
    
    return InvitationResponse(
        message=f"Invitation sent to {request.email}" if email_sent else f"Invitation created for {request.email} (check server logs for link)",
        email=request.email
    )


@router.get("/invitation/verify", response_model=InvitationInfoResponse)
async def verify_invitation(
    token: str,
    session: Session = Depends(get_session)
):
    """
    Verify an invitation token and return its details.
    Used by the frontend to show invitation info before accepting.
    """
    payload = verify_staff_invitation_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired invitation token"
        )
    
    # Get restaurant name
    restaurant = session.exec(
        select(Restaurant).where(Restaurant.id == payload["restaurant_id"])
    ).first()
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    return InvitationInfoResponse(
        email=payload["email"],
        restaurant_id=payload["restaurant_id"],
        restaurant_name=restaurant.restaurant_name,
        role=payload["role"],
        valid=True
    )


@router.post("/invitation/accept", response_model=MembershipResponse)
async def accept_invitation(
    request: AcceptInvitationRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Accept an invitation to join a restaurant.
    The current logged-in user will be added to the restaurant.
    The user's email must match the invitation email.
    """
    # Verify the token
    payload = verify_staff_invitation_token(request.token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired invitation token"
        )
    
    # Verify the email matches
    if current_user.email.lower() != payload["email"].lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This invitation was sent to a different email address"
        )
    
    # Get the restaurant
    restaurant = session.exec(
        select(Restaurant).where(Restaurant.id == payload["restaurant_id"])
    ).first()
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    
    # Check if already a member
    existing = session.exec(
        select(Membership).where(
            Membership.user_id == current_user.id,
            Membership.restaurant_id == payload["restaurant_id"]
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already a member of this restaurant"
        )
    
    # Create the membership
    membership = Membership(
        user_id=current_user.id,
        restaurant_id=payload["restaurant_id"],
        role=OrgRole(payload["role"])
    )
    session.add(membership)
    session.commit()
    session.refresh(membership)
    
    return MembershipResponse(
        id=membership.id,
        user_id=membership.user_id,
        restaurant_id=membership.restaurant_id,
        role=membership.role,
        user_email=current_user.email,
        user_name=f"{current_user.first_name} {current_user.last_name}"
    )