"""
Order System Tests

These tests verify the order lifecycle:
- Customer places an order
- Order status transitions
- Only authorized users can update orders

ORDER STATUS FLOW
=================
PENDING → PAID → PREPARING → READY → COMPLETED
    ↓       ↓
CANCELLED  CANCELLED

Each transition has rules:
- Only restaurant staff can mark PREPARING → READY
- Only the customer who placed the order can view it
- etc.
"""

import pytest
from app.models.enums import OrderStatus


class TestCreateOrder:
    """Tests for order creation."""
    
    def test_create_order_success(self, client, test_customer, test_restaurant, test_recipe):
        """
        Test that a logged-in customer can place an order.
        
        This is the "happy path" for the order flow.
        """
        # Log in as customer
        client.post(
            "/auth/token",
            json={"username": test_customer.username, "password": "CustomerPass123!"}
        )
        
        # Create order
        order_data = {
            "restaurant_id": test_restaurant.id,
            "items": [
                {"recipe_id": test_recipe.id, "quantity": 2}
            ],
            "notes": "Extra cheese please"
        }
        
        response = client.post("/orders/", json=order_data)
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.json()}"
        
        data = response.json()
        assert data["restaurant_id"] == test_restaurant.id
        assert data["customer_id"] == test_customer.id
        assert data["status"] == "pending"
        assert len(data["items"]) == 1
        assert data["items"][0]["quantity"] == 2
        # Total should be 2 * 12.99 (test_recipe price)
        # Note: API returns total_amount as string for Decimal precision
        assert float(data["total_amount"]) == pytest.approx(25.98, rel=0.01)
    
    def test_create_order_requires_auth(self, client, test_restaurant, test_recipe):
        """Test that creating an order requires authentication."""
        order_data = {
            "restaurant_id": test_restaurant.id,
            "items": [{"recipe_id": test_recipe.id, "quantity": 1}],
        }
        
        response = client.post("/orders/", json=order_data)
        
        assert response.status_code == 401
    
    def test_create_order_invalid_restaurant(self, client, test_customer, test_recipe):
        """Test that creating an order for non-existent restaurant fails."""
        client.post(
            "/auth/token",
            json={"username": test_customer.username, "password": "CustomerPass123!"}
        )
        
        order_data = {
            "restaurant_id": 99999,  # Doesn't exist
            "items": [{"recipe_id": test_recipe.id, "quantity": 1}],
        }
        
        response = client.post("/orders/", json=order_data)
        
        assert response.status_code == 404
    
    def test_create_order_empty_items(self, client, test_customer, test_restaurant):
        """Test that creating an order with no items fails."""
        client.post(
            "/auth/token",
            json={"username": test_customer.username, "password": "CustomerPass123!"}
        )
        
        order_data = {
            "restaurant_id": test_restaurant.id,
            "items": [],  # Empty!
        }
        
        response = client.post("/orders/", json=order_data)
        
        # Should fail - can't have an order with no items
        assert response.status_code in [400, 422]


