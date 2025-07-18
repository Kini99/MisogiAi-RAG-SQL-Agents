"""Product service for the price comparison platform."""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.exc import SQLAlchemyError

from ..core.logging import get_logger
from ..database.models.core import Product, Category, Brand, Platform
from ..database.models.pricing import Price
from ..database.models.availability import Availability
from ..database.models.platforms import PlatformProduct
from .cache_service import CacheService

logger = get_logger(__name__)


class ProductService:
    """Service for managing product data and search functionality."""
    
    def __init__(self, db: AsyncSession):
        """Initialize product service."""
        self.db = db
        self.cache_service = CacheService()
    
    async def search_products(
        self,
        query: str,
        limit: int = 50,
        offset: int = 0,
        category_id: Optional[int] = None,
        brand_id: Optional[int] = None,
        platform_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock_only: bool = True,
        sort_by: str = "relevance",
    ) -> Dict[str, Any]:
        """Search products with filters and sorting."""
        try:
            # Generate cache key based on search parameters
            cache_key = f"product_search:{hash(query)}:{limit}:{offset}:{category_id}:{brand_id}:{platform_id}:{min_price}:{max_price}:{in_stock_only}:{sort_by}"
            cached_result = await self.cache_service.get(cache_key)
            
            if cached_result:
                return cached_result
            
            # Build base query
            base_query = select(Product).distinct()
            
            # Add joins for filtering
            base_query = base_query.outerjoin(Price, Product.id == Price.product_id)
            base_query = base_query.outerjoin(Availability, Product.id == Availability.product_id)
            
            # Add search conditions
            search_conditions = [
                or_(
                    Product.name.ilike(f"%{query}%"),
                    Product.description.ilike(f"%{query}%"),
                    Product.sku.ilike(f"%{query}%"),
                )
            ]
            
            # Add filters
            if category_id:
                search_conditions.append(Product.category_id == category_id)
            
            if brand_id:
                search_conditions.append(Product.brand_id == brand_id)
            
            if platform_id:
                base_query = base_query.join(PlatformProduct, Product.id == PlatformProduct.product_id)
                search_conditions.append(PlatformProduct.platform_id == platform_id)
            
            if min_price is not None:
                search_conditions.append(Price.selling_price >= min_price)
            
            if max_price is not None:
                search_conditions.append(Price.selling_price <= max_price)
            
            if in_stock_only:
                search_conditions.append(Availability.is_available == True)
            
            # Apply conditions
            base_query = base_query.where(and_(*search_conditions))
            
            # Add sorting
            if sort_by == "price_low":
                base_query = base_query.order_by(asc(Price.selling_price))
            elif sort_by == "price_high":
                base_query = base_query.order_by(desc(Price.selling_price))
            elif sort_by == "name":
                base_query = base_query.order_by(asc(Product.name))
            elif sort_by == "discount":
                base_query = base_query.order_by(desc(Price.discount_percentage))
            else:  # relevance - default
                base_query = base_query.order_by(desc(Product.rating), desc(Product.review_count))
            
            # Add pagination
            base_query = base_query.limit(limit).offset(offset)
            
            # Execute query
            result = await self.db.execute(base_query)
            products = result.scalars().all()
            
            # Get total count for pagination
            count_query = select(func.count(Product.id.distinct())).select_from(base_query.subquery())
            count_result = await self.db.execute(count_query)
            total_count = count_result.scalar()
            
            # Format results
            products_data = []
            for product in products:
                product_data = await self._format_product_data(product)
                products_data.append(product_data)
            
            search_result = {
                "products": products_data,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total_count,
                "search_query": query,
                "filters_applied": {
                    "category_id": category_id,
                    "brand_id": brand_id,
                    "platform_id": platform_id,
                    "min_price": min_price,
                    "max_price": max_price,
                    "in_stock_only": in_stock_only,
                    "sort_by": sort_by,
                },
            }
            
            # Cache the result
            await self.cache_service.set(cache_key, search_result, ttl=1800)
            
            return search_result
            
        except Exception as e:
            logger.error("Product search failed", query=query, error=str(e))
            return {
                "products": [],
                "total_count": 0,
                "limit": limit,
                "offset": offset,
                "has_more": False,
                "search_query": query,
                "error": str(e),
            }
    
    async def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get product by ID with detailed information."""
        try:
            cache_key = f"product:{product_id}"
            cached_result = await self.cache_service.get(cache_key)
            
            if cached_result:
                return cached_result
            
            result = await self.db.execute(
                select(Product).where(Product.id == product_id)
            )
            product = result.scalar_one_or_none()
            
            if not product:
                return None
            
            product_data = await self._format_product_data(product, include_details=True)
            
            # Cache the result
            await self.cache_service.set(cache_key, product_data, ttl=3600)
            
            return product_data
            
        except Exception as e:
            logger.error("Failed to get product by ID", product_id=product_id, error=str(e))
            return None
    
    async def get_product_prices(self, product_id: int) -> List[Dict[str, Any]]:
        """Get all prices for a product across platforms."""
        try:
            cache_key = f"product_prices:{product_id}"
            cached_result = await self.cache_service.get(cache_key)
            
            if cached_result:
                return cached_result
            
            result = await self.db.execute(
                select(Price, Platform)
                .join(Platform, Price.platform_id == Platform.id)
                .where(
                    and_(
                        Price.product_id == product_id,
                        Price.is_active == True,
                    )
                )
                .order_by(Price.selling_price)
            )
            
            prices_data = []
            for price, platform in result.fetchall():
                prices_data.append({
                    "platform_id": platform.id,
                    "platform_name": platform.name,
                    "platform_slug": platform.slug,
                    "mrp": float(price.mrp),
                    "selling_price": float(price.selling_price),
                    "discounted_price": float(price.discounted_price) if price.discounted_price else None,
                    "discount_percentage": price.discount_percentage,
                    "discount_amount": float(price.discount_amount) if price.discount_amount else None,
                    "currency": price.currency,
                    "delivery_fee": float(price.delivery_fee) if price.delivery_fee else 0,
                    "packaging_fee": float(price.packaging_fee) if price.packaging_fee else 0,
                    "taxes": float(price.taxes) if price.taxes else 0,
                    "is_available": price.is_available,
                    "last_updated": price.updated_at.isoformat(),
                })
            
            # Cache the result
            await self.cache_service.set(cache_key, prices_data, ttl=900)  # 15 minutes
            
            return prices_data
            
        except Exception as e:
            logger.error("Failed to get product prices", product_id=product_id, error=str(e))
            return []
    
    async def get_product_availability(self, product_id: int) -> List[Dict[str, Any]]:
        """Get availability information for a product across platforms."""
        try:
            cache_key = f"product_availability:{product_id}"
            cached_result = await self.cache_service.get(cache_key)
            
            if cached_result:
                return cached_result
            
            result = await self.db.execute(
                select(Availability, Platform)
                .join(Platform, Availability.platform_id == Platform.id)
                .where(Availability.product_id == product_id)
                .order_by(Platform.name)
            )
            
            availability_data = []
            for availability, platform in result.fetchall():
                availability_data.append({
                    "platform_id": platform.id,
                    "platform_name": platform.name,
                    "platform_slug": platform.slug,
                    "is_available": availability.is_available,
                    "availability_status": availability.availability_status,
                    "stock_quantity": availability.stock_quantity,
                    "min_order_quantity": availability.min_order_quantity,
                    "max_order_quantity": availability.max_order_quantity,
                    "delivery_time_min": availability.delivery_time_min,
                    "delivery_time_max": availability.delivery_time_max,
                    "delivery_slots_available": availability.delivery_slots_available,
                    "is_restricted": availability.is_restricted,
                    "restriction_reason": availability.restriction_reason,
                    "last_updated": availability.updated_at.isoformat(),
                })
            
            # Cache the result
            await self.cache_service.set(cache_key, availability_data, ttl=900)  # 15 minutes
            
            return availability_data
            
        except Exception as e:
            logger.error("Failed to get product availability", product_id=product_id, error=str(e))
            return []
    
    async def get_products_by_category(
        self,
        category_id: int,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "name",
    ) -> Dict[str, Any]:
        """Get products by category."""
        try:
            cache_key = f"products_category:{category_id}:{limit}:{offset}:{sort_by}"
            cached_result = await self.cache_service.get(cache_key)
            
            if cached_result:
                return cached_result
            
            # Build query
            query = select(Product).where(Product.category_id == category_id)
            
            # Add sorting
            if sort_by == "price_low":
                query = query.join(Price, Product.id == Price.product_id).order_by(asc(Price.selling_price))
            elif sort_by == "price_high":
                query = query.join(Price, Product.id == Price.product_id).order_by(desc(Price.selling_price))
            elif sort_by == "rating":
                query = query.order_by(desc(Product.rating))
            elif sort_by == "reviews":
                query = query.order_by(desc(Product.review_count))
            else:  # name
                query = query.order_by(asc(Product.name))
            
            # Add pagination
            query = query.limit(limit).offset(offset)
            
            result = await self.db.execute(query)
            products = result.scalars().all()
            
            # Get total count
            count_result = await self.db.execute(
                select(func.count(Product.id)).where(Product.category_id == category_id)
            )
            total_count = count_result.scalar()
            
            # Format results
            products_data = []
            for product in products:
                product_data = await self._format_product_data(product)
                products_data.append(product_data)
            
            category_result = {
                "products": products_data,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total_count,
                "category_id": category_id,
                "sort_by": sort_by,
            }
            
            # Cache the result
            await self.cache_service.set(cache_key, category_result, ttl=3600)
            
            return category_result
            
        except Exception as e:
            logger.error("Failed to get products by category", category_id=category_id, error=str(e))
            return {
                "products": [],
                "total_count": 0,
                "limit": limit,
                "offset": offset,
                "has_more": False,
                "category_id": category_id,
                "error": str(e),
            }
    
    async def get_products_by_brand(
        self,
        brand_id: int,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "name",
    ) -> Dict[str, Any]:
        """Get products by brand."""
        try:
            cache_key = f"products_brand:{brand_id}:{limit}:{offset}:{sort_by}"
            cached_result = await self.cache_service.get(cache_key)
            
            if cached_result:
                return cached_result
            
            # Build query
            query = select(Product).where(Product.brand_id == brand_id)
            
            # Add sorting
            if sort_by == "price_low":
                query = query.join(Price, Product.id == Price.product_id).order_by(asc(Price.selling_price))
            elif sort_by == "price_high":
                query = query.join(Price, Product.id == Price.product_id).order_by(desc(Price.selling_price))
            elif sort_by == "rating":
                query = query.order_by(desc(Product.rating))
            elif sort_by == "reviews":
                query = query.order_by(desc(Product.review_count))
            else:  # name
                query = query.order_by(asc(Product.name))
            
            # Add pagination
            query = query.limit(limit).offset(offset)
            
            result = await self.db.execute(query)
            products = result.scalars().all()
            
            # Get total count
            count_result = await self.db.execute(
                select(func.count(Product.id)).where(Product.brand_id == brand_id)
            )
            total_count = count_result.scalar()
            
            # Format results
            products_data = []
            for product in products:
                product_data = await self._format_product_data(product)
                products_data.append(product_data)
            
            brand_result = {
                "products": products_data,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total_count,
                "brand_id": brand_id,
                "sort_by": sort_by,
            }
            
            # Cache the result
            await self.cache_service.set(cache_key, brand_result, ttl=3600)
            
            return brand_result
            
        except Exception as e:
            logger.error("Failed to get products by brand", brand_id=brand_id, error=str(e))
            return {
                "products": [],
                "total_count": 0,
                "limit": limit,
                "offset": offset,
                "has_more": False,
                "brand_id": brand_id,
                "error": str(e),
            }
    
    async def get_best_deals(
        self,
        limit: int = 20,
        min_discount: float = 20.0,
        category_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get best deals (products with highest discounts)."""
        try:
            cache_key = f"best_deals:{limit}:{min_discount}:{category_id}"
            cached_result = await self.cache_service.get(cache_key)
            
            if cached_result:
                return cached_result
            
            # Build query
            query = select(Product, Price, Platform)
            query = query.join(Price, Product.id == Price.product_id)
            query = query.join(Platform, Price.platform_id == Platform.id)
            
            # Add conditions
            conditions = [
                Price.discount_percentage >= min_discount,
                Price.is_active == True,
                Price.is_available == True,
            ]
            
            if category_id:
                conditions.append(Product.category_id == category_id)
            
            query = query.where(and_(*conditions))
            query = query.order_by(desc(Price.discount_percentage))
            query = query.limit(limit)
            
            result = await self.db.execute(query)
            
            deals_data = []
            for product, price, platform in result.fetchall():
                deals_data.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "product_image": product.image_url,
                    "platform_id": platform.id,
                    "platform_name": platform.name,
                    "platform_slug": platform.slug,
                    "mrp": float(price.mrp),
                    "selling_price": float(price.selling_price),
                    "discount_percentage": price.discount_percentage,
                    "discount_amount": float(price.discount_amount) if price.discount_amount else None,
                    "currency": price.currency,
                    "rating": product.rating,
                    "review_count": product.review_count,
                })
            
            # Cache the result
            await self.cache_service.set(cache_key, deals_data, ttl=1800)
            
            return deals_data
            
        except Exception as e:
            logger.error("Failed to get best deals", error=str(e))
            return []
    
    async def _format_product_data(self, product: Product, include_details: bool = False) -> Dict[str, Any]:
        """Format product data for API response."""
        product_data = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "sku": product.sku,
            "barcode": product.barcode,
            "image_url": product.image_url,
            "rating": product.rating,
            "review_count": product.review_count,
            "category_id": product.category_id,
            "brand_id": product.brand_id,
            "is_active": product.is_active,
            "created_at": product.created_at.isoformat(),
            "updated_at": product.updated_at.isoformat(),
        }
        
        if include_details:
            # Get category and brand information
            if product.category:
                product_data["category"] = {
                    "id": product.category.id,
                    "name": product.category.name,
                    "slug": product.category.slug,
                }
            
            if product.brand:
                product_data["brand"] = {
                    "id": product.brand.id,
                    "name": product.brand.name,
                    "slug": product.brand.slug,
                }
            
            # Get specifications
            if product.specifications:
                product_data["specifications"] = product.specifications
        
        return product_data 