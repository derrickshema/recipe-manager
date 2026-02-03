import enum

class SystemRole(str, enum.Enum):
    SUPERADMIN = "superadmin"        # App admin - manages restaurants, owners, employees, customers
    CUSTOMER = "customer"            # End user who orders food from restaurants
    RESTAURANT_OWNER = "restaurant_owner"  # Restaurant owner (can create/manage restaurants)
    SUSPENDED = "suspended"          # Account suspended

class OrgRole(str, enum.Enum):
    RESTAURANT_ADMIN = "restaurant_admin"
    EMPLOYEE = "employee"

class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"      # Awaiting admin approval
    APPROVED = "approved"    # Approved and active
    REJECTED = "rejected"    # Rejected by admin
    SUSPENDED = "suspended"  # Suspended by admin

class OrderStatus(str, enum.Enum):
    """
    Order status workflow:
    PENDING → PAID → PREPARING → READY → COMPLETED
                ↘ CANCELLED (can cancel before PREPARING)
    """
    PENDING = "pending"        # Order created, awaiting payment
    PAID = "paid"              # Payment confirmed
    PREPARING = "preparing"    # Restaurant is preparing the order
    READY = "ready"            # Ready for pickup/delivery
    COMPLETED = "completed"    # Customer received the order
    CANCELLED = "cancelled"    # Order was cancelled
