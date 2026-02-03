from datetime import datetime, timezone
from decimal import Decimal
from typing import List, TYPE_CHECKING

from sqlmodel import JSON, Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .restaurant import Restaurant



class RecipeBase(SQLModel):
    title: str
    description: str | None = None
    ingredients: List[str] = Field(sa_column=Column(JSON))
    instructions: List[str] = Field(sa_column=Column(JSON))
    prep_time: int | None = None  # in minutes
    cook_time: int | None = None  # in minutes
    servings: int | None = None
    price: Decimal = Field(default=Decimal("0.00"), decimal_places=2, description="Price of the item")
    image_url: str | None = None  # S3 URL for recipe image

class Recipe(RecipeBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    restaurant_id: int = Field(foreign_key="restaurant.id")  # Required field in the table
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)}
    )

    restaurant: "Restaurant" = Relationship(back_populates="recipes")

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
    image_url: str | None = None  # S3 URL for recipe image