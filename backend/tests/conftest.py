"""
Test Configuration - conftest.py

This file is SPECIAL to pytest. It's automatically loaded before any tests run.
It contains "fixtures" - reusable pieces of test setup.

WHAT IS A FIXTURE?
==================
A fixture is a function that provides data or setup for tests. Instead of 
repeating setup code in every test, you define it once here.

Example:
    @pytest.fixture
    def test_user():
        return {"username": "testuser", "password": "secret"}
    
    def test_login(test_user):  # pytest injects the fixture automatically!
        response = client.post("/auth/login", json=test_user)
        assert response.status_code == 200

WHY USE FIXTURES?
=================
1. DRY (Don't Repeat Yourself) - Write setup code once
2. Isolation - Each test gets a fresh state
3. Readability - Tests focus on what they're testing, not setup
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# Import our app and database session dependency
from app.main import app
from app.db.session import get_session
from app.models.user import User, SystemRole
from app.models.restaurant import Restaurant, ApprovalStatus
from app.models.membership import Membership, OrgRole
from app.models.recipe import Recipe
from app.models.order import Order, OrderItem
from app.models.enums import OrderStatus
from app.utilities.auth_utils import hash_password


# =============================================================================
# Database Fixture - Creates a fresh test database for each test
# =============================================================================

@pytest.fixture(name="session")
def session_fixture():
    """
    Creates an in-memory SQLite database for testing.
    
    WHY IN-MEMORY SQLITE?
    ---------------------
    - Super fast (no disk I/O)
    - Completely isolated (each test gets a fresh database)
    - No cleanup needed (disappears when test ends)
    
    In production we use PostgreSQL, but SQLite is fine for testing
    because SQLModel/SQLAlchemy abstracts the differences.
    
    WHAT'S StaticPool?
    ------------------
    Normally SQLAlchemy creates new connections as needed. But SQLite
    in-memory databases are tied to a single connection - if you make
    a new connection, you get a new (empty) database!
    
    StaticPool keeps using the same connection, so all our test code
    sees the same data.
    """
    # Create an in-memory SQLite database
    engine = create_engine(
        "sqlite://",  # :// with no path = in-memory
        connect_args={"check_same_thread": False},  # SQLite threading quirk
        poolclass=StaticPool,  # Keep same connection for all operations
    )
    
    # Create all tables (User, Restaurant, Order, etc.)
    SQLModel.metadata.create_all(engine)
    
    # Create a session and yield it to the test
    with Session(engine) as session:
        yield session
    
    # After the test, the session closes and database disappears
    # (No cleanup needed - it was in-memory!)


# =============================================================================
# Test Client Fixture - A fake HTTP client that talks to our app
# =============================================================================

@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Creates a test client that can make HTTP requests to our FastAPI app.
    
    WHAT'S A TEST CLIENT?
    ---------------------
    Instead of starting a real server and making real HTTP requests,
    the TestClient simulates requests directly to our app. This is:
    - Faster (no network overhead)
    - Isolated (no port conflicts)
    - Deterministic (no timing issues)
    
    DEPENDENCY OVERRIDE
    -------------------
    Our app normally uses get_session() to get a database session.
    We override it to use our test session instead, so tests use
    the in-memory test database, not the real PostgreSQL database.
    """
    
    # Override the get_session dependency to use our test session
    def get_session_override():
        yield session
    
    app.dependency_overrides[get_session] = get_session_override
    
    # Create the test client
    client = TestClient(app)
    yield client
    
    # Clean up the override after the test
    app.dependency_overrides.clear()


# =============================================================================
# User Fixtures - Pre-made users for testing
# =============================================================================

@pytest.fixture(name="test_user_data")
def test_user_data_fixture():
    """Raw user data for registration tests."""
    return {
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "TestPassword123!",
    }


@pytest.fixture(name="test_customer")
def test_customer_fixture(session: Session):
    """
    Creates a customer user in the test database.
    
    Use this when you need a logged-in customer for testing.
    """
    user = User(
        first_name="Customer",
        last_name="One",
        username="customer1",
        email="customer1@example.com",
        hashed_password=hash_password("CustomerPass123!"),
        role=SystemRole.CUSTOMER,
        email_verified=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="test_owner")
def test_owner_fixture(session: Session):
    """Creates a restaurant owner user in the test database."""
    user = User(
        first_name="Owner",
        last_name="One",
        username="owner1",
        email="owner1@example.com",
        hashed_password=hash_password("OwnerPass123!"),
        role=SystemRole.RESTAURANT_OWNER,
        email_verified=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="test_superadmin")
def test_superadmin_fixture(session: Session):
    """Creates a superadmin user in the test database."""
    user = User(
        first_name="Super",
        last_name="Admin",
        username="superadmin",
        email="admin@example.com",
        hashed_password=hash_password("AdminPass123!"),
        role=SystemRole.SUPERADMIN,
        email_verified=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# =============================================================================
# Restaurant Fixtures
# =============================================================================

@pytest.fixture(name="test_restaurant")
def test_restaurant_fixture(session: Session, test_owner: User):
    """
    Creates an approved restaurant owned by test_owner.
    
    Note: This fixture depends on test_owner fixture - pytest handles
    the dependency automatically!
    """
    restaurant = Restaurant(
        restaurant_name="Test Restaurant",
        address="123 Test Street",
        phone="555-0100",
        cuisine_type="Italian",
        approval_status=ApprovalStatus.APPROVED,
    )
    session.add(restaurant)
    session.commit()
    session.refresh(restaurant)
    
    # Create membership linking owner to restaurant
    # Note: The field is 'role', not 'org_role'
    membership = Membership(
        user_id=test_owner.id,
        restaurant_id=restaurant.id,
        role=OrgRole.RESTAURANT_ADMIN,
    )
    session.add(membership)
    session.commit()
    
    return restaurant


@pytest.fixture(name="test_recipe")
def test_recipe_fixture(session: Session, test_restaurant: Restaurant):
    """Creates a recipe in the test restaurant."""
    recipe = Recipe(
        title="Test Pizza",
        description="A delicious test pizza",
        price=12.99,
        restaurant_id=test_restaurant.id,
    )
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return recipe


# =============================================================================
# Authentication Helper Fixture
# =============================================================================

@pytest.fixture(name="auth_headers")
def auth_headers_fixture():
    """
    Returns a function to create auth headers for a given user.
    
    Usage in tests:
        headers = auth_headers(test_customer, client)
        response = client.get("/some/protected/endpoint", headers=headers)
    """
    def _get_auth_headers(user: User, client: TestClient, password: str = None):
        """
        Log in as the user and return headers with the auth cookie.
        
        Note: Our app uses httpOnly cookies, so we need to let the
        test client handle cookies automatically.
        """
        # Determine password based on user role (matches our fixtures)
        if password is None:
            if user.role == SystemRole.CUSTOMER:
                password = "CustomerPass123!"
            elif user.role == SystemRole.RESTAURANT_OWNER:
                password = "OwnerPass123!"
            elif user.role == SystemRole.SUPERADMIN:
                password = "AdminPass123!"
            else:
                password = "TestPassword123!"
        
        # Log in to get the cookie
        response = client.post(
            "/auth/login",
            json={"username": user.username, "password": password}
        )
        
        # The cookie is automatically stored in the client
        # Just return empty dict - client handles cookies
        return {}
    
    return _get_auth_headers
