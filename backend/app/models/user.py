from datetime import datetime, timezone
import re
from sqlmodel import Field, Index, Relationship, SQLModel, UniqueConstraint
from pydantic import field_validator, EmailStr
import enum

# from .restaurant import Restaurant

class Role(str, enum.Enum):
    """User roles for access control."""
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class UserBase(SQLModel):
    """
    Base model for User with common fields.
    """
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    username: str = Field(index=True, unique=True, description="Unique username for the user")
    email: EmailStr = Field(index=True, unique=True, description="User's email address")
    role: Role = Field(default=Role.VIEWER)    
    restaurant_id: int = Field(foreign_key="restaurant.id", index=True)

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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)}
    ) 

    restaurant: "Restaurant" = Relationship(back_populates="users") 

class UserCreate(UserBase):
    """Model for creating a new user."""
    password: str

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
    role: Role
    restaurant_id: int | None

class UserUpdate(SQLModel):
    """Model for updating user data."""
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    email: str | None = None
    role: Role | None = None
    password: str | None = None
    restaurant_id: int | None = None

class UserLogin(SQLModel):
    """Model for user login."""
    username: str
    password: str

class Token(SQLModel):
    """Model for authentication token."""
    access_token: str
    token_type: str