"""Monitoring API endpoints for the price comparison platform."""

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from ...database.base import get_db
from ...services.monitoring_service import MonitoringService

router = APIRouter()

@router.get("/health", summary="Health check")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Get system health status."""
    service = MonitoringService(db)
    return await service.get_health_status()

@router.get("/metrics", summary="Prometheus metrics")
async def prometheus_metrics():
    """Get Prometheus metrics."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@router.get("/system", summary="System metrics")
async def system_metrics(db: AsyncSession = Depends(get_db)):
    """Get current system metrics."""
    service = MonitoringService(db)
    return await service.collect_system_metrics()

@router.get("/performance", summary="Performance metrics")
async def performance_metrics(time_period: str = "1h", db: AsyncSession = Depends(get_db)):
    """Get comprehensive performance metrics."""
    service = MonitoringService(db)
    return await service.get_performance_metrics(time_period)

@router.get("/database", summary="Database metrics")
async def database_metrics(time_period: str = "1h", db: AsyncSession = Depends(get_db)):
    """Get database performance metrics."""
    service = MonitoringService(db)
    return await service.get_database_metrics(time_period)

@router.get("/cache", summary="Cache metrics")
async def cache_metrics(db: AsyncSession = Depends(get_db)):
    """Get Redis cache metrics."""
    service = MonitoringService(db)
    return await service.get_cache_metrics() 