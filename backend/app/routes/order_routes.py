"""
Order Routes

This module handles all order-related API endpoints.

Key endpoints:
- POST /orders - Create a new order (customer)
- GET /orders - Get customer's orders
- GET /orders/{order_id} - Get specific order details
- PUT /orders/{order_id}/status - Update order status (restaurant staff)
"""

from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from ..db.session import get_session
from ..models.order import Order, OrderCreate, OrderRead, OrderItem, OrderItemRead, OrderUpdate
from ..models.recipe import Recipe
from ..models.restaurant import Restaurant, ApprovalStatus
from ..models.user import User
from ..models.enums import SystemRole, OrderStatus
from ..utilities.auth import get_current_user
from .websocket_routes import notify_new_order, notify_order_status_change

router = APIRouter(prefix="/orders", tags=["Orders"])


# =============================================================================
# Helper Functions
# =============================================================================

def calculate_order_total(items: list[OrderItem]) -> Decimal:
    """Calculate the total amount for an order from its items."""
    return sum(item.subtotal for item in items)


def order_to_read_model(order: Order, include_restaurant_name: bool = False) -> OrderRead:
    """Convert Order database model to OrderRead response model."""
    # Get restaurant name if requested and restaurant is loaded
    restaurant_name = None
    if include_restaurant_name and order.restaurant is not None:
        restaurant_name = order.restaurant.restaurant_name
    
    return OrderRead(
        id=order.id,
        customer_id=order.customer_id,
        restaurant_id=order.restaurant_id,
        restaurant_name=restaurant_name,
        status=order.status,
        total_amount=order.total_amount,
        notes=order.notes,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=[
            OrderItemRead(
                id=item.id,
                recipe_id=item.recipe_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                notes=item.notes,
                subtotal=item.subtotal
            )
            for item in order.items
        ]
    )


# =============================================================================
# Customer Endpoints
# =============================================================================

@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new order.
    
    This endpoint:
    1. Validates the user is a customer
    2. Validates the restaurant exists and is approved
    3. Validates all recipes exist and belong to the restaurant
    4. Creates the order with calculated totals
    
    The order starts in PENDING status (awaiting payment).
    """
    # Step 1: Only customers can place orders
    if current_user.role != SystemRole.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can place orders"
        )
    
    # Step 2: Validate restaurant exists and is approved
    restaurant = session.exec(
        select(Restaurant).where(Restaurant.id == order_data.restaurant_id)
    ).first()
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    if restaurant.approval_status != ApprovalStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot order from this restaurant - it is not currently available"
        )
    
    # Step 3: Validate items and calculate prices
    if not order_data.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one item"
        )
    
    order_items: list[OrderItem] = []
    
    for item_data in order_data.items:
        # Get the recipe
        recipe = session.exec(
            select(Recipe).where(
                Recipe.id == item_data.recipe_id,
                Recipe.restaurant_id == order_data.restaurant_id
            )
        ).first()
        
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Recipe with id {item_data.recipe_id} not found in this restaurant"
            )
        
        # Create order item with price at time of order
        subtotal = recipe.price * item_data.quantity
        order_item = OrderItem(
            recipe_id=recipe.id,
            quantity=item_data.quantity,
            unit_price=recipe.price,
            subtotal=subtotal,
            notes=item_data.notes
        )
        order_items.append(order_item)
    
    # Step 4: Create the order
    total_amount = calculate_order_total(order_items)
    
    new_order = Order(
        customer_id=current_user.id,
        restaurant_id=order_data.restaurant_id,
        status=OrderStatus.PENDING,
        total_amount=total_amount,
        notes=order_data.notes
    )
    
    session.add(new_order)
    session.commit()
    session.refresh(new_order)
    
    # Step 5: Add items to the order (now that we have the order ID)
    for item in order_items:
        item.order_id = new_order.id
        session.add(item)
    
    session.commit()
    session.refresh(new_order)
    
    # Convert to read model for response
    order_read = order_to_read_model(new_order)
    
    # Send WebSocket notification to restaurant (in background)
    background_tasks.add_task(
        notify_new_order,
        order_data.restaurant_id,
        order_read.model_dump(mode='json')
    )
    
    return order_read


@router.get("/", response_model=list[OrderRead])
async def get_my_orders(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get all orders for the current customer.
    Returns orders sorted by most recent first, includes restaurant name.
    """
    if current_user.role != SystemRole.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can view their orders"
        )
    
    orders = session.exec(
        select(Order)
        .where(Order.customer_id == current_user.id)
        .options(selectinload(Order.restaurant), selectinload(Order.items))
        .order_by(Order.created_at.desc())
    ).all()
    
    return [order_to_read_model(order, include_restaurant_name=True) for order in orders]


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific order by ID.
    
    Customers can only view their own orders.
    Restaurant staff can view orders for their restaurant.
    """
    order = session.exec(
        select(Order).where(Order.id == order_id)
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check access: customer can see their own orders
    if current_user.role == SystemRole.CUSTOMER:
        if order.customer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own orders"
            )
    
    # TODO: Add check for restaurant staff access
    
    return order_to_read_model(order)


# =============================================================================
# Restaurant Staff Endpoints
# =============================================================================

@router.get("/restaurant/{restaurant_id}", response_model=list[OrderRead])
async def get_restaurant_orders(
    restaurant_id: int,
    status_filter: OrderStatus | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get all orders for a restaurant.
    
    This endpoint is for restaurant staff to view incoming orders.
    Optional status filter to show only orders in a specific state.
    
    TODO: Add proper RBAC to verify user is staff of this restaurant
    """
    # Build query
    query = select(Order).where(Order.restaurant_id == restaurant_id)
    
    if status_filter:
        query = query.where(Order.status == status_filter)
    
    query = query.order_by(Order.created_at.desc())
    
    orders = session.exec(query).all()
    
    return [order_to_read_model(order) for order in orders]


@router.put("/{order_id}/status", response_model=OrderRead)
async def update_order_status(
    order_id: int,
    update_data: OrderUpdate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update the status of an order.
    
    Status workflow:
    - PENDING → PAID (after payment confirmation)
    - PAID → PREPARING (restaurant starts preparing)
    - PREPARING → READY (order is ready for pickup)
    - READY → COMPLETED (customer received order)
    - PENDING/PAID → CANCELLED (order cancelled before preparation)
    
    TODO: Add proper RBAC and status transition validation
    """
    order = session.exec(
        select(Order).where(Order.id == order_id)
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Validate status transitions
    if update_data.status:
        valid_transitions = {
            OrderStatus.PENDING: [OrderStatus.PAID, OrderStatus.CANCELLED],
            OrderStatus.PAID: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
            OrderStatus.PREPARING: [OrderStatus.READY],
            OrderStatus.READY: [OrderStatus.COMPLETED],
            OrderStatus.COMPLETED: [],  # Terminal state
            OrderStatus.CANCELLED: [],  # Terminal state
        }
        
        if update_data.status not in valid_transitions.get(order.status, []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot transition from {order.status.value} to {update_data.status.value}"
            )
        
        order.status = update_data.status
    
    if update_data.notes is not None:
        order.notes = update_data.notes
    
    session.add(order)
    session.commit()
    session.refresh(order)
    
    # Convert to read model for response
    order_read = order_to_read_model(order)
    
    # Send WebSocket notification to customer (in background)
    background_tasks.add_task(
        notify_order_status_change,
        order.customer_id,
        order_read.model_dump(mode='json')
    )
    
    return order_read
