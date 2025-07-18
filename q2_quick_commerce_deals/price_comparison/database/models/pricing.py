"""Pricing models for the price comparison platform."""

from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import (
    Integer, String, Text, Boolean, DateTime, Float, 
    ForeignKey, Index, UniqueConstraint, CheckConstraint, Numeric
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from ..base import Base
from ..core.logging import LoggerMixin


class Price(Base, LoggerMixin):
    """Current price model."""
    
    __tablename__ = "prices"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    platform_id: Mapped[int] = mapped_column(Integer, ForeignKey("platforms.id"), nullable=False, index=True)
    variant_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("product_variants.id"), index=True)
    
    # Price fields
    mrp: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    selling_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    discounted_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    
    # Discount information
    discount_percentage: Mapped[Optional[float]] = mapped_column(Float)
    discount_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    
    # Additional pricing
    delivery_fee: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), default=0)
    packaging_fee: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), default=0)
    taxes: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), default=0)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    
    # Metadata
    source_url: Mapped[Optional[str]] = mapped_column(String(500))
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="prices")
    platform = relationship("Platform")
    variant = relationship("ProductVariant")
    price_history = relationship("PriceHistory", back_populates="price")
    discounts = relationship("Discount", back_populates="price")
    
    __table_args__ = (
        Index("idx_prices_product_platform", "product_id", "platform_id"),
        Index("idx_prices_active_available", "is_active", "is_available"),
        Index("idx_prices_selling_price", "selling_price"),
        Index("idx_prices_discount_percentage", "discount_percentage"),
        Index("idx_prices_last_updated", "last_updated"),
        UniqueConstraint("product_id", "platform_id", "variant_id", name="uq_price_product_platform_variant"),
        CheckConstraint("mrp >= 0", name="ck_mrp_positive"),
        CheckConstraint("selling_price >= 0", name="ck_selling_price_positive"),
        CheckConstraint("discounted_price >= 0", name="ck_discounted_price_positive"),
    )


class PriceHistory(Base, LoggerMixin):
    """Price history tracking model."""
    
    __tablename__ = "price_history"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    price_id: Mapped[int] = mapped_column(Integer, ForeignKey("prices.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    platform_id: Mapped[int] = mapped_column(Integer, ForeignKey("platforms.id"), nullable=False, index=True)
    
    # Price snapshot
    mrp: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    selling_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    discounted_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    discount_percentage: Mapped[Optional[float]] = mapped_column(Float)
    discount_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    
    # Change tracking
    price_change: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    percentage_change: Mapped[Optional[float]] = mapped_column(Float)
    
    # Timestamp
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    price = relationship("Price", back_populates="price_history")
    
    __table_args__ = (
        Index("idx_price_history_product_platform", "product_id", "platform_id"),
        Index("idx_price_history_recorded_at", "recorded_at"),
        Index("idx_price_history_price_change", "price_change"),
    )


class DiscountType(Base, LoggerMixin):
    """Discount type model."""
    
    __tablename__ = "discount_types"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    discount_type: Mapped[str] = mapped_column(String(20), nullable=False)  # percentage, fixed, buy_x_get_y
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    discounts = relationship("Discount", back_populates="discount_type")
    
    __table_args__ = (
        CheckConstraint("discount_type IN ('percentage', 'fixed', 'buy_x_get_y', 'free_delivery')", name="ck_discount_type"),
    )


class Discount(Base, LoggerMixin):
    """Discount model."""
    
    __tablename__ = "discounts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    price_id: Mapped[int] = mapped_column(Integer, ForeignKey("prices.id"), nullable=False, index=True)
    discount_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("discount_types.id"), nullable=False, index=True)
    promotion_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("promotions.id"), index=True)
    
    # Discount details
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    discount_value: Mapped[float] = mapped_column(Float, nullable=False)
    discount_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    min_purchase_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    max_discount_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    
    # Conditions
    min_quantity: Mapped[Optional[int]] = mapped_column(Integer, default=1)
    max_quantity: Mapped[Optional[int]] = mapped_column(Integer)
    applicable_categories: Mapped[Optional[list]] = mapped_column(JSONB)
    applicable_brands: Mapped[Optional[list]] = mapped_column(JSONB)
    
    # Validity
    valid_from: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    
    # Usage tracking
    usage_limit: Mapped[Optional[int]] = mapped_column(Integer)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Metadata
    coupon_code: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    terms_conditions: Mapped[Optional[str]] = mapped_column(Text)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    price = relationship("Price", back_populates="discounts")
    discount_type = relationship("DiscountType", back_populates="discounts")
    promotion = relationship("Promotion", back_populates="discounts")
    
    __table_args__ = (
        Index("idx_discounts_valid_from_until", "valid_from", "valid_until"),
        Index("idx_discounts_active_valid", "is_active", "valid_from", "valid_until"),
        Index("idx_discounts_coupon_code", "coupon_code"),
        CheckConstraint("discount_value >= 0", name="ck_discount_value_positive"),
        CheckConstraint("valid_until IS NULL OR valid_until > valid_from", name="ck_discount_validity"),
    )


