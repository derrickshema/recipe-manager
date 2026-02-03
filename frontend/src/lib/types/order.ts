// ==================== Order Status ====================

/**
 * Order status enum
 * Matches backend OrderStatus enum
 */
export enum OrderStatus {
    PENDING = "pending",        // Order created, awaiting payment
    PAID = "paid",              // Payment confirmed
    PREPARING = "preparing",    // Restaurant is preparing the order
    READY = "ready",            // Ready for pickup/delivery
    COMPLETED = "completed",    // Customer received the order
    CANCELLED = "cancelled"     // Order was cancelled
}

// ==================== Order Item Types ====================

/**
 * Order item in a response
 */
export interface OrderItem {
    id: number;
    recipe_id: number;
    quantity: number;
    unit_price: number;
    notes?: string;
    subtotal: number;
}

/**
 * Order item for creating an order
 */
export interface OrderItemCreate {
    recipe_id: number;
    quantity: number;
    notes?: string;
}

// ==================== Order Types ====================

/**
 * Complete order entity
 * Returned from GET /orders/{id}
 */
export interface Order {
    id: number;
    customer_id: number;
    restaurant_id: number;
    restaurant_name?: string;  // Included when fetching customer's orders
    status: OrderStatus;
    total_amount: number;
    notes?: string;
    created_at: string;
    updated_at: string;
    items: OrderItem[];
}

/**
 * Order creation request payload
 * Sent to POST /orders
 */
export interface OrderCreateRequest {
    restaurant_id: number;
    items: OrderItemCreate[];
    notes?: string;
}

/**
 * Order update request payload
 * Sent to PUT /orders/{id}/status
 */
export interface OrderUpdateRequest {
    status?: OrderStatus;
    notes?: string;
}
