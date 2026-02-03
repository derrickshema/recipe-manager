"""
WebSocket Routes for Real-time Order Updates

This module provides WebSocket endpoints for real-time order notifications.

Key features:
- Restaurant staff can connect to receive new order notifications
- Customers can connect to track their order status changes
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Dict, Set
import json

router = APIRouter(prefix="/ws", tags=["WebSocket"])


# =============================================================================
# Connection Manager
# =============================================================================

class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        # Restaurant connections: restaurant_id -> set of websockets
        self.restaurant_connections: Dict[int, Set[WebSocket]] = {}
        # Customer connections: user_id -> set of websockets
        self.customer_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect_restaurant(self, websocket: WebSocket, restaurant_id: int):
        """Connect a restaurant staff member to receive order updates."""
        await websocket.accept()
        if restaurant_id not in self.restaurant_connections:
            self.restaurant_connections[restaurant_id] = set()
        self.restaurant_connections[restaurant_id].add(websocket)
    
    async def connect_customer(self, websocket: WebSocket, user_id: int):
        """Connect a customer to receive their order status updates."""
        await websocket.accept()
        if user_id not in self.customer_connections:
            self.customer_connections[user_id] = set()
        self.customer_connections[user_id].add(websocket)
    
    def disconnect_restaurant(self, websocket: WebSocket, restaurant_id: int):
        """Disconnect a restaurant staff member."""
        if restaurant_id in self.restaurant_connections:
            self.restaurant_connections[restaurant_id].discard(websocket)
            if not self.restaurant_connections[restaurant_id]:
                del self.restaurant_connections[restaurant_id]
    
    def disconnect_customer(self, websocket: WebSocket, user_id: int):
        """Disconnect a customer."""
        if user_id in self.customer_connections:
            self.customer_connections[user_id].discard(websocket)
            if not self.customer_connections[user_id]:
                del self.customer_connections[user_id]
    
    async def notify_restaurant_new_order(self, restaurant_id: int, order_data: dict):
        """Notify restaurant of a new order."""
        if restaurant_id in self.restaurant_connections:
            message = json.dumps({
                "type": "new_order",
                "data": order_data
            })
            dead_connections = set()
            for websocket in self.restaurant_connections[restaurant_id]:
                try:
                    await websocket.send_text(message)
                except Exception:
                    dead_connections.add(websocket)
            # Clean up dead connections
            for ws in dead_connections:
                self.restaurant_connections[restaurant_id].discard(ws)
    
    async def notify_customer_order_update(self, user_id: int, order_data: dict):
        """Notify customer of an order status change."""
        if user_id in self.customer_connections:
            message = json.dumps({
                "type": "order_update",
                "data": order_data
            })
            dead_connections = set()
            for websocket in self.customer_connections[user_id]:
                try:
                    await websocket.send_text(message)
                except Exception:
                    dead_connections.add(websocket)
            # Clean up dead connections
            for ws in dead_connections:
                self.customer_connections[user_id].discard(ws)


# Global connection manager instance
manager = ConnectionManager()


# =============================================================================
# WebSocket Endpoints
# =============================================================================

@router.websocket("/restaurant/{restaurant_id}")
async def restaurant_websocket(
    websocket: WebSocket,
    restaurant_id: int
):
    """
    WebSocket endpoint for restaurant staff to receive real-time order updates.
    
    Messages sent:
    - new_order: When a customer places a new order
    - order_cancelled: When an order is cancelled
    """
    await manager.connect_restaurant(websocket, restaurant_id)
    try:
        while True:
            # Keep connection alive, wait for messages (can be used for ping/pong)
            data = await websocket.receive_text()
            # Echo back for connection testing
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect_restaurant(websocket, restaurant_id)


@router.websocket("/customer/{user_id}")
async def customer_websocket(
    websocket: WebSocket,
    user_id: int
):
    """
    WebSocket endpoint for customers to receive real-time order status updates.
    
    Messages sent:
    - order_update: When order status changes
    """
    await manager.connect_customer(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect_customer(websocket, user_id)


# =============================================================================
# Helper function for routes to send notifications
# =============================================================================

async def notify_new_order(restaurant_id: int, order_data: dict):
    """Called from order_routes when a new order is created."""
    await manager.notify_restaurant_new_order(restaurant_id, order_data)


async def notify_order_status_change(customer_id: int, order_data: dict):
    """Called from order_routes when order status changes."""
    await manager.notify_customer_order_update(customer_id, order_data)