class Promotion(Base, LoggerMixin):
    """Promotion model for campaigns and offers."""
    
    __tablename__ = "promotions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    platform_id: Mapped[int] = mapped_column(Integer, ForeignKey("platforms.id"), nullable=False, index=True)
    
    # Promotion details
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    promotion_type: Mapped[str] = mapped_column(String(50), nullable=False)  # flash_sale, festival, clearance, etc.
    
    # Validity
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    
    # Targeting
    applicable_categories: Mapped[Optional[list]] = mapped_column(JSONB)
    applicable_brands: Mapped[Optional[list]] = mapped_column(JSONB)
    applicable_products: Mapped[Optional[list]] = mapped_column(JSONB)
    min_order_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    
    # Metadata
    banner_image_url: Mapped[Optional[str]] = mapped_column(String(500))
    terms_conditions: Mapped[Optional[str]] = mapped_column(Text)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    platform = relationship("Platform")
    discounts = relationship("Discount", back_populates="promotion")
    
    __table_args__ = (
        Index("idx_promotions_platform_active", "platform_id", "is_active"),
        Index("idx_promotions_start_end_date", "start_date", "end_date"),
        CheckConstraint("end_date > start_date", name="ck_promotion_dates"),
    )


class Coupon(Base, LoggerMixin):
    """Coupon model for promotional codes."""
    
    __tablename__ = "coupons"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    platform_id: Mapped[int] = mapped_column(Integer, ForeignKey("platforms.id"), nullable=False, index=True)
    
    # Coupon details
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    discount_type: Mapped[str] = mapped_column(String(20), nullable=False)  # percentage, fixed
    discount_value: Mapped[float] = mapped_column(Float, nullable=False)
    max_discount_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    
    # Conditions
    min_order_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    applicable_categories: Mapped[Optional[list]] = mapped_column(JSONB)
    applicable_brands: Mapped[Optional[list]] = mapped_column(JSONB)
    
    # Validity
    valid_from: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    
    # Usage
    usage_limit: Mapped[Optional[int]] = mapped_column(Integer)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    is_first_time_only: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Metadata
    terms_conditions: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    platform = relationship("Platform")
    
    __table_args__ = (
        Index("idx_coupons_platform_active", "platform_id", "is_active"),
        Index("idx_coupons_valid_from_until", "valid_from", "valid_until"),
        CheckConstraint("discount_type IN ('percentage', 'fixed')", name="ck_coupon_discount_type"),
        CheckConstraint("discount_value >= 0", name="ck_coupon_discount_value"),
        CheckConstraint("valid_until IS NULL OR valid_until > valid_from", name="ck_coupon_validity"),
    )


class PriceAlert(Base, LoggerMixin):
    """Price alert model for user notifications."""
    
    __tablename__ = "price_alerts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    platform_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("platforms.id"), index=True)
    
    # Alert conditions
    target_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    alert_type: Mapped[str] = mapped_column(String(20), nullable=False)  # below_price, percentage_drop, price_increase
    threshold_value: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_triggered: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Notification
    notification_email: Mapped[bool] = mapped_column(Boolean, default=True)
    notification_push: Mapped[bool] = mapped_column(Boolean, default=False)
    notification_sms: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    product = relationship("Product")
    platform = relationship("Platform")
    
    __table_args__ = (
        Index("idx_price_alerts_user_active", "user_id", "is_active"),
        Index("idx_price_alerts_product_platform", "product_id", "platform_id"),
        Index("idx_price_alerts_triggered", "is_triggered", "triggered_at"),
        CheckConstraint("alert_type IN ('below_price', 'percentage_drop', 'price_increase')", name="ck_alert_type"),
        CheckConstraint("target_price >= 0", name="ck_target_price_positive"),
    ) 