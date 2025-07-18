"""Platform service for the price comparison platform."""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.exc import SQLAlchemyError

from ..core.logging import get_logger
from ..database.models.core import Platform
from ..database.models.platforms import PlatformProduct, PlatformMetadata
from ..database.models.pricing import Price
from ..database.models.availability import Availability
from .cache_service import CacheService

logger = get_logger(__name__)


class PlatformService:
    """Service for managing platform data and integrations."""
    
    def __init__(self, db: AsyncSession):
        """Initialize platform service."""
        self.db = db
        self.cache_service = CacheService()
    
    async def get_all_platforms(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all platforms."""
        try:
            cache_key = f"platforms:all:{active_only}"
            cached_result = await self.cache_service.get(cache_key)
            
            if cached_result:
                return cached_result
            
            query = select(Platform)
            if active_only:
                query = query.where(Platform.is_active == True)
            
            query = query.order_by(Platform.priority.desc(), Platform.name)
            result = await self.db.execute(query)
            platforms = result.scalars().all()
            
            platform_data = []
            for platform in platforms:
                platform_data.append({
                    "id": platform.id,
                    "name": platform.name,
                    "display_name": platform.display_name,
                    "slug": platform.slug,
                    "description": platform.description,
                    "logo_url": platform.logo_url,
                    "website_url": platform.website_url,
                    "is_active": platform.is_active,
                    "priority": platform.priority,
                    "metadata": platform.metadata,
                    "created_at": platform.created_at.isoformat(),
                    "updated_at": platform.updated_at.isoformat(),
                })
            
            # Cache the result
            await self.cache_service.set(cache_key, platform_data, ttl=3600)
            
            return platform_data
            
        except Exception as e:
            logger.error("Failed to get platforms", error=str(e))
            return []
    
    async def get_platform_by_id(self, platform_id: int) -> Optional[Dict[str, Any]]:
        """Get platform by ID."""
        try:
            cache_key = f"platform:{platform_id}"
            cached_result = await self.cache_service.get(cache_key)
            
            if cached_result:
                return cached_result
            
            result = await self.db.execute(
                select(Platform).where(Platform.id == platform_id)
            )
            platform = result.scalar_one_or_none()
            
            if not platform:
                return None
            
            platform_data = {
                "id": platform.id,
                "name": platform.name,
                "display_name": platform.display_name,
                "slug": platform.slug,
                "description": platform.description,
                "logo_url": platform.logo_url,
                "website_url": platform.website_url,
                "is_active": platform.is_active,
                "priority": platform.priority,
                "metadata": platform.metadata,
                "created_at": platform.created_at.isoformat(),
                "updated_at": platform.updated_at.isoformat(),
            }
            
            # Cache the result
            await self.cache_service.set(cache_key, platform_data, ttl=3600)
            
            return platform_data
            
        except Exception as e:
            logger.error("Failed to get platform by ID", platform_id=platform_id, error=str(e))
            return None
    
    async def get_platform_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get platform by slug."""
        try:
            cache_key = f"platform:slug:{slug}"
            cached_result = await self.cache_service.get(cache_key)
            
            if cached_result:
                return cached_result
            
            result = await self.db.execute(
                select(Platform).where(Platform.slug == slug)
            )
            platform = result.scalar_one_or_none()
            
            if not platform:
                return None
            
            platform_data = {
                "id": platform.id,
                "name": platform.name,
                "display_name": platform.display_name,
                "slug": platform.slug,
                "description": platform.description,
                "logo_url": platform.logo_url,
                "website_url": platform.website_url,
                "is_active": platform.is_active,
                "priority": platform.priority,
                "metadata": platform.metadata,
                "created_at": platform.created_at.isoformat(),
                "updated_at": platform.updated_at.isoformat(),
            }
            
            # Cache the result
            await self.cache_service.set(cache_key, platform_data, ttl=3600)
            
            return platform_data
            
        except Exception as e:
            logger.error("Failed to get platform by slug", slug=slug, error=str(e))
            return None
    
    async def get_platform_products(
        self,
        platform_id: int,
        limit: int = 100,
        offset: int = 0,
        active_only: bool = True,
    ) -> List[Dict[str, Any]]:
        """Get products for a specific platform."""
        try:
            cache_key = f"platform_products:{platform_id}:{limit}:{offset}:{active_only}"
            cached_result = await self.cache_service.get(cache_key)
            
            if cached_result:
                return cached_result
            
            query = select(PlatformProduct).where(PlatformProduct.platform_id == platform_id)
            
            if active_only:
                query = query.where(PlatformProduct.is_active == True)
            
            query = query.limit(limit).offset(offset)
            result = await self.db.execute(query)
            platform_products = result.scalars().all()
            
            products_data = []
            for pp in platform_products:
                products_data.append({
                    "id": pp.id,
                    "platform_id": pp.platform_id,
                    "product_id": pp.product_id,
                    "platform_product_id": pp.platform_product_id,
                    "platform_sku": pp.platform_sku,
                    "platform_barcode": pp.platform_barcode,
                    "platform_name": pp.platform_name,
                    "platform_description": pp.platform_description,
                    "platform_url": pp.platform_url,
                    "platform_images": pp.platform_images,
                    "is_active": pp.is_active,
                    "is_verified": pp.is_verified,
                    "confidence_score": pp.confidence_score,
                    "last_synced": pp.last_synced.isoformat(),
                    "sync_status": pp.sync_status,
                })
            
            # Cache the result
            await self.cache_service.set(cache_key, products_data, ttl=1800)
            
            return products_data
            
        except Exception as e:
            logger.error("Failed to get platform products", platform_id=platform_id, error=str(e))
            return []
    
    async def get_platform_metadata(self, platform_id: int) -> Optional[Dict[str, Any]]:
        """Get platform metadata and configuration."""
        try:
            cache_key = f"platform_metadata:{platform_id}"
            cached_result = await self.cache_service.get(cache_key)
            
            if cached_result:
                return cached_result
            
            result = await self.db.execute(
                select(PlatformMetadata).where(PlatformMetadata.platform_id == platform_id)
            )
            metadata = result.scalar_one_or_none()
            
            if not metadata:
                return None
            
            metadata_data = {
                "id": metadata.id,
                "platform_id": metadata.platform_id,
                "api_config": metadata.api_config,
                "scraping_config": metadata.scraping_config,
                "rate_limits": metadata.rate_limits,
                "supports_real_time_pricing": metadata.supports_real_time_pricing,
                "supports_inventory_tracking": metadata.supports_inventory_tracking,
                "supports_delivery_slots": metadata.supports_delivery_slots,
                "supports_coupons": metadata.supports_coupons,
                "data_freshness_threshold": metadata.data_freshness_threshold,
                "sync_frequency": metadata.sync_frequency,
                "last_successful_sync": metadata.last_successful_sync.isoformat() if metadata.last_successful_sync else None,
                "last_error": metadata.last_error,
                "error_count": metadata.error_count,
                "consecutive_failures": metadata.consecutive_failures,
                "avg_response_time": metadata.avg_response_time,
                "success_rate": metadata.success_rate,
                "total_requests": metadata.total_requests,
                "successful_requests": metadata.successful_requests,
                "is_active": metadata.is_active,
                "is_healthy": metadata.is_healthy,
            }
            
            # Cache the result
            await self.cache_service.set(cache_key, metadata_data, ttl=1800)
            
            return metadata_data
            
        except Exception as e:
            logger.error("Failed to get platform metadata", platform_id=platform_id, error=str(e))
            return None
    
    async def get_platform_analytics(self, platform_id: int, time_period: str = "24h") -> Dict[str, Any]:
        """Get analytics for a specific platform."""
        try:
            cache_key = f"platform_analytics:{platform_id}:{time_period}"
            cached_result = await self.cache_service.get(cache_key)
            
            if cached_result:
                return cached_result
            
            # Calculate time filter
            now = datetime.utcnow()
            if time_period == "24h":
                time_filter = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_period == "7d":
                time_filter = now - timedelta(days=7)
            elif time_period == "30d":
                time_filter = now - timedelta(days=30)
            else:
                time_filter = now - timedelta(hours=24)
            
            # Get price analytics
            price_result = await self.db.execute(
                select(
                    func.count(Price.id).label("total_prices"),
                    func.avg(Price.selling_price).label("avg_price"),
                    func.min(Price.selling_price).label("min_price"),
                    func.max(Price.selling_price).label("max_price"),
                    func.avg(Price.discount_percentage).label("avg_discount"),
                ).where(
                    and_(
                        Price.platform_id == platform_id,
                        Price.is_active == True,
                        Price.updated_at >= time_filter,
                    )
                )
            )
            price_stats = price_result.fetchone()
            
            # Get availability analytics
            availability_result = await self.db.execute(
                select(
                    func.count(Availability.id).label("total_products"),
                    func.count(Availability.id).filter(Availability.is_available == True).label("available_products"),
                    func.count(Availability.id).filter(Availability.is_available == False).label("unavailable_products"),
                ).where(
                    and_(
                        Availability.platform_id == platform_id,
                        Availability.updated_at >= time_filter,
                    )
                )
            )
            availability_stats = availability_result.fetchone()
            
            analytics = {
                "platform_id": platform_id,
                "time_period": time_period,
                "prices": {
                    "total_prices": price_stats[0] or 0,
                    "avg_price": float(price_stats[1]) if price_stats[1] else 0,
                    "min_price": float(price_stats[2]) if price_stats[2] else 0,
                    "max_price": float(price_stats[3]) if price_stats[3] else 0,
                    "avg_discount": float(price_stats[4]) if price_stats[4] else 0,
                },
                "availability": {
                    "total_products": availability_stats[0] or 0,
                    "available_products": availability_stats[1] or 0,
                    "unavailable_products": availability_stats[2] or 0,
                    "availability_rate": (
                        (availability_stats[1] / availability_stats[0] * 100)
                        if availability_stats[0] and availability_stats[0] > 0
                        else 0
                    ),
                },
            }
            
            # Cache the result
            await self.cache_service.set(cache_key, analytics, ttl=1800)
            
            return analytics
            
        except Exception as e:
            logger.error("Failed to get platform analytics", platform_id=platform_id, error=str(e))
            return {}
    
    async def search_platforms(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search platforms by name or description."""
        try:
            cache_key = f"platform_search:{query}:{limit}"
            cached_result = await self.cache_service.get(cache_key)
            
            if cached_result:
                return cached_result
            
            search_query = select(Platform).where(
                and_(
                    Platform.is_active == True,
                    or_(
                        Platform.name.ilike(f"%{query}%"),
                        Platform.display_name.ilike(f"%{query}%"),
                        Platform.description.ilike(f"%{query}%"),
                    ),
                )
            ).limit(limit)
            
            result = await self.db.execute(search_query)
            platforms = result.scalars().all()
            
            platform_data = []
            for platform in platforms:
                platform_data.append({
                    "id": platform.id,
                    "name": platform.name,
                    "display_name": platform.display_name,
                    "slug": platform.slug,
                    "description": platform.description,
                    "logo_url": platform.logo_url,
                    "priority": platform.priority,
                })
            
            # Cache the result
            await self.cache_service.set(cache_key, platform_data, ttl=1800)
            
            return platform_data
            
        except Exception as e:
            logger.error("Failed to search platforms", query=query, error=str(e))
            return []
    
    async def get_platform_health_status(self) -> List[Dict[str, Any]]:
        """Get health status for all platforms."""
        try:
            cache_key = "platform_health"
            cached_result = await self.cache_service.get(cache_key)
            
            if cached_result:
                return cached_result
            
            # Get all platforms with their metadata
            result = await self.db.execute(
                select(Platform, PlatformMetadata).outerjoin(
                    PlatformMetadata, Platform.id == PlatformMetadata.platform_id
                ).where(Platform.is_active == True)
            )
            
            health_status = []
            for platform, metadata in result.fetchall():
                status = {
                    "platform_id": platform.id,
                    "platform_name": platform.name,
                    "platform_slug": platform.slug,
                    "is_active": platform.is_active,
                    "is_healthy": metadata.is_healthy if metadata else True,
                    "last_successful_sync": metadata.last_successful_sync.isoformat() if metadata and metadata.last_successful_sync else None,
                    "error_count": metadata.error_count if metadata else 0,
                    "consecutive_failures": metadata.consecutive_failures if metadata else 0,
                    "success_rate": metadata.success_rate if metadata else 100.0,
                    "avg_response_time": metadata.avg_response_time if metadata else 0,
                }
                
                # Determine overall health
                if not platform.is_active:
                    status["overall_status"] = "inactive"
                elif metadata and not metadata.is_healthy:
                    status["overall_status"] = "unhealthy"
                elif metadata and metadata.consecutive_failures > 5:
                    status["overall_status"] = "degraded"
                else:
                    status["overall_status"] = "healthy"
                
                health_status.append(status)
            
            # Cache the result
            await self.cache_service.set(cache_key, health_status, ttl=900)  # 15 minutes
            
            return health_status
            
        except Exception as e:
            logger.error("Failed to get platform health status", error=str(e))
            return []
    
    async def update_platform_metadata(
        self,
        platform_id: int,
        metadata_updates: Dict[str, Any],
    ) -> bool:
        """Update platform metadata."""
        try:
            result = await self.db.execute(
                select(PlatformMetadata).where(PlatformMetadata.platform_id == platform_id)
            )
            metadata = result.scalar_one_or_none()
            
            if not metadata:
                # Create new metadata record
                metadata = PlatformMetadata(platform_id=platform_id)
                self.db.add(metadata)
            
            # Update fields
            for key, value in metadata_updates.items():
                if hasattr(metadata, key):
                    setattr(metadata, key, value)
            
            await self.db.commit()
            
            # Invalidate cache
            await self.cache_service.delete(f"platform_metadata:{platform_id}")
            await self.cache_service.delete("platform_health")
            
            logger.info("Platform metadata updated", platform_id=platform_id)
            return True
            
        except Exception as e:
            logger.error("Failed to update platform metadata", platform_id=platform_id, error=str(e))
            await self.db.rollback()
            return False 