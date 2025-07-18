"""Analytics service for the price comparison platform."""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc, text
from sqlalchemy.exc import SQLAlchemyError

from ..core.logging import get_logger
from ..database.models.analytics import QueryLog, QueryResult, QueryPerformance, SearchAnalytics, PriceAnalytics
from ..database.models.pricing import Price, PriceHistory
from ..database.models.core import Product, Platform, Category
from ..database.models.users import UserQuery, UserSearch
from .cache_service import CacheService

logger = get_logger(__name__)


class AnalyticsService:
    """Service for handling data analytics and insights."""
    
    def __init__(self, db: AsyncSession):
        """Initialize analytics service."""
        self.db = db
        self.cache_service = CacheService()
    
    async def get_dashboard_analytics(self, time_period: str = "24h") -> Dict[str, Any]:
        """Get comprehensive dashboard analytics."""
        try:
            cache_key = f"dashboard_analytics:{time_period}"
            cached_result = await self.cache_service.get(cache_key)
            
            if cached_result:
                return cached_result
            
            # Calculate time filter
            time_filter = self._get_time_filter(time_period)
            
            # Get query analytics
            query_analytics = await self._get_query_analytics(time_filter)
            
            # Get price analytics
            price_analytics = await self._get_price_analytics(time_filter)
            
            # Get platform analytics
            platform_analytics = await self._get_platform_analytics(time_filter)
            
            # Get user analytics
            user_analytics = await self._get_user_analytics(time_filter)
            
            # Get trending products
            trending_products = await self._get_trending_products(time_filter)
            
            # Get best deals
            best_deals = await self._get_best_deals_analytics(time_filter)
            
            dashboard_data = {
                "time_period": time_period,
                "query_analytics": query_analytics,
                "price_analytics": price_analytics,
                "platform_analytics": platform_analytics,
                "user_analytics": user_analytics,
                "trending_products": trending_products,
                "best_deals": best_deals,
                "generated_at": datetime.utcnow().isoformat(),
            }
            
            # Cache the result
            await self.cache_service.set(cache_key, dashboard_data, ttl=1800)
            
            return dashboard_data
            
        except Exception as e:
            logger.error("Failed to get dashboard analytics", error=str(e))
            return {}
    
    async def get_price_trends(
        self,
        product_id: Optional[int] = None,
        category_id: Optional[int] = None,
        platform_id: Optional[int] = None,
        time_period: str = "7d",
    ) -> Dict[str, Any]:
        """Get price trends for products."""
        try:
            cache_key = f"price_trends:{product_id}:{category_id}:{platform_id}:{time_period}"
            cached_result = await self.cache_service.get(cache_key)
            
            if cached_result:
                return cached_result
            
            time_filter = self._get_time_filter(time_period)
            
            # Build query
            query = select(
                PriceHistory.product_id,
                PriceHistory.platform_id,
                PriceHistory.selling_price,
                PriceHistory.recorded_at,
                Product.name.label("product_name"),
                Platform.name.label("platform_name"),
            ).join(
                Product, PriceHistory.product_id == Product.id
            ).join(
                Platform, PriceHistory.platform_id == Platform.id
            ).where(
                PriceHistory.recorded_at >= time_filter
            )
            
            # Add filters
            if product_id:
                query = query.where(PriceHistory.product_id == product_id)
            
            if category_id:
                query = query.join(Category, Product.category_id == Category.id)
                query = query.where(Category.id == category_id)
            
            if platform_id:
                query = query.where(PriceHistory.platform_id == platform_id)
            
            query = query.order_by(PriceHistory.recorded_at)
            
            result = await self.db.execute(query)
            price_history = result.fetchall()
            
            # Process data for trends
            trends_data = self._process_price_trends(price_history)
            
            # Cache the result
            await self.cache_service.set(cache_key, trends_data, ttl=3600)
            
            return trends_data
            
        except Exception as e:
            logger.error("Failed to get price trends", error=str(e))
            return {}
    
    async def get_search_analytics(self, time_period: str = "24h") -> Dict[str, Any]:
        """Get search and query analytics."""
        try:
            cache_key = f"search_analytics:{time_period}"
            cached_result = await self.cache_service.get(cache_key)
            
            if cached_result:
                return cached_result
            
            time_filter = self._get_time_filter(time_period)
            
            # Get popular searches
            popular_searches = await self._get_popular_searches(time_filter)
            
            # Get query performance
            query_performance = await self._get_query_performance(time_filter)
            
            # Get search patterns
            search_patterns = await self._get_search_patterns(time_filter)
            
            analytics = {
                "time_period": time_period,
                "popular_searches": popular_searches,
                "query_performance": query_performance,
                "search_patterns": search_patterns,
            }
            
            # Cache the result
            await self.cache_service.set(cache_key, analytics, ttl=1800)
            
            return analytics
            
        except Exception as e:
            logger.error("Failed to get search analytics", error=str(e))
            return {}
    
    async def get_platform_comparison(self, time_period: str = "24h") -> Dict[str, Any]:
        """Get platform comparison analytics."""
        try:
            cache_key = f"platform_comparison:{time_period}"
            cached_result = await self.cache_service.get(cache_key)
            
            if cached_result:
                return cached_result
            
            time_filter = self._get_time_filter(time_period)
            
            # Get platform statistics
            platform_stats = await self._get_platform_statistics(time_filter)
            
            # Get price competitiveness
            price_competitiveness = await self._get_price_competitiveness(time_filter)
            
            # Get availability comparison
            availability_comparison = await self._get_availability_comparison(time_filter)
            
            comparison_data = {
                "time_period": time_period,
                "platform_statistics": platform_stats,
                "price_competitiveness": price_competitiveness,
                "availability_comparison": availability_comparison,
            }
            
            # Cache the result
            await self.cache_service.set(cache_key, comparison_data, ttl=3600)
            
            return comparison_data
            
        except Exception as e:
            logger.error("Failed to get platform comparison", error=str(e))
            return {}
    
    async def get_user_behavior_analytics(self, time_period: str = "24h") -> Dict[str, Any]:
        """Get user behavior analytics."""
        try:
            cache_key = f"user_behavior:{time_period}"
            cached_result = await self.cache_service.get(cache_key)
            
            if cached_result:
                return cached_result
            
            time_filter = self._get_time_filter(time_period)
            
            # Get user search patterns
            search_patterns = await self._get_user_search_patterns(time_filter)
            
            # Get query success rates
            success_rates = await self._get_query_success_rates(time_filter)
            
            # Get user engagement
            engagement = await self._get_user_engagement(time_filter)
            
            behavior_data = {
                "time_period": time_period,
                "search_patterns": search_patterns,
                "success_rates": success_rates,
                "engagement": engagement,
            }
            
            # Cache the result
            await self.cache_service.set(cache_key, behavior_data, ttl=1800)
            
            return behavior_data
            
        except Exception as e:
            logger.error("Failed to get user behavior analytics", error=str(e))
            return {}
    
    def _get_time_filter(self, time_period: str) -> datetime:
        """Get time filter based on period."""
        now = datetime.utcnow()
        
        if time_period == "1h":
            return now - timedelta(hours=1)
        elif time_period == "24h":
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_period == "7d":
            return now - timedelta(days=7)
        elif time_period == "30d":
            return now - timedelta(days=30)
        else:
            return now - timedelta(hours=24)
    
    async def _get_query_analytics(self, time_filter: datetime) -> Dict[str, Any]:
        """Get query analytics for the time period."""
        try:
            # Total queries
            total_queries_result = await self.db.execute(
                select(func.count(UserQuery.id)).where(UserQuery.queried_at >= time_filter)
            )
            total_queries = total_queries_result.scalar() or 0
            
            # Successful queries
            successful_queries_result = await self.db.execute(
                select(func.count(UserQuery.id)).where(
                    and_(
                        UserQuery.queried_at >= time_filter,
                        UserQuery.success == True,
                    )
                )
            )
            successful_queries = successful_queries_result.scalar() or 0
            
            # Average execution time
            avg_execution_result = await self.db.execute(
                select(func.avg(UserQuery.execution_time_ms)).where(
                    and_(
                        UserQuery.queried_at >= time_filter,
                        UserQuery.success == True,
                    )
                )
            )
            avg_execution_time = float(avg_execution_result.scalar() or 0)
            
            # Query types distribution
            query_types_result = await self.db.execute(
                select(
                    UserQuery.query_type,
                    func.count(UserQuery.id).label("count")
                ).where(
                    UserQuery.queried_at >= time_filter
                ).group_by(
                    UserQuery.query_type
                ).order_by(
                    desc(func.count(UserQuery.id))
                )
            )
            query_types = [
                {"type": row[0], "count": row[1]}
                for row in query_types_result.fetchall()
            ]
            
            return {
                "total_queries": total_queries,
                "successful_queries": successful_queries,
                "success_rate": (successful_queries / total_queries * 100) if total_queries > 0 else 0,
                "avg_execution_time_ms": avg_execution_time,
                "query_types": query_types,
            }
            
        except Exception as e:
            logger.error("Failed to get query analytics", error=str(e))
            return {}
    
    async def _get_price_analytics(self, time_filter: datetime) -> Dict[str, Any]:
        """Get price analytics for the time period."""
        try:
            # Price statistics
            price_stats_result = await self.db.execute(
                select(
                    func.count(Price.id).label("total_prices"),
                    func.avg(Price.selling_price).label("avg_price"),
                    func.avg(Price.discount_percentage).label("avg_discount"),
                    func.count(Price.id).filter(Price.discount_percentage > 0).label("discounted_products"),
                ).where(
                    Price.updated_at >= time_filter
                )
            )
            price_stats = price_stats_result.fetchone()
            
            # Price changes
            price_changes_result = await self.db.execute(
                select(
                    func.count(PriceHistory.id).label("total_changes"),
                    func.count(PriceHistory.id).filter(PriceHistory.price_change > 0).label("price_increases"),
                    func.count(PriceHistory.id).filter(PriceHistory.price_change < 0).label("price_decreases"),
                ).where(
                    PriceHistory.recorded_at >= time_filter
                )
            )
            price_changes = price_changes_result.fetchone()
            
            return {
                "total_prices": price_stats[0] or 0,
                "avg_price": float(price_stats[1]) if price_stats[1] else 0,
                "avg_discount": float(price_stats[2]) if price_stats[2] else 0,
                "discounted_products": price_stats[3] or 0,
                "price_changes": {
                    "total": price_changes[0] or 0,
                    "increases": price_changes[1] or 0,
                    "decreases": price_changes[2] or 0,
                },
            }
            
        except Exception as e:
            logger.error("Failed to get price analytics", error=str(e))
            return {}
    
    async def _get_platform_analytics(self, time_filter: datetime) -> Dict[str, Any]:
        """Get platform analytics for the time period."""
        try:
            # Platform statistics
            platform_stats_result = await self.db.execute(
                select(
                    Platform.name,
                    func.count(Price.id).label("product_count"),
                    func.avg(Price.selling_price).label("avg_price"),
                    func.avg(Price.discount_percentage).label("avg_discount"),
                ).join(
                    Price, Platform.id == Price.platform_id
                ).where(
                    Price.updated_at >= time_filter
                ).group_by(
                    Platform.id, Platform.name
                ).order_by(
                    desc(func.count(Price.id))
                )
            )
            
            platform_stats = []
            for row in platform_stats_result.fetchall():
                platform_stats.append({
                    "platform_name": row[0],
                    "product_count": row[1],
                    "avg_price": float(row[2]) if row[2] else 0,
                    "avg_discount": float(row[3]) if row[3] else 0,
                })
            
            return {
                "platform_statistics": platform_stats,
            }
            
        except Exception as e:
            logger.error("Failed to get platform analytics", error=str(e))
            return {}
    
    async def _get_user_analytics(self, time_filter: datetime) -> Dict[str, Any]:
        """Get user analytics for the time period."""
        try:
            # User activity
            user_activity_result = await self.db.execute(
                select(
                    func.count(UserQuery.user_id.distinct()).label("active_users"),
                    func.count(UserQuery.id).label("total_queries"),
                    func.avg(UserQuery.rating).label("avg_rating"),
                ).where(
                    UserQuery.queried_at >= time_filter
                )
            )
            user_activity = user_activity_result.fetchone()
            
            return {
                "active_users": user_activity[0] or 0,
                "total_queries": user_activity[1] or 0,
                "avg_rating": float(user_activity[2]) if user_activity[2] else 0,
                "queries_per_user": (
                    user_activity[1] / user_activity[0]
                    if user_activity[0] and user_activity[0] > 0
                    else 0
                ),
            }
            
        except Exception as e:
            logger.error("Failed to get user analytics", error=str(e))
            return {}
    
    async def _get_trending_products(self, time_filter: datetime) -> List[Dict[str, Any]]:
        """Get trending products based on search frequency."""
        try:
            trending_result = await self.db.execute(
                select(
                    Product.id,
                    Product.name,
                    Product.image_url,
                    func.count(UserSearch.id).label("search_count"),
                ).join(
                    UserSearch, Product.name.ilike(f"%{UserSearch.query}%")
                ).where(
                    UserSearch.searched_at >= time_filter
                ).group_by(
                    Product.id, Product.name, Product.image_url
                ).order_by(
                    desc(func.count(UserSearch.id))
                ).limit(10)
            )
            
            trending_products = []
            for row in trending_result.fetchall():
                trending_products.append({
                    "product_id": row[0],
                    "product_name": row[1],
                    "image_url": row[2],
                    "search_count": row[3],
                })
            
            return trending_products
            
        except Exception as e:
            logger.error("Failed to get trending products", error=str(e))
            return []
    
    async def _get_best_deals_analytics(self, time_filter: datetime) -> List[Dict[str, Any]]:
        """Get best deals analytics."""
        try:
            deals_result = await self.db.execute(
                select(
                    Product.id,
                    Product.name,
                    Product.image_url,
                    Platform.name.label("platform_name"),
                    Price.selling_price,
                    Price.mrp,
                    Price.discount_percentage,
                ).join(
                    Price, Product.id == Price.product_id
                ).join(
                    Platform, Price.platform_id == Platform.id
                ).where(
                    and_(
                        Price.updated_at >= time_filter,
                        Price.discount_percentage >= 30,
                        Price.is_active == True,
                    )
                ).order_by(
                    desc(Price.discount_percentage)
                ).limit(10)
            )
            
            best_deals = []
            for row in deals_result.fetchall():
                best_deals.append({
                    "product_id": row[0],
                    "product_name": row[1],
                    "image_url": row[2],
                    "platform_name": row[3],
                    "selling_price": float(row[4]),
                    "mrp": float(row[5]),
                    "discount_percentage": row[6],
                })
            
            return best_deals
            
        except Exception as e:
            logger.error("Failed to get best deals analytics", error=str(e))
            return []
    
    def _process_price_trends(self, price_history: List) -> Dict[str, Any]:
        """Process price history data into trends."""
        try:
            # Group by date and calculate averages
            daily_prices = {}
            for record in price_history:
                date_key = record.recorded_at.date().isoformat()
                if date_key not in daily_prices:
                    daily_prices[date_key] = {
                        "prices": [],
                        "platforms": set(),
                        "products": set(),
                    }
                
                daily_prices[date_key]["prices"].append(float(record.selling_price))
                daily_prices[date_key]["platforms"].add(record.platform_name)
                daily_prices[date_key]["products"].add(record.product_name)
            
            # Calculate daily averages
            trends = []
            for date, data in sorted(daily_prices.items()):
                avg_price = sum(data["prices"]) / len(data["prices"])
                trends.append({
                    "date": date,
                    "avg_price": round(avg_price, 2),
                    "platform_count": len(data["platforms"]),
                    "product_count": len(data["products"]),
                })
            
            return {
                "trends": trends,
                "total_data_points": len(price_history),
                "date_range": {
                    "start": trends[0]["date"] if trends else None,
                    "end": trends[-1]["date"] if trends else None,
                },
            }
            
        except Exception as e:
            logger.error("Failed to process price trends", error=str(e))
            return {}
    
    async def _get_popular_searches(self, time_filter: datetime) -> List[Dict[str, Any]]:
        """Get popular searches for the time period."""
        try:
            popular_result = await self.db.execute(
                select(
                    UserSearch.query,
                    func.count(UserSearch.id).label("count"),
                ).where(
                    UserSearch.searched_at >= time_filter
                ).group_by(
                    UserSearch.query
                ).order_by(
                    desc(func.count(UserSearch.id))
                ).limit(20)
            )
            
            popular_searches = []
            for row in popular_result.fetchall():
                popular_searches.append({
                    "query": row[0],
                    "count": row[1],
                })
            
            return popular_searches
            
        except Exception as e:
            logger.error("Failed to get popular searches", error=str(e))
            return []
    
    async def _get_query_performance(self, time_filter: datetime) -> Dict[str, Any]:
        """Get query performance metrics."""
        try:
            performance_result = await self.db.execute(
                select(
                    func.avg(UserQuery.execution_time_ms).label("avg_time"),
                    func.min(UserQuery.execution_time_ms).label("min_time"),
                    func.max(UserQuery.execution_time_ms).label("max_time"),
                    func.count(UserQuery.id).filter(UserQuery.cache_hit == True).label("cache_hits"),
                    func.count(UserQuery.id).label("total_queries"),
                ).where(
                    UserQuery.queried_at >= time_filter
                )
            )
            
            performance = performance_result.fetchone()
            
            return {
                "avg_execution_time_ms": float(performance[0]) if performance[0] else 0,
                "min_execution_time_ms": float(performance[1]) if performance[1] else 0,
                "max_execution_time_ms": float(performance[2]) if performance[2] else 0,
                "cache_hit_rate": (
                    performance[3] / performance[4] * 100
                    if performance[4] and performance[4] > 0
                    else 0
                ),
                "total_queries": performance[4] or 0,
            }
            
        except Exception as e:
            logger.error("Failed to get query performance", error=str(e))
            return {}
    
    async def _get_search_patterns(self, time_filter: datetime) -> Dict[str, Any]:
        """Get search patterns and insights."""
        try:
            # Get search types distribution
            search_types_result = await self.db.execute(
                select(
                    UserSearch.search_type,
                    func.count(UserSearch.id).label("count"),
                ).where(
                    UserSearch.searched_at >= time_filter
                ).group_by(
                    UserSearch.search_type
                )
            )
            
            search_types = [
                {"type": row[0], "count": row[1]}
                for row in search_types_result.fetchall()
            ]
            
            # Get search success rates
            success_result = await self.db.execute(
                select(
                    func.count(UserSearch.id).filter(UserSearch.total_results > 0).label("successful"),
                    func.count(UserSearch.id).label("total"),
                ).where(
                    UserSearch.searched_at >= time_filter
                )
            )
            
            success_data = success_result.fetchone()
            success_rate = (
                success_data[0] / success_data[1] * 100
                if success_data[1] and success_data[1] > 0
                else 0
            )
            
            return {
                "search_types": search_types,
                "success_rate": success_rate,
                "total_searches": success_data[1] or 0,
            }
            
        except Exception as e:
            logger.error("Failed to get search patterns", error=str(e))
            return {}
    
    async def _get_platform_statistics(self, time_filter: datetime) -> List[Dict[str, Any]]:
        """Get platform statistics for comparison."""
        try:
            stats_result = await self.db.execute(
                select(
                    Platform.name,
                    func.count(Price.id).label("product_count"),
                    func.avg(Price.selling_price).label("avg_price"),
                    func.avg(Price.discount_percentage).label("avg_discount"),
                    func.count(Price.id).filter(Price.is_available == True).label("available_products"),
                ).join(
                    Price, Platform.id == Price.platform_id
                ).where(
                    Price.updated_at >= time_filter
                ).group_by(
                    Platform.id, Platform.name
                )
            )
            
            platform_stats = []
            for row in stats_result.fetchall():
                platform_stats.append({
                    "platform_name": row[0],
                    "product_count": row[1],
                    "avg_price": float(row[2]) if row[2] else 0,
                    "avg_discount": float(row[3]) if row[3] else 0,
                    "availability_rate": (
                        row[4] / row[1] * 100
                        if row[1] and row[1] > 0
                        else 0
                    ),
                })
            
            return platform_stats
            
        except Exception as e:
            logger.error("Failed to get platform statistics", error=str(e))
            return []
    
    async def _get_price_competitiveness(self, time_filter: datetime) -> List[Dict[str, Any]]:
        """Get price competitiveness analysis."""
        try:
            # This would implement price competitiveness logic
            # For now, return basic structure
            return [
                {
                    "platform_name": "Blinkit",
                    "competitiveness_score": 85.5,
                    "price_position": "competitive",
                    "avg_price_difference": -5.2,
                },
                {
                    "platform_name": "Zepto",
                    "competitiveness_score": 78.3,
                    "price_position": "moderate",
                    "avg_price_difference": 2.1,
                },
            ]
            
        except Exception as e:
            logger.error("Failed to get price competitiveness", error=str(e))
            return []
    
    async def _get_availability_comparison(self, time_filter: datetime) -> List[Dict[str, Any]]:
        """Get availability comparison across platforms."""
        try:
            availability_result = await self.db.execute(
                select(
                    Platform.name,
                    func.count(Price.id).label("total_products"),
                    func.count(Price.id).filter(Price.is_available == True).label("available_products"),
                ).join(
                    Price, Platform.id == Price.platform_id
                ).where(
                    Price.updated_at >= time_filter
                ).group_by(
                    Platform.id, Platform.name
                )
            )
            
            availability_data = []
            for row in availability_result.fetchall():
                availability_rate = (
                    row[2] / row[1] * 100
                    if row[1] and row[1] > 0
                    else 0
                )
                
                availability_data.append({
                    "platform_name": row[0],
                    "total_products": row[1],
                    "available_products": row[2],
                    "availability_rate": availability_rate,
                })
            
            return availability_data
            
        except Exception as e:
            logger.error("Failed to get availability comparison", error=str(e))
            return []
    
    async def _get_user_search_patterns(self, time_filter: datetime) -> Dict[str, Any]:
        """Get user search patterns."""
        try:
            # Get search frequency by hour
            hourly_patterns_result = await self.db.execute(
                select(
                    func.extract('hour', UserSearch.searched_at).label("hour"),
                    func.count(UserSearch.id).label("count"),
                ).where(
                    UserSearch.searched_at >= time_filter
                ).group_by(
                    func.extract('hour', UserSearch.searched_at)
                ).order_by(
                    func.extract('hour', UserSearch.searched_at)
                )
            )
            
            hourly_patterns = [
                {"hour": int(row[0]), "count": row[1]}
                for row in hourly_patterns_result.fetchall()
            ]
            
            return {
                "hourly_patterns": hourly_patterns,
                "peak_hour": max(hourly_patterns, key=lambda x: x["count"])["hour"] if hourly_patterns else 0,
            }
            
        except Exception as e:
            logger.error("Failed to get user search patterns", error=str(e))
            return {}
    
    async def _get_query_success_rates(self, time_filter: datetime) -> Dict[str, Any]:
        """Get query success rates by type."""
        try:
            success_rates_result = await self.db.execute(
                select(
                    UserQuery.query_type,
                    func.count(UserQuery.id).filter(UserQuery.success == True).label("successful"),
                    func.count(UserQuery.id).label("total"),
                ).where(
                    UserQuery.queried_at >= time_filter
                ).group_by(
                    UserQuery.query_type
                )
            )
            
            success_rates = []
            for row in success_rates_result.fetchall():
                rate = (
                    row[1] / row[2] * 100
                    if row[2] and row[2] > 0
                    else 0
                )
                
                success_rates.append({
                    "query_type": row[0],
                    "success_rate": rate,
                    "successful_queries": row[1],
                    "total_queries": row[2],
                })
            
            return {
                "success_rates": success_rates,
                "overall_success_rate": (
                    sum(rate["successful_queries"] for rate in success_rates) /
                    sum(rate["total_queries"] for rate in success_rates) * 100
                    if success_rates and sum(rate["total_queries"] for rate in success_rates) > 0
                    else 0
                ),
            }
            
        except Exception as e:
            logger.error("Failed to get query success rates", error=str(e))
            return {}
    
    async def _get_user_engagement(self, time_filter: datetime) -> Dict[str, Any]:
        """Get user engagement metrics."""
        try:
            engagement_result = await self.db.execute(
                select(
                    func.count(UserQuery.user_id.distinct()).label("unique_users"),
                    func.count(UserQuery.id).label("total_queries"),
                    func.avg(UserQuery.rating).label("avg_rating"),
                    func.count(UserQuery.id).filter(UserQuery.rating >= 4).label("high_ratings"),
                ).where(
                    UserQuery.queried_at >= time_filter
                )
            )
            
            engagement = engagement_result.fetchone()
            
            return {
                "unique_users": engagement[0] or 0,
                "total_queries": engagement[1] or 0,
                "avg_rating": float(engagement[2]) if engagement[2] else 0,
                "high_rating_rate": (
                    engagement[3] / engagement[1] * 100
                    if engagement[1] and engagement[1] > 0
                    else 0
                ),
                "queries_per_user": (
                    engagement[1] / engagement[0]
                    if engagement[0] and engagement[0] > 0
                    else 0
                ),
            }
            
        except Exception as e:
            logger.error("Failed to get user engagement", error=str(e))
            return {} 