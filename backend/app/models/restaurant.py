import datetime
from sqlmodel import Field, Relationship, SQLModel

from backend.app.models.recipe import Recipe
from backend.app.models.user import User


class RestaurantBase(SQLModel):
    restaurant_name: str = Field(max_length=100)
    users: list["User"] = Relationship(back_populates="restaurant")
    recipes: list["Recipe"] = Relationship(back_populates="restaurant")

class Restaurant(RestaurantBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

class RestaurantCreate(RestaurantBase):
    pass

class RestaurantRead(RestaurantBase):
    id: int
    created_at: datetime
    updated_at: datetime

class RestaurantUpdate(SQLModel):
    restaurant_name: str | None = None


    
