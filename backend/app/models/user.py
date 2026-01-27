from datetime import datetime, timezone
import re
from sqlmodel import Column, Field, Relationship, SQLModel, Enum
from pydantic import field_validator, EmailStr
import enum
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .membership import Membership

from .membership import OrgRole

class SystemRole(str, enum.Enum):
    SUPERADMIN = "superadmin"        # App admin - manages restaurants, owners, employees, customers
    CUSTOMER = "customer"            # End user who orders food from restaurants
    RESTAURANT_OWNER = "restaurant_owner"  # Restaurant owner (can create/manage restaurants)
    SUSPENDED = "suspended"          # Account suspended

class UserBase(SQLModel):
    """
    Base model for User with common fields.
    """
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    username: str = Field(index=True, unique=True, description="Unique username for the user")
    email: EmailStr = Field(index=True, unique=True, description="User's email address")
    role: SystemRole = Field(
        default=SystemRole.CUSTOMER,
        sa_column=Column(Enum(SystemRole, name="system_role", create_type=True)),
        description="System-wide role for the user"
    )

    @field_validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must be alphanumeric with underscores only')
        return v
    
    @field_validator('email')
    def validate_email(cls, v):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, v):
            raise ValueError('Invalid email format')
        return v

class User(UserBase, table=True):
    """User model for database table."""
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str = Field(max_length=255) # Store hashed password
    email_verified: bool = Field(default=False, description="Whether the user's email has been verified")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)}
    ) 

    # Cascade delete: when user is deleted, delete all their memberships
    memberships: list["Membership"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class UserCreate(UserBase):
    """Model for creating a new user."""
    password: str
    org_role: Optional[OrgRole] = None  # Optional org role for initial membership
    restaurant_id: Optional[int] = None  # Optional restaurant ID for initial membership

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserRead(UserBase):
    """Model for reading user data."""
    id: int
    role: SystemRole
    email_verified: bool = False

class UserUpdate(SQLModel):
    """Model for updating user data."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[SystemRole] = None
    password: Optional[str] = None

class UserLogin(SQLModel):
    """Model for user login."""
    username: str
    password: str

class Token(SQLModel):
    """Model for authentication token."""
    access_token: str
    token_type: str