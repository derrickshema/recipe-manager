from .enums import OrgRole
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .user import User
    from .restaurant import Restaurant


from sqlmodel import UniqueConstraint

class Membership(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("user_id", "restaurant_id", name="uix_user_restaurant"),)
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    restaurant_id: int = Field(foreign_key="restaurant.id")
    role: OrgRole

    user: "User" = Relationship(back_populates="memberships")
    restaurant: "Restaurant" = Relationship(back_populates="memberships")