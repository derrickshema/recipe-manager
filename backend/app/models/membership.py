import enum

from sqlmodel import Field, Relationship, SQLModel


class OrgRole(str, enum.Enum):
    RESTAURANT_ADMIN = "restaurant_admin"
    EMPLOYEE = "employee"

class Membership(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    restaurant_id: int = Field(foreign_key="restaurant.id")
    role: OrgRole

    user: "User" = Relationship(back_populates="memberships")
    restaurant: "Restaurant" = Relationship(back_populates="memberships")