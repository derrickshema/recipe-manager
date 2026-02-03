"""
Payment Routes - Stripe Integration

This module handles payment processing with Stripe Checkout.

Flow:
1. Customer places order (status: PENDING)
2. Customer clicks "Pay" → we create a Stripe Checkout Session
3. Customer is redirected to Stripe's hosted payment page
4. After payment, Stripe sends a webhook → we mark order as PAID
5. Customer is redirected back to our success page

Key Concepts:
- Checkout Session: A temporary Stripe object that represents a payment attempt
- Webhook: Stripe calls our server to notify us of events (like successful payment)
- Webhook Secret: Used to verify the webhook really came from Stripe (not a hacker)
"""

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session, select

from ..db.session import get_session
from ..models.order import Order
from ..models.enums import OrderStatus
from ..utilities.auth import get_current_user
from ..models.user import User
from ..config import settings

router = APIRouter(prefix="/payments", tags=["Payments"])

# Configure Stripe with API key from centralized settings
# In production, use STRIPE_SECRET_KEY (live key)
# In development, use test key (starts with sk_test_)
stripe.api_key = settings.STRIPE_SECRET_KEY

# Webhook secret for verifying webhook signatures
# Get this from Stripe Dashboard > Webhooks > Signing secret
WEBHOOK_SECRET = settings.STRIPE_WEBHOOK_SECRET

# Frontend URLs for redirect after payment
FRONTEND_URL = settings.FRONTEND_URL


@router.post("/create-checkout-session")
async def create_checkout_session(
    order_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a Stripe Checkout Session for an order.
    
    This endpoint:
    1. Validates the order exists and belongs to the user
    2. Checks the order is in PENDING status
    3. Creates a Stripe Checkout Session with line items
    4. Returns the checkout URL for the frontend to redirect to
    
    The checkout session includes:
    - Line items (what the customer is buying)
    - Success/cancel URLs (where to redirect after payment)
    - Metadata (our order_id so we can link payment to order)
    """
    # Step 1: Get and validate the order
    order = session.exec(
        select(Order).where(Order.id == order_id)
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Only the customer who placed the order can pay for it
    if order.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only pay for your own orders"
        )
    
    # Can only pay for pending orders
    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order is already {order.status.value}, cannot process payment"
        )
    
    # Step 2: Create Stripe Checkout Session
    try:
        # Build line items from order
        # In a real app, you'd include individual items
        # For simplicity, we're creating one line item for the total
        line_items = [
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"Order #{order.id}",
                        "description": f"Order from restaurant",
                    },
                    # Stripe expects amounts in cents
                    "unit_amount": int(order.total_amount * 100),
                },
                "quantity": 1,
            }
        ]
        
        # Create the checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            # Where to redirect after successful payment
            success_url=f"{FRONTEND_URL}/orders?payment=success&order_id={order.id}",
            # Where to redirect if customer cancels
            cancel_url=f"{FRONTEND_URL}/orders?payment=cancelled&order_id={order.id}",
            # Metadata lets us link this payment back to our order
            metadata={
                "order_id": str(order.id),
                "customer_id": str(current_user.id),
            },
        )
        
        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stripe error: {str(e)}"
        )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Handle Stripe webhooks.
    
    Stripe sends webhooks to notify us of events like:
    - checkout.session.completed (payment successful)
    - payment_intent.payment_failed (payment failed)
    
    Security:
    - We verify the webhook signature to ensure it's really from Stripe
    - This prevents attackers from faking payment confirmations
    
    Flow:
    1. Receive webhook from Stripe
    2. Verify signature using webhook secret
    3. Parse the event
    4. If checkout completed, mark order as PAID
    """
    # Get the raw request body (needed for signature verification)
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing stripe-signature header"
        )
    
    # Verify the webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload"
        )
    except stripe.error.SignatureVerificationError:
        # Invalid signature - could be an attacker!
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )
    
    # Handle the event
    if event["type"] == "checkout.session.completed":
        # Payment was successful!
        checkout_session = event["data"]["object"]
        
        # Get our order_id from the metadata we attached
        order_id = checkout_session.get("metadata", {}).get("order_id")
        
        if order_id:
            # Update the order status to PAID
            order = session.exec(
                select(Order).where(Order.id == int(order_id))
            ).first()
            
            if order and order.status == OrderStatus.PENDING:
                order.status = OrderStatus.PAID
                session.add(order)
                session.commit()
                
                # TODO: Send WebSocket notification to restaurant
                # TODO: Send confirmation email to customer
                
                print(f"✅ Order #{order_id} marked as PAID")
    
    elif event["type"] == "payment_intent.payment_failed":
        # Payment failed
        payment_intent = event["data"]["object"]
        print(f"❌ Payment failed: {payment_intent.get('id')}")
        # Could send notification to customer
    
    # Return 200 to acknowledge receipt
    # If we don't return 200, Stripe will retry the webhook
    return {"status": "success"}
