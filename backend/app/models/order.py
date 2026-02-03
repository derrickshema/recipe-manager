"""
Order Models

This module defines the Order and OrderItem models for the ordering system.

Key Concepts:
- Order: The main order record (who ordered, from where, status, total)
- OrderItem: Individual items in an order (what was ordered, how many, price)

Relationships:
- Order belongs to a User (customer)
- Order belongs to a Restaurant
- Order has many OrderItems
- OrderItem references a Recipe
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from .enums import OrderStatus

if TYPE_CHECKING:
    from .user import User
    from .restaurant import Restaurant
    from .recipe import Recipe


# =============================================================================
# Order Item Model
# =============================================================================

class OrderItemBase(SQLModel):
    """
    Base fields for an order item.
    
    Why store unit_price here instead of just referencing the recipe?
    Because prices can change! We want to capture the price AT THE TIME of order.
    """
    quantity: int = Field(ge=1, description="Number of this item ordered")
    unit_price: Decimal = Field(decimal_places=2, description="Price per unit at time of order")
    notes: str | None = Field(default=None, description="Special instructions (e.g., 'no onions')")


class OrderItem(OrderItemBase, table=True):
    """
    Database model for an individual item in an order.
    
    Example: If someone orders "2 Margherita Pizzas", that's one OrderItem
    with quantity=2 and unit_price=12.99
    """
    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", description="Which order this item belongs to")
    recipe_id: int = Field(foreign_key="recipe.id", description="Which menu item was ordered")
    
    # Computed field: quantity * unit_price
    subtotal: Decimal = Field(decimal_places=2, description="Total for this line item")
    
    # Relationships
    order: "Order" = Relationship(back_populates="items")
    recipe: "Recipe" = Relationship()


class OrderItemCreate(SQLModel):
    """
    What the customer sends when creating an order item.
    They only need to specify the recipe and quantity - we look up the price.
    """
    recipe_id: int
    quantity: int = Field(ge=1, default=1)
    notes: str | None = None


class OrderItemRead(OrderItemBase):
    """Response model for order items - includes computed fields."""
    id: int
    recipe_id: int
    subtotal: Decimal
    # We could also include recipe details here if needed


# =============================================================================
# Order Model
# =============================================================================

class OrderBase(SQLModel):
    """
    Base fields for an order.
    
    total_amount is calculated from all OrderItems, but we store it
    for quick access (denormalization - a common pattern).
    """
    total_amount: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    notes: str | None = Field(default=None, description="General order notes")


class Order(OrderBase, table=True):
    """
    Database model for an order.
    
    Represents a customer's order from a restaurant.
    """
    id: int | None = Field(default=None, primary_key=True)
    
    # Who placed the order
    customer_id: int = Field(foreign_key="user.id")
    
    # Which restaurant
    restaurant_id: int = Field(foreign_key="restaurant.id")
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)}
    )
    
    # Relationships
    customer: "User" = Relationship(back_populates="orders")
    restaurant: "Restaurant" = Relationship(back_populates="orders")
    items: List["OrderItem"] = Relationship(back_populates="order")


class OrderCreate(SQLModel):
    """
    What the customer sends to create an order.
    
    They specify:
    - Which restaurant they're ordering from
    - What items they want (list of recipe_id + quantity)
    - Optional notes
    """
    restaurant_id: int
    items: List[OrderItemCreate]
    notes: str | None = None


class OrderRead(OrderBase):
    """
    Response model for orders.
    Includes all the computed and related data.
    """
    id: int
    customer_id: int
    restaurant_id: int
    restaurant_name: str | None = None  # Optional: included when we join with restaurant
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemRead] = []


class OrderUpdate(SQLModel):
    """
    Fields that can be updated on an order.
    Mainly used by restaurant staff to update status.
    """
    status: OrderStatus | None = None
    notes: str | None = None
