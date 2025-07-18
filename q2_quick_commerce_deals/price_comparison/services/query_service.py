"""Query service for the price comparison platform."""

import time
import hashlib
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func
from sqlalchemy.exc import SQLAlchemyError

from ..core.logging import get_logger
from ..database.models.analytics import QueryLog, QueryResult, QueryPerformance
from ..database.models.users import UserQuery
from .cache_service import CacheService

logger = get_logger(__name__)


class QueryService:
    """Service for handling query processing, optimization, and analytics."""
    
    def __init__(self, db: AsyncSession):
        """Initialize query service."""
        self.db = db
        self.cache_service = CacheService()
    
    async def process_natural_language_query(
        self,
        query: str,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        max_results: int = 100,
    ) -> Dict[str, Any]:
        """Process natural language query and return results."""
        start_time = time.time()
        query_hash = hashlib.sha256(query.encode()).hexdigest()
        
        try:
            # Check cache first
            cache_key = f"nl_query:{query_hash}:{max_results}"
            cached_result = await self.cache_service.get(cache_key)
            
            if cached_result:
                logger.info("Serving cached natural language query result", query_hash=query_hash)
                return {
                    "success": True,
                    "results": cached_result["results"],
                    "cache_hit": True,
                    "execution_time_ms": (time.time() - start_time) * 1000,
                    "query_hash": query_hash,
                }
            
            # Process query (this would integrate with SQL agent)
            # For now, return a mock result
            result = await self._mock_query_processing(query, max_results)
            
            # Cache the result
            await self.cache_service.set(cache_key, result, ttl=300)
            
            # Log query
            await self._log_query(
                query=query,
                query_hash=query_hash,
                query_type="natural_language",
                user_id=user_id,
                session_id=session_id,
                execution_time=(time.time() - start_time),
                success=True,
                result_count=len(result.get("results", [])),
            )
            
            return {
                "success": True,
                "results": result["results"],
                "cache_hit": False,
                "execution_time_ms": (time.time() - start_time) * 1000,
                "query_hash": query_hash,
                "metadata": result.get("metadata"),
            }
            
        except Exception as e:
            logger.error("Query processing failed", query=query, error=str(e))
            
            # Log failed query
            await self._log_query(
                query=query,
                query_hash=query_hash,
                query_type="natural_language",
                user_id=user_id,
                session_id=session_id,
                execution_time=(time.time() - start_time),
                success=False,
                error_message=str(e),
            )
            
            return {
                "success": False,
                "error": str(e),
                "cache_hit": False,
                "execution_time_ms": (time.time() - start_time) * 1000,
                "query_hash": query_hash,
            }
    
    async def _mock_query_processing(self, query: str, max_results: int) -> Dict[str, Any]:
        """Mock query processing for demonstration."""
        # This would be replaced with actual SQL agent integration
        query_lower = query.lower()
        
        if "cheapest" in query_lower and "onions" in query_lower:
            return {
                "results": [
                    {
                        "platform": "Blinkit",
                        "product": "Fresh Onions",
                        "price": 45.0,
                        "mrp": 60.0,
                        "discount": "25%",
                        "delivery_time": "10-15 minutes",
                    },
                    {
                        "platform": "Zepto",
                        "product": "Organic Onions",
                        "price": 48.0,
                        "mrp": 65.0,
                        "discount": "26%",
                        "delivery_time": "10 minutes",
                    },
                ],
                "metadata": {
                    "intent": "price_comparison",
                    "entities": ["onions", "cheapest"],
                    "confidence": 0.95,
                },
            }
        elif "discount" in query_lower and "blinkit" in query_lower:
            return {
                "results": [
                    {
                        "platform": "Blinkit",
                        "product": "Premium Basmati Rice",
                        "price": 120.0,
                        "mrp": 180.0,
                        "discount": "33%",
                    },
                    {
                        "platform": "Blinkit",
                        "product": "Organic Tomatoes",
                        "price": 35.0,
                        "mrp": 50.0,
                        "discount": "30%",
                    },
                ],
                "metadata": {
                    "intent": "discount_search",
                    "entities": ["blinkit", "discount"],
                    "confidence": 0.92,
                },
            }
        else:
            return {
                "results": [
                    {
                        "platform": "Multiple",
                        "product": "Various Products",
                        "message": "Query processed successfully",
                    }
                ],
                "metadata": {
                    "intent": "general_search",
                    "entities": [],
                    "confidence": 0.85,
                },
            }
    
    async def _log_query(
        self,
        query: str,
        query_hash: str,
        query_type: str,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        execution_time: float = 0.0,
        success: bool = True,
        result_count: int = 0,
        error_message: Optional[str] = None,
    ) -> None:
        """Log query execution for analytics."""
        try:
            query_log = QueryLog(
                query_hash=query_hash,
                original_query=query,
                query_type=query_type,
                user_id=user_id,
                session_id=session_id,
                processing_time_ms=int(execution_time * 1000),
                success=success,
                result_count=result_count,
                error_message=error_message,
            )
            
            self.db.add(query_log)
            await self.db.commit()
            
        except Exception as e:
            logger.error("Failed to log query", error=str(e))
            await self.db.rollback()
    
    async def get_query_suggestions(self, partial_query: str, limit: int = 10) -> List[str]:
        """Get query suggestions based on partial input."""
        try:
            # Get popular queries that match the partial input
            stmt = select(UserQuery.query).where(
                UserQuery.query.ilike(f"%{partial_query}%"),
                UserQuery.success == True,
            ).order_by(
                UserQuery.queried_at.desc()
            ).limit(limit)
            
            result = await self.db.execute(stmt)
            suggestions = [row[0] for row in result.fetchall()]
            
            # Add default suggestions if not enough found
            default_suggestions = [
                "Which app has cheapest onions right now?",
                "Show products with 30%+ discount on Blinkit",
                "Compare fruit prices between Zepto and Instamart",
                "Find best deals for ₹1000 grocery list",
                "What's the cheapest milk delivery today?",
            ]
            
            for suggestion in default_suggestions:
                if len(suggestions) >= limit:
                    break
                if partial_query.lower() in suggestion.lower() and suggestion not in suggestions:
                    suggestions.append(suggestion)
            
            return suggestions[:limit]
            
        except Exception as e:
            logger.error("Failed to get query suggestions", error=str(e))
            return []
    
    async def get_popular_queries(self, limit: int = 10, time_period: str = "24h") -> List[Dict[str, Any]]:
        """Get popular queries from the last time period."""
        try:
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
            
            # Get popular queries
            stmt = select(
                UserQuery.query,
                func.count(UserQuery.id).label("count"),
                func.avg(UserQuery.rating).label("avg_rating"),
            ).where(
                UserQuery.queried_at >= time_filter,
                UserQuery.success == True,
            ).group_by(
                UserQuery.query
            ).order_by(
                func.count(UserQuery.id).desc()
            ).limit(limit)
            
            result = await self.db.execute(stmt)
            popular_queries = []
            
            for row in result.fetchall():
                popular_queries.append({
                    "query": row[0],
                    "count": row[1],
                    "avg_rating": float(row[2]) if row[2] else None,
                })
            
            return popular_queries
            
        except Exception as e:
            logger.error("Failed to get popular queries", error=str(e))
            return []
    
    async def get_query_analytics(self, time_period: str = "24h") -> Dict[str, Any]:
        """Get query analytics for the specified time period."""
        try:
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
            
            # Get analytics
            stmt = select(
                func.count(UserQuery.id).label("total_queries"),
                func.avg(UserQuery.execution_time_ms).label("avg_execution_time"),
                func.count(UserQuery.id).filter(UserQuery.success == True).label("successful_queries"),
                func.count(UserQuery.id).filter(UserQuery.success == False).label("failed_queries"),
            ).where(
                UserQuery.queried_at >= time_filter
            )
            
            result = await self.db.execute(stmt)
            row = result.fetchone()
            
            total_queries = row[0] or 0
            successful_queries = row[2] or 0
            
            return {
                "total_queries": total_queries,
                "successful_queries": successful_queries,
                "failed_queries": row[3] or 0,
                "success_rate": (successful_queries / total_queries * 100) if total_queries > 0 else 0,
                "avg_execution_time_ms": float(row[1]) if row[1] else 0,
                "time_period": time_period,
            }
            
        except Exception as e:
            logger.error("Failed to get query analytics", error=str(e))
            return {}
    
    async def optimize_query(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """Optimize query for better performance."""
        try:
            # This would implement query optimization logic
            # For now, return the original query with basic optimization info
            optimization_info = {
                "original_query": query,
                "optimized_query": query,
                "optimizations_applied": [],
                "estimated_improvement": 0.0,
            }
            
            return query, optimization_info
            
        except Exception as e:
            logger.error("Query optimization failed", error=str(e))
            return query, {}
    
    async def analyze_query_complexity(self, query: str) -> Dict[str, Any]:
        """Analyze query complexity and performance characteristics."""
        try:
            # Basic complexity analysis
            complexity_score = 0
            complexity_factors = []
            
            # Check for common complexity indicators
            if "JOIN" in query.upper():
                complexity_score += 30
                complexity_factors.append("multiple_joins")
            
            if "GROUP BY" in query.upper():
                complexity_score += 20
                complexity_factors.append("grouping")
            
            if "ORDER BY" in query.upper():
                complexity_score += 10
                complexity_factors.append("sorting")
            
            if "LIKE" in query.upper():
                complexity_score += 15
                complexity_factors.append("pattern_matching")
            
            if "DISTINCT" in query.upper():
                complexity_score += 25
                complexity_factors.append("distinct_operation")
            
            return {
                "complexity_score": min(complexity_score, 100),
                "complexity_level": "low" if complexity_score < 30 else "medium" if complexity_score < 70 else "high",
                "complexity_factors": complexity_factors,
                "estimated_execution_time_ms": complexity_score * 10,  # Rough estimate
                "recommended_optimizations": self._get_optimization_recommendations(complexity_factors),
            }
            
        except Exception as e:
            logger.error("Query complexity analysis failed", error=str(e))
            return {}
    
    def _get_optimization_recommendations(self, complexity_factors: List[str]) -> List[str]:
        """Get optimization recommendations based on complexity factors."""
        recommendations = []
        
        if "multiple_joins" in complexity_factors:
            recommendations.append("Consider adding indexes on join columns")
        
        if "grouping" in complexity_factors:
            recommendations.append("Use covering indexes for GROUP BY operations")
        
        if "pattern_matching" in complexity_factors:
            recommendations.append("Consider full-text search for better performance")
        
        if "distinct_operation" in complexity_factors:
            recommendations.append("Evaluate if DISTINCT is necessary")
        
        return recommendations 