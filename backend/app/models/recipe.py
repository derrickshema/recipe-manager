import datetime
from typing import List

from sqlmodel import JSON, Column, Field, Relationship, SQLModel

from backend.app.models.restaurant import Restaurant


class RecipeBase(SQLModel):
    title: str
    description: str | None = None
    ingredients: List[str] = Field(sa_column=Column(JSON))
    instructions: List[str] = Field(sa_column=Column(JSON))
    prep_time: int | None = None  # in minutes
    cook_time: int | None = None  # in minutes
    servings: int | None = None
    restaurant_id: int | None = Field(default=None, foreign_key="restaurant.id")

    restaurant: "Restaurant" = Relationship(back_populates="recipes")

class Recipe(RecipeBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

class RecipeCreate(RecipeBase):
    pass

class RecipeRead(RecipeBase):
    id: int
    restaurant_id: int | None
    created_at: datetime
    updated_at: datetime

class RecipeUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    ingredients: List[str] | None = None
    instructions: List[str] | None = None
    prep_time: int | None = None  # in minutes
    cook_time: int | None = None  # in minutes
    servings: int | None = None
    restaurant_id: int | None = None