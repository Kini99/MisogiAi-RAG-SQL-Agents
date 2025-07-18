"""Analytics API endpoints for the price comparison platform."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ...database.base import get_db
from ...services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/dashboard", summary="Get dashboard analytics")
async def dashboard_analytics(time_period: str = "24h", db: AsyncSession = Depends(get_db)):
    service = AnalyticsService(db)
    return await service.get_dashboard_analytics(time_period)

@router.get("/price-trends", summary="Get price trends")
async def price_trends(
    product_id: int = None,
    category_id: int = None,
    platform_id: int = None,
    time_period: str = "7d",
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    return await service.get_price_trends(product_id, category_id, platform_id, time_period)

@router.get("/search", summary="Get search analytics")
async def search_analytics(time_period: str = "24h", db: AsyncSession = Depends(get_db)):
    service = AnalyticsService(db)
    return await service.get_search_analytics(time_period)

@router.get("/platform-comparison", summary="Get platform comparison analytics")
async def platform_comparison(time_period: str = "24h", db: AsyncSession = Depends(get_db)):
    service = AnalyticsService(db)
    return await service.get_platform_comparison(time_period)

@router.get("/user-behavior", summary="Get user behavior analytics")
async def user_behavior(time_period: str = "24h", db: AsyncSession = Depends(get_db)):
    service = AnalyticsService(db)
    return await service.get_user_behavior_analytics(time_period) 