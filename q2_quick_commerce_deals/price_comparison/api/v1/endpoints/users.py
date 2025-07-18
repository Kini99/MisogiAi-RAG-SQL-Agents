"""Users API endpoints for the price comparison platform."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ...database.base import get_db
from ...database.models.users import User, UserProfile, UserPreference, UserQuery
from ...services.cache_service import CacheService

router = APIRouter()

@router.get("/profile", summary="Get user profile")
async def get_user_profile(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get user profile information."""
    # This would typically use JWT authentication
    # For now, using user_id parameter
    cache_service = CacheService()
    cache_key = f"user_profile:{user_id}"
    
    cached_profile = await cache_service.get(cache_key)
    if cached_profile:
        return cached_profile
    
    # Mock user profile data
    profile = {
        "user_id": user_id,
        "email": f"user{user_id}@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "is_premium": False,
        "preferences": {
            "default_platforms": ["blinkit", "zepto"],
            "price_alerts": True,
            "email_notifications": True,
        },
        "stats": {
            "total_queries": 25,
            "favorite_products": 12,
            "price_alerts": 5,
        }
    }
    
    await cache_service.set(cache_key, profile, ttl=3600)
    return profile

@router.get("/queries", summary="Get user query history")
async def get_user_queries(
    user_id: int,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get user's query history."""
    # Mock query history
    queries = [
        {
            "id": 1,
            "query": "Which app has cheapest onions right now?",
            "query_type": "comparison",
            "success": True,
            "result_count": 3,
            "execution_time_ms": 245,
            "queried_at": "2024-01-15T10:30:00Z",
        },
        {
            "id": 2,
            "query": "Show products with 30%+ discount on Blinkit",
            "query_type": "search",
            "success": True,
            "result_count": 15,
            "execution_time_ms": 189,
            "queried_at": "2024-01-15T09:15:00Z",
        }
    ]
    
    return {
        "queries": queries[offset:offset + limit],
        "total_count": len(queries),
        "limit": limit,
        "offset": offset,
    }

@router.get("/alerts", summary="Get user price alerts")
async def get_user_alerts(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get user's price alerts."""
    # Mock price alerts
    alerts = [
        {
            "id": 1,
            "product_name": "Fresh Onions",
            "target_price": 40.0,
            "current_price": 45.0,
            "platform": "Blinkit",
            "alert_type": "below_price",
            "is_active": True,
            "created_at": "2024-01-10T08:00:00Z",
        },
        {
            "id": 2,
            "product_name": "Organic Tomatoes",
            "target_price": 30.0,
            "current_price": 35.0,
            "platform": "Zepto",
            "alert_type": "below_price",
            "is_active": True,
            "created_at": "2024-01-12T14:30:00Z",
        }
    ]
    
    return {"alerts": alerts}

@router.get("/favorites", summary="Get user favorite products")
async def get_user_favorites(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get user's favorite products."""
    # Mock favorite products
    favorites = [
        {
            "product_id": 1,
            "product_name": "Fresh Onions",
            "image_url": "/images/onions.jpg",
            "current_best_price": 45.0,
            "platform": "Blinkit",
            "added_at": "2024-01-10T08:00:00Z",
        },
        {
            "product_id": 2,
            "product_name": "Organic Tomatoes",
            "image_url": "/images/tomatoes.jpg",
            "current_best_price": 35.0,
            "platform": "Zepto",
            "added_at": "2024-01-12T14:30:00Z",
        }
    ]
    
    return {"favorites": favorites} 