class TestOrderStatusTransitions:
    """Tests for order status updates."""
    
    def test_restaurant_can_update_to_preparing(
        self, client, session, test_owner, test_restaurant, test_customer, test_recipe
    ):
        """
        Test that restaurant owner can mark a PAID order as PREPARING.
        
        This simulates: Customer pays → Restaurant starts cooking
        """
        # First, create an order as customer
        client.post(
            "/auth/token",
            json={"username": test_customer.username, "password": "CustomerPass123!"}
        )
        
        order_response = client.post("/orders/", json={
            "restaurant_id": test_restaurant.id,
            "items": [{"recipe_id": test_recipe.id, "quantity": 1}],
        })
        order_id = order_response.json()["id"]
        
        # Manually set order to PAID (normally Stripe webhook does this)
        from app.models.order import Order
        from sqlmodel import select
        order = session.exec(select(Order).where(Order.id == order_id)).first()
        order.status = OrderStatus.PAID
        session.add(order)
        session.commit()
        
        # Now log in as restaurant owner
        client.post(
            "/auth/token",
            json={"username": test_owner.username, "password": "OwnerPass123!"}
        )
        
        # Update status to PREPARING
        response = client.put(
            f"/orders/{order_id}/status",
            json={"status": "preparing"}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "preparing"
    
    def test_cannot_skip_status(
        self, client, session, test_owner, test_restaurant, test_customer, test_recipe
    ):
        """
        Test that you can't skip statuses (e.g., PENDING → READY).
        
        Order must follow the proper flow.
        """
        # Create order as customer
        client.post(
            "/auth/token",
            json={"username": test_customer.username, "password": "CustomerPass123!"}
        )
        
        order_response = client.post("/orders/", json={
            "restaurant_id": test_restaurant.id,
            "items": [{"recipe_id": test_recipe.id, "quantity": 1}],
        })
        order_id = order_response.json()["id"]
        
        # Log in as owner
        client.post(
            "/auth/token",
            json={"username": test_owner.username, "password": "OwnerPass123!"}
        )
        
        # Try to skip from PENDING directly to READY (should fail)
        response = client.put(
            f"/orders/{order_id}/status",
            json={"status": "ready"}
        )
        
        assert response.status_code == 400
        assert "cannot transition" in response.json()["detail"].lower()


class TestOrderAccess:
    """Tests for order access control."""
    
    def test_customer_can_view_own_orders(
        self, client, test_customer, test_restaurant, test_recipe
    ):
        """Test that customers can see their own orders."""
        client.post(
            "/auth/token",
            json={"username": test_customer.username, "password": "CustomerPass123!"}
        )
        
        # Create an order
        client.post("/orders/", json={
            "restaurant_id": test_restaurant.id,
            "items": [{"recipe_id": test_recipe.id, "quantity": 1}],
        })
        
        # Get my orders
        response = client.get("/orders/")
        
        assert response.status_code == 200
        orders = response.json()
        assert len(orders) == 1
        assert orders[0]["customer_id"] == test_customer.id
    
    def test_customer_cannot_view_others_orders(
        self, client, session, test_customer, test_restaurant, test_recipe
    ):
        """
        Test that customers cannot see other customers' orders.
        
        Security test: A user should only see their own orders.
        """
        # Create another customer
        from app.models.user import User, SystemRole
        from app.utilities.auth_utils import hash_password
        
        other_customer = User(
            first_name="Other",
            last_name="Customer",
            username="other_customer",
            email="other@example.com",
            hashed_password=hash_password("OtherPass123!"),
            role=SystemRole.CUSTOMER,
            email_verified=True,
        )
        session.add(other_customer)
        session.commit()
        session.refresh(other_customer)
        
        # Log in as first customer and create an order
        client.post(
            "/auth/token",
            json={"username": test_customer.username, "password": "CustomerPass123!"}
        )
        client.post("/orders/", json={
            "restaurant_id": test_restaurant.id,
            "items": [{"recipe_id": test_recipe.id, "quantity": 1}],
        })
        
        # Log in as OTHER customer
        client.post(
            "/auth/token",
            json={"username": "other_customer", "password": "OtherPass123!"}
        )
        
        # Try to get orders - should only see own (none)
        response = client.get("/orders/")
        
        assert response.status_code == 200
        orders = response.json()
        assert len(orders) == 0  # Other customer has no orders


class TestCancelOrder:
    """Tests for order cancellation."""
    
    def test_customer_can_cancel_pending_order(
        self, client, test_customer, test_restaurant, test_recipe
    ):
        """Test that customers can cancel their pending orders."""
        client.post(
            "/auth/token",
            json={"username": test_customer.username, "password": "CustomerPass123!"}
        )
        
        # Create order
        order_response = client.post("/orders/", json={
            "restaurant_id": test_restaurant.id,
            "items": [{"recipe_id": test_recipe.id, "quantity": 1}],
        })
        order_id = order_response.json()["id"]
        
        # Cancel it
        response = client.put(
            f"/orders/{order_id}/status",
            json={"status": "cancelled"}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"
    
    def test_cannot_cancel_preparing_order(
        self, client, session, test_customer, test_owner, test_restaurant, test_recipe
    ):
        """
        Test that orders being prepared cannot be cancelled.
        
        Business rule: Once kitchen starts cooking, it's too late to cancel.
        """
        # Create order as customer
        client.post(
            "/auth/token",
            json={"username": test_customer.username, "password": "CustomerPass123!"}
        )
        
        order_response = client.post("/orders/", json={
            "restaurant_id": test_restaurant.id,
            "items": [{"recipe_id": test_recipe.id, "quantity": 1}],
        })
        order_id = order_response.json()["id"]
        
        # Set order to PREPARING (simulating kitchen started)
        from app.models.order import Order
        from sqlmodel import select
        order = session.exec(select(Order).where(Order.id == order_id)).first()
        order.status = OrderStatus.PAID
        session.commit()
        order.status = OrderStatus.PREPARING
        session.add(order)
        session.commit()
        
        # Try to cancel as customer
        response = client.put(
            f"/orders/{order_id}/status",
            json={"status": "cancelled"}
        )
        
        assert response.status_code == 400
        assert "cannot transition" in response.json()["detail"].lower()
