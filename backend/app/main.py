# Lifespan event for database initialization
from fastapi import FastAPI
from sqlmodel import SQLModel, Session, select
from .db.database import engine
from .routes import recipe_routes, restaurant_routes, auth_routes, admin_routes, upload_routes, order_routes, websocket_routes, payment_routes
from fastapi.middleware.cors import CORSMiddleware

# Define lifespan event to create database tables on startup
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

# Create FastAPI app instance with lifespan event
app = FastAPI(lifespan=lifespan)

# Set up CORS middleware for cross-origin requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Health Check Endpoint
# =============================================================================
# 
# WHY DO WE NEED THIS?
# --------------------
# When your app runs in production (Railway, AWS, etc.), the hosting platform
# needs to know if your app is healthy. It does this by calling a "health check"
# endpoint periodically (e.g., every 30 seconds).
#
# If your app doesn't respond, the platform knows something is wrong and can:
# - Restart your app automatically
# - Route traffic to healthy instances
# - Alert you that something is broken
#
# WHAT SHOULD A HEALTH CHECK DO?
# ------------------------------
# 1. Return quickly (don't do heavy processing)
# 2. Check critical dependencies (database connection)
# 3. Return a clear status (200 = healthy, 503 = unhealthy)
#
# TWO COMMON PATTERNS:
# - /health - Simple "am I alive?" check
# - /health/ready - Deeper check including database connectivity
# =============================================================================

@app.get("/health")
async def health_check():
    """
    Basic health check - is the server running?
    
    This is the simplest check. It just confirms the FastAPI server
    is up and can respond to HTTP requests.
    
    Used by: Load balancers, container orchestrators (Kubernetes/Docker)
    """
    return {"status": "healthy"}


@app.get("/health/ready")
async def readiness_check():
    """
    Readiness check - is the server ready to handle requests?
    
    This does a deeper check by verifying we can connect to the database.
    If the database is down, we return 503 (Service Unavailable).
    
    Used by: Kubernetes readiness probes, deployment health checks
    
    Why separate from /health?
    - /health = "Is the process alive?" (restart if not)
    - /health/ready = "Can it serve traffic?" (don't send requests if not)
    """
    try:
        # Try to connect to database and run a simple query
        with Session(engine) as session:
            session.exec(select(1)).first()
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        # Return 503 Service Unavailable if database is down
        from fastapi import Response
        return Response(
            content='{"status": "not ready", "database": "disconnected"}',
            status_code=503,
            media_type="application/json"
        )


# Include routers for different functionalities
app.include_router(auth_routes.router)
app.include_router(restaurant_routes.router)
app.include_router(recipe_routes.router)
app.include_router(admin_routes.router)
app.include_router(upload_routes.router)
app.include_router(order_routes.router)
app.include_router(websocket_routes.router)
app.include_router(payment_routes.router)
