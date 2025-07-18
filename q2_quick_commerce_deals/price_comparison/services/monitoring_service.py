"""Monitoring service for the price comparison platform."""

import time
import psutil
import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.exc import SQLAlchemyError

from ..core.logging import get_logger
from ..database.models.monitoring import SystemMetrics, DatabaseMetrics, CacheMetrics, QueryMetrics
from ..services.cache_service import CacheService

logger = get_logger(__name__)


class MonitoringService:
    """Service for system monitoring and metrics collection."""
    
    def __init__(self, db: AsyncSession):
        """Initialize monitoring service."""
        self.db = db
        self.cache_service = CacheService()
    
    async def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_load = psutil.getloadavg()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics
            network = psutil.net_io_counters()
            
            metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "cpu": {
                    "usage_percent": cpu_percent,
                    "count": cpu_count,
                    "load_1min": cpu_load[0],
                    "load_5min": cpu_load[1],
                    "load_15min": cpu_load[2],
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "usage_percent": memory.percent,
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "available_gb": round(disk.free / (1024**3), 2),
                    "usage_percent": round((disk.used / disk.total) * 100, 2),
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv,
                },
            }
            
            # Store metrics in database
            await self._store_system_metrics(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error("Failed to collect system metrics", error=str(e))
            return {}
    
    async def get_database_metrics(self, time_period: str = "1h") -> Dict[str, Any]:
        """Get database performance metrics."""
        try:
            time_filter = self._get_time_filter(time_period)
            
            # Get query performance metrics
            query_result = await self.db.execute(
                select(
                    func.count(QueryMetrics.id).label("total_queries"),
                    func.avg(QueryMetrics.avg_execution_time_ms).label("avg_execution_time"),
                    func.sum(QueryMetrics.cache_hits).label("total_cache_hits"),
                    func.sum(QueryMetrics.cache_misses).label("total_cache_misses"),
                    func.avg(QueryMetrics.success_rate).label("avg_success_rate"),
                ).where(
                    QueryMetrics.last_updated >= time_filter
                )
            )
            
            query_stats = query_result.fetchone()
            
            # Get database connection metrics
            db_metrics = {
                "total_queries": query_stats[0] or 0,
                "avg_execution_time_ms": float(query_stats[1]) if query_stats[1] else 0,
                "cache_hit_rate": (
                    query_stats[2] / (query_stats[2] + query_stats[3]) * 100
                    if query_stats[2] and query_stats[3] and (query_stats[2] + query_stats[3]) > 0
                    else 0
                ),
                "success_rate": float(query_stats[4]) if query_stats[4] else 0,
            }
            
            return db_metrics
            
        except Exception as e:
            logger.error("Failed to get database metrics", error=str(e))
            return {}
    
    async def get_cache_metrics(self) -> Dict[str, Any]:
        """Get Redis cache metrics."""
        try:
            cache_stats = await self.cache_service.get_cache_stats()
            
            # Calculate additional metrics
            hit_rate = (
                cache_stats.get("keyspace_hits", 0) /
                (cache_stats.get("keyspace_hits", 0) + cache_stats.get("keyspace_misses", 0)) * 100
                if (cache_stats.get("keyspace_hits", 0) + cache_stats.get("keyspace_misses", 0)) > 0
                else 0
            )
            
            return {
                "connected_clients": cache_stats.get("connected_clients", 0),
                "used_memory": cache_stats.get("used_memory_human", "0B"),
                "total_commands": cache_stats.get("total_commands_processed", 0),
                "hit_rate_percent": round(hit_rate, 2),
                "keyspace_hits": cache_stats.get("keyspace_hits", 0),
                "keyspace_misses": cache_stats.get("keyspace_misses", 0),
                "uptime_seconds": cache_stats.get("uptime_in_seconds", 0),
            }
            
        except Exception as e:
            logger.error("Failed to get cache metrics", error=str(e))
            return {}
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status."""
        try:
            # Check database health
            db_healthy = await self._check_database_health()
            
            # Check cache health
            cache_healthy = await self.cache_service.health_check()
            
            # Check system resources
            system_healthy = await self._check_system_health()
            
            # Determine overall health
            overall_health = "healthy"
            if not db_healthy or not cache_healthy or not system_healthy:
                overall_health = "unhealthy"
            elif not (db_healthy and cache_healthy and system_healthy):
                overall_health = "degraded"
            
            return {
                "status": overall_health,
                "timestamp": datetime.utcnow().isoformat(),
                "components": {
                    "database": "healthy" if db_healthy else "unhealthy",
                    "cache": "healthy" if cache_healthy else "unhealthy",
                    "system": "healthy" if system_healthy else "unhealthy",
                },
                "details": {
                    "database_healthy": db_healthy,
                    "cache_healthy": cache_healthy,
                    "system_healthy": system_healthy,
                },
            }
            
        except Exception as e:
            logger.error("Failed to get health status", error=str(e))
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
            }
    
    async def get_performance_metrics(self, time_period: str = "1h") -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        try:
            time_filter = self._get_time_filter(time_period)
            
            # Get system metrics
            system_metrics = await self.collect_system_metrics()
            
            # Get database metrics
            db_metrics = await self.get_database_metrics(time_period)
            
            # Get cache metrics
            cache_metrics = await self.get_cache_metrics()
            
            # Get health status
            health_status = await self.get_health_status()
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "time_period": time_period,
                "system": system_metrics,
                "database": db_metrics,
                "cache": cache_metrics,
                "health": health_status,
            }
            
        except Exception as e:
            logger.error("Failed to get performance metrics", error=str(e))
            return {}
    
    async def _store_system_metrics(self, metrics: Dict[str, Any]) -> None:
        """Store system metrics in database."""
        try:
            system_metrics = SystemMetrics(
                hostname=psutil.gethostname(),
                service_name="price_comparison_api",
                cpu_usage_percent=metrics["cpu"]["usage_percent"],
                cpu_count=metrics["cpu"]["count"],
                cpu_load_1min=metrics["cpu"]["load_1min"],
                cpu_load_5min=metrics["cpu"]["load_5min"],
                cpu_load_15min=metrics["cpu"]["load_15min"],
                memory_total_gb=metrics["memory"]["total_gb"],
                memory_used_gb=metrics["memory"]["used_gb"],
                memory_available_gb=metrics["memory"]["available_gb"],
                memory_usage_percent=metrics["memory"]["usage_percent"],
                disk_total_gb=metrics["disk"]["total_gb"],
                disk_used_gb=metrics["disk"]["used_gb"],
                disk_available_gb=metrics["disk"]["available_gb"],
                disk_usage_percent=metrics["disk"]["usage_percent"],
                network_bytes_sent=metrics["network"]["bytes_sent"],
                network_bytes_recv=metrics["network"]["bytes_recv"],
            )
            
            self.db.add(system_metrics)
            await self.db.commit()
            
        except Exception as e:
            logger.error("Failed to store system metrics", error=str(e))
            await self.db.rollback()
    
    async def _check_database_health(self) -> bool:
        """Check database health."""
        try:
            # Simple health check query
            result = await self.db.execute(select(1))
            result.fetchone()
            return True
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return False
    
    async def _check_system_health(self) -> bool:
        """Check system resource health."""
        try:
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                return False
            
            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                return False
            
            # Check disk usage
            disk = psutil.disk_usage('/')
            if (disk.used / disk.total) * 100 > 90:
                return False
            
            return True
            
        except Exception as e:
            logger.error("System health check failed", error=str(e))
            return False
    
    def _get_time_filter(self, time_period: str) -> datetime:
        """Get time filter based on period."""
        now = datetime.utcnow()
        
        if time_period == "1h":
            return now - timedelta(hours=1)
        elif time_period == "24h":
            return now - timedelta(hours=24)
        elif time_period == "7d":
            return now - timedelta(days=7)
        else:
            return now - timedelta(hours=1) 