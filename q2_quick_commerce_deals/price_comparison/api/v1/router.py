"""Main API v1 router for the price comparison platform."""

from fastapi import APIRouter

from .endpoints import (
    query,
    products,
    platforms,
    analytics,
    users,
    auth,
    monitoring,
)

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(platforms.router, prefix="/platforms", tags=["Platforms"])
api_router.include_router(query.router, prefix="/query", tags=["Natural Language Query"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["Monitoring"]) 