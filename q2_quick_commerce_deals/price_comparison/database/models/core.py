"""Core database models for platforms, categories, brands, and products."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Float, 
    ForeignKey, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID
import uuid

from ..base import Base
from ..core.logging import LoggerMixin


class Platform(Base, LoggerMixin):
    """Platform model for quick commerce apps."""
    
    __tablename__ = "platforms"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    website_url: Mapped[Optional[str]] = mapped_column(String(500))
    api_endpoint: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    priority: Mapped[int] = mapped_column(Integer, default=0, index=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    platform_products = relationship("PlatformProduct", back_populates="platform")
    platform_categories = relationship("PlatformCategory", back_populates="platform")
    platform_brands = relationship("PlatformBrand", back_populates="platform")
    platform_pricing = relationship("PlatformPricing", back_populates="platform")
    platform_availability = relationship("PlatformAvailability", back_populates="platform")
    platform_metadata = relationship("PlatformMetadata", back_populates="platform")
    
    __table_args__ = (
        Index("idx_platforms_active_priority", "is_active", "priority"),
        Index("idx_platforms_name_slug", "name", "slug"),
    )


class Category(Base, LoggerMixin):
    """Product category model."""
    
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.id"), index=True)
    level: Mapped[int] = mapped_column(Integer, default=0, index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent = relationship("Category", remote_side=[id], backref="children")
    products = relationship("Product", back_populates="category")
    platform_categories = relationship("PlatformCategory", back_populates="category")
    
    __table_args__ = (
        Index("idx_categories_parent_level", "parent_id", "level"),
        Index("idx_categories_active_sort", "is_active", "sort_order"),
        UniqueConstraint("parent_id", "name", name="uq_category_parent_name"),
    )


class Brand(Base, LoggerMixin):
    """Brand model."""
    
    __tablename__ = "brands"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    website_url: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products = relationship("Product", back_populates="brand")
    platform_brands = relationship("PlatformBrand", back_populates="brand")
    
    __table_args__ = (
        Index("idx_brands_active_name", "is_active", "name"),
    )


class Product(Base, LoggerMixin):
    """Product model."""
    
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(500), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    brand_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("brands.id"), index=True)
    barcode: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    sku: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    weight: Mapped[Optional[float]] = mapped_column(Float)
    weight_unit: Mapped[Optional[str]] = mapped_column(String(20))
    dimensions: Mapped[Optional[dict]] = mapped_column(JSONB)
    nutritional_info: Mapped[Optional[dict]] = mapped_column(JSONB)
    ingredients: Mapped[Optional[list]] = mapped_column(JSONB)
    allergens: Mapped[Optional[list]] = mapped_column(JSONB)
    is_vegetarian: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_vegan: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_organic: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_gluten_free: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("Category", back_populates="products")
    brand = relationship("Brand", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product")
    images = relationship("ProductImage", back_populates="product")
    specifications = relationship("ProductSpecification", back_populates="product")
    reviews = relationship("ProductReview", back_populates="product")
    platform_products = relationship("PlatformProduct", back_populates="product")
    prices = relationship("Price", back_populates="product")
    availability = relationship("Availability", back_populates="product")
    
    __table_args__ = (
        Index("idx_products_category_brand", "category_id", "brand_id"),
        Index("idx_products_barcode_sku", "barcode", "sku"),
        Index("idx_products_active_name", "is_active", "name"),
        Index("idx_products_metadata", "metadata", postgresql_using="gin"),
    )


class ProductVariant(Base, LoggerMixin):
    """Product variant model (e.g., different sizes, flavors)."""
    
    __tablename__ = "product_variants"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    sku: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    weight: Mapped[Optional[float]] = mapped_column(Float)
    weight_unit: Mapped[Optional[str]] = mapped_column(String(20))
    volume: Mapped[Optional[float]] = mapped_column(Float)
    volume_unit: Mapped[Optional[str]] = mapped_column(String(20))
    quantity: Mapped[Optional[float]] = mapped_column(Float)
    quantity_unit: Mapped[Optional[str]] = mapped_column(String(20))
    attributes: Mapped[Optional[dict]] = mapped_column(JSONB)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="variants")
    
    __table_args__ = (
        Index("idx_product_variants_product_active", "product_id", "is_active"),
        UniqueConstraint("product_id", "name", name="uq_product_variant_name"),
    )


class ProductImage(Base, LoggerMixin):
    """Product image model."""
    
    __tablename__ = "product_images"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    alt_text: Mapped[Optional[str]] = mapped_column(String(200))
    caption: Mapped[Optional[str]] = mapped_column(String(200))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    width: Mapped[Optional[int]] = mapped_column(Integer)
    height: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="images")
    
    __table_args__ = (
        Index("idx_product_images_product_primary", "product_id", "is_primary"),
        Index("idx_product_images_sort_order", "product_id", "sort_order"),
    )


class ProductSpecification(Base, LoggerMixin):
    """Product specification model."""
    
    __tablename__ = "product_specifications"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(50))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="specifications")
    
    __table_args__ = (
        Index("idx_product_specs_product_name", "product_id", "name"),
        UniqueConstraint("product_id", "name", name="uq_product_spec_name"),
    )


class ProductReview(Base, LoggerMixin):
    """Product review model."""
    
    __tablename__ = "product_reviews"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    platform_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("platforms.id"), index=True)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(200))
    comment: Mapped[Optional[str]] = mapped_column(Text)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_helpful: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="reviews")
    
    __table_args__ = (
        Index("idx_product_reviews_product_rating", "product_id", "rating"),
        Index("idx_product_reviews_verified", "is_verified", "rating"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_rating_range"),
    ) 