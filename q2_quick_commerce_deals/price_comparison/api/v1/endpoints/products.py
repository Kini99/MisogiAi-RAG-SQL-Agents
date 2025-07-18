"""Products API endpoints for the price comparison platform."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ...database.base import get_db
from ...services.product_service import ProductService

router = APIRouter()

@router.get("/", summary="Search products")
async def search_products(
    q: str = Query("", description="Search query"),
    limit: int = 50,
    offset: int = 0,
    category_id: int = None,
    brand_id: int = None,
    platform_id: int = None,
    min_price: float = None,
    max_price: float = None,
    in_stock_only: bool = True,
    sort_by: str = "relevance",
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    return await service.search_products(
        query=q,
        limit=limit,
        offset=offset,
        category_id=category_id,
        brand_id=brand_id,
        platform_id=platform_id,
        min_price=min_price,
        max_price=max_price,
        in_stock_only=in_stock_only,
        sort_by=sort_by,
    )

@router.get("/{product_id}", summary="Get product details")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    product = await service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/{product_id}/prices", summary="Get product prices across platforms")
async def get_product_prices(product_id: int, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    return await service.get_product_prices(product_id)

@router.get("/{product_id}/availability", summary="Get product availability across platforms")
async def get_product_availability(product_id: int, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    return await service.get_product_availability(product_id)

@router.get("/best-deals", summary="Get best deals")
async def get_best_deals(
    limit: int = 20,
    min_discount: float = 20.0,
    category_id: int = None,
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    return await service.get_best_deals(limit=limit, min_discount=min_discount, category_id=category_id) 