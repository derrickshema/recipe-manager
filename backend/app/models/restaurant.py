from datetime import datetime, timezone
from sqlmodel import Field, Relationship, SQLModel

# from .recipe import Recipe
# from .user import User


class RestaurantBase(SQLModel):
    restaurant_name: str = Field(max_length=100)

class Restaurant(RestaurantBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc), sa_column_kwargs={"onupdate": datetime.utcnow})

    users: list["User"] = Relationship(back_populates="restaurant")
    recipes: list["Recipe"] = Relationship(back_populates="restaurant")

class RestaurantCreate(RestaurantBase):
    pass

class RestaurantRead(RestaurantBase):
    id: int
    created_at: datetime
    updated_at: datetime

class RestaurantUpdate(SQLModel):
    restaurant_name: str | None = None


    
