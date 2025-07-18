"""Platform-specific models for the price comparison platform."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Integer, String, Text, Boolean, DateTime, Float, 
    ForeignKey, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from ..base import Base
from ..core.logging import LoggerMixin


class PlatformProduct(Base, LoggerMixin):
    """Platform-specific product mapping."""
    
    __tablename__ = "platform_products"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    platform_id: Mapped[int] = mapped_column(Integer, ForeignKey("platforms.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    # Platform-specific identifiers
    platform_product_id: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    platform_sku: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    platform_barcode: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    
    # Platform-specific data
    platform_name: Mapped[Optional[str]] = mapped_column(String(500))
    platform_description: Mapped[Optional[str]] = mapped_column(Text)
    platform_url: Mapped[Optional[str]] = mapped_column(String(500))
    platform_images: Mapped[Optional[list]] = mapped_column(JSONB)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)  # Matching confidence
    
    # Metadata
    last_synced: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sync_status: Mapped[str] = mapped_column(String(50), default="active", index=True)  # active, inactive, error
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    platform = relationship("Platform", back_populates="platform_products")
    product = relationship("Product", back_populates="platform_products")
    
    __table_args__ = (
        Index("idx_platform_products_platform_product", "platform_id", "product_id"),
        Index("idx_platform_products_platform_id", "platform_id", "platform_product_id"),
        Index("idx_platform_products_active_verified", "is_active", "is_verified"),
        Index("idx_platform_products_sync_status", "sync_status", "last_synced"),
        UniqueConstraint("platform_id", "platform_product_id", name="uq_platform_product_id"),
        UniqueConstraint("platform_id", "product_id", name="uq_platform_product_mapping"),
    )


class PlatformCategory(Base, LoggerMixin):
    """Platform-specific category mapping."""
    
    __tablename__ = "platform_categories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    platform_id: Mapped[int] = mapped_column(Integer, ForeignKey("platforms.id"), nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    
    # Platform-specific identifiers
    platform_category_id: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    platform_category_name: Mapped[str] = mapped_column(String(200), nullable=False)
    platform_category_path: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Platform-specific data
    platform_category_description: Mapped[Optional[str]] = mapped_column(Text)
    platform_category_image: Mapped[Optional[str]] = mapped_column(String(500))
    platform_category_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Hierarchy
    platform_parent_category_id: Mapped[Optional[str]] = mapped_column(String(200), index=True)
    platform_category_level: Mapped[int] = mapped_column(Integer, default=0)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # Metadata
    last_synced: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sync_status: Mapped[str] = mapped_column(String(50), default="active", index=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    platform = relationship("Platform", back_populates="platform_categories")
    category = relationship("Category", back_populates="platform_categories")
    
    __table_args__ = (
        Index("idx_platform_categories_platform_category", "platform_id", "category_id"),
        Index("idx_platform_categories_platform_id", "platform_id", "platform_category_id"),
        Index("idx_platform_categories_active_verified", "is_active", "is_verified"),
        UniqueConstraint("platform_id", "platform_category_id", name="uq_platform_category_id"),
        UniqueConstraint("platform_id", "category_id", name="uq_platform_category_mapping"),
    )


class PlatformBrand(Base, LoggerMixin):
    """Platform-specific brand mapping."""
    
    __tablename__ = "platform_brands"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    platform_id: Mapped[int] = mapped_column(Integer, ForeignKey("platforms.id"), nullable=False, index=True)
    brand_id: Mapped[int] = mapped_column(Integer, ForeignKey("brands.id"), nullable=False, index=True)
    
    # Platform-specific identifiers
    platform_brand_id: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    platform_brand_name: Mapped[str] = mapped_column(String(200), nullable=False)
    
    # Platform-specific data
    platform_brand_description: Mapped[Optional[str]] = mapped_column(Text)
    platform_brand_logo: Mapped[Optional[str]] = mapped_column(String(500))
    platform_brand_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # Metadata
    last_synced: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sync_status: Mapped[str] = mapped_column(String(50), default="active", index=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    platform = relationship("Platform", back_populates="platform_brands")
    brand = relationship("Brand", back_populates="platform_brands")
    
    __table_args__ = (
        Index("idx_platform_brands_platform_brand", "platform_id", "brand_id"),
        Index("idx_platform_brands_platform_id", "platform_id", "platform_brand_id"),
        Index("idx_platform_brands_active_verified", "is_active", "is_verified"),
        UniqueConstraint("platform_id", "platform_brand_id", name="uq_platform_brand_id"),
        UniqueConstraint("platform_id", "brand_id", name="uq_platform_brand_mapping"),
    )


class PlatformPricing(Base, LoggerMixin):
    """Platform-specific pricing information."""
    
    __tablename__ = "platform_pricing"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    platform_id: Mapped[int] = mapped_column(Integer, ForeignKey("platforms.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    # Platform-specific pricing
    platform_mrp: Mapped[Optional[float]] = mapped_column(Float)
    platform_selling_price: Mapped[Optional[float]] = mapped_column(Float)
    platform_discounted_price: Mapped[Optional[float]] = mapped_column(Float)
    platform_currency: Mapped[str] = mapped_column(String(3), default="INR")
    
    # Platform-specific discounts
    platform_discount_percentage: Mapped[Optional[float]] = mapped_column(Float)
    platform_discount_amount: Mapped[Optional[float]] = mapped_column(Float)
    platform_discount_description: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Platform-specific fees
    platform_delivery_fee: Mapped[Optional[float]] = mapped_column(Float, default=0)
    platform_packaging_fee: Mapped[Optional[float]] = mapped_column(Float, default=0)
    platform_taxes: Mapped[Optional[float]] = mapped_column(Float, default=0)
    
    # Platform-specific offers
    platform_offers: Mapped[Optional[list]] = mapped_column(JSONB)
    platform_coupons: Mapped[Optional[list]] = mapped_column(JSONB)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    
    # Metadata
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    source_url: Mapped[Optional[str]] = mapped_column(String(500))
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    platform = relationship("Platform", back_populates="platform_pricing")
    product = relationship("Product")
    
    __table_args__ = (
        Index("idx_platform_pricing_platform_product", "platform_id", "product_id"),
        Index("idx_platform_pricing_active_available", "is_active", "is_available"),
        Index("idx_platform_pricing_selling_price", "platform_selling_price"),
        Index("idx_platform_pricing_discount_percentage", "platform_discount_percentage"),
        Index("idx_platform_pricing_last_updated", "last_updated"),
        UniqueConstraint("platform_id", "product_id", name="uq_platform_pricing_product"),
        CheckConstraint("platform_mrp IS NULL OR platform_mrp >= 0", name="ck_platform_mrp_positive"),
        CheckConstraint("platform_selling_price IS NULL OR platform_selling_price >= 0", name="ck_platform_selling_price_positive"),
    )


class PlatformAvailability(Base, LoggerMixin):
    """Platform-specific availability information."""
    
    __tablename__ = "platform_availability"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    platform_id: Mapped[int] = mapped_column(Integer, ForeignKey("platforms.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    # Platform-specific availability
    platform_is_available: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    platform_availability_status: Mapped[str] = mapped_column(String(50), default="in_stock", index=True)
    platform_stock_quantity: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Platform-specific delivery
    platform_delivery_time_min: Mapped[Optional[int]] = mapped_column(Integer)  # minutes
    platform_delivery_time_max: Mapped[Optional[int]] = mapped_column(Integer)  # minutes
    platform_delivery_slots: Mapped[Optional[list]] = mapped_column(JSONB)
    
    # Platform-specific restrictions
    platform_min_order_quantity: Mapped[Optional[int]] = mapped_column(Integer, default=1)
    platform_max_order_quantity: Mapped[Optional[int]] = mapped_column(Integer)
    platform_restrictions: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    
    # Metadata
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    source_url: Mapped[Optional[str]] = mapped_column(String(500))
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    platform = relationship("Platform", back_populates="platform_availability")
    product = relationship("Product")
    
    __table_args__ = (
        Index("idx_platform_availability_platform_product", "platform_id", "product_id"),
        Index("idx_platform_availability_status", "platform_availability_status", "platform_is_available"),
        Index("idx_platform_availability_last_updated", "last_updated"),
        UniqueConstraint("platform_id", "product_id", name="uq_platform_availability_product"),
        CheckConstraint("platform_delivery_time_max IS NULL OR platform_delivery_time_max >= platform_delivery_time_min", name="ck_platform_delivery_time"),
    )


class PlatformMetadata(Base, LoggerMixin):
    """Platform-specific metadata and configuration."""
    
    __tablename__ = "platform_metadata"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    platform_id: Mapped[int] = mapped_column(Integer, ForeignKey("platforms.id"), nullable=False, index=True)
    
    # Platform configuration
    api_config: Mapped[Optional[dict]] = mapped_column(JSONB)
    scraping_config: Mapped[Optional[dict]] = mapped_column(JSONB)
    rate_limits: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Platform capabilities
    supports_real_time_pricing: Mapped[bool] = mapped_column(Boolean, default=True)
    supports_inventory_tracking: Mapped[bool] = mapped_column(Boolean, default=True)
    supports_delivery_slots: Mapped[bool] = mapped_column(Boolean, default=True)
    supports_coupons: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Data quality metrics
    data_freshness_threshold: Mapped[Optional[int]] = mapped_column(Integer)  # minutes
    sync_frequency: Mapped[Optional[int]] = mapped_column(Integer)  # minutes
    last_successful_sync: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Error tracking
    last_error: Mapped[Optional[str]] = mapped_column(Text)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    consecutive_failures: Mapped[int] = mapped_column(Integer, default=0)
    
    # Performance metrics
    avg_response_time: Mapped[Optional[float]] = mapped_column(Float)  # milliseconds
    success_rate: Mapped[Optional[float]] = mapped_column(Float)  # percentage
    total_requests: Mapped[int] = mapped_column(Integer, default=0)
    successful_requests: Mapped[int] = mapped_column(Integer, default=0)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_healthy: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    platform = relationship("Platform", back_populates="platform_metadata")
    
    __table_args__ = (
        Index("idx_platform_metadata_platform", "platform_id"),
        Index("idx_platform_metadata_active_healthy", "is_active", "is_healthy"),
        Index("idx_platform_metadata_last_sync", "last_successful_sync"),
        UniqueConstraint("platform_id", name="uq_platform_metadata"),
        CheckConstraint("success_rate IS NULL OR (success_rate >= 0 AND success_rate <= 100)", name="ck_success_rate"),
        CheckConstraint("consecutive_failures >= 0", name="ck_consecutive_failures"),
    ) 