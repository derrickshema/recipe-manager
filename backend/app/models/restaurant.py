from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
import enum

if TYPE_CHECKING:
    from .recipe import Recipe
    from .membership import Membership


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"      # Awaiting admin approval
    APPROVED = "approved"    # Approved and active
    REJECTED = "rejected"    # Rejected by admin
    SUSPENDED = "suspended"  # Suspended by admin


class RestaurantBase(SQLModel):
    restaurant_name: str = Field(max_length=100)
    cuisine_type: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    logo_url: str | None = Field(default=None, max_length=500, description="URL to restaurant logo image")


class Restaurant(RestaurantBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    approval_status: ApprovalStatus = Field(default=ApprovalStatus.PENDING)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)}
    )

    # Cascade delete: when restaurant is deleted, delete all its recipes and memberships
    recipes: list["Recipe"] = Relationship(
        back_populates="restaurant",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    memberships: list["Membership"] = Relationship(
        back_populates="restaurant",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class RestaurantCreate(RestaurantBase):
    pass


class RestaurantRead(RestaurantBase):
    id: int
    approval_status: ApprovalStatus
    created_at: datetime
    updated_at: datetime


class RestaurantUpdate(SQLModel):
    restaurant_name: str | None = None
    cuisine_type: str | None = None
    address: str | None = None
    phone: str | None = None
    logo_url: str | None = None
    approval_status: ApprovalStatus | None = None

class RestaurantOwnerRegistration(SQLModel):
    """
    Model for registering a restaurant owner with restaurant details.
    Combines user creation, restaurant creation, and membership assignment.
    """
    # Owner Information
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    username: str
    email: str
    password: str
    phone_number: str | None = None
    
    # Restaurant Information
    restaurant_name: str = Field(max_length=100)
    cuisine_type: str | None = Field(default=None, max_length=50)
    address: str | None = None
    restaurant_phone: str | None = None
