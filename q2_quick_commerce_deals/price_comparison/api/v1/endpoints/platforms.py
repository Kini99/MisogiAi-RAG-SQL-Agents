"""Platforms API endpoints for the price comparison platform."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ...database.base import get_db
from ...services.platform_service import PlatformService

router = APIRouter()

@router.get("/", summary="List all platforms")
async def list_platforms(active_only: bool = True, db: AsyncSession = Depends(get_db)):
    service = PlatformService(db)
    return await service.get_all_platforms(active_only=active_only)

@router.get("/{platform_id}", summary="Get platform details")
async def get_platform(platform_id: int, db: AsyncSession = Depends(get_db)):
    service = PlatformService(db)
    platform = await service.get_platform_by_id(platform_id)
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    return platform

@router.get("/{platform_id}/products", summary="Get products for a platform")
async def get_platform_products(platform_id: int, limit: int = 100, offset: int = 0, active_only: bool = True, db: AsyncSession = Depends(get_db)):
    service = PlatformService(db)
    return await service.get_platform_products(platform_id, limit, offset, active_only)

@router.get("/{platform_id}/analytics", summary="Get platform analytics")
async def get_platform_analytics(platform_id: int, time_period: str = "24h", db: AsyncSession = Depends(get_db)):
    service = PlatformService(db)
    return await service.get_platform_analytics(platform_id, time_period)

@router.get("/search", summary="Search platforms")
async def search_platforms(q: str, limit: int = 10, db: AsyncSession = Depends(get_db)):
    service = PlatformService(db)
    return await service.search_platforms(q, limit)

@router.get("/health", summary="Get platform health status")
async def get_platform_health(db: AsyncSession = Depends(get_db)):
    service = PlatformService(db)
    return await service.get_platform_health_status() 