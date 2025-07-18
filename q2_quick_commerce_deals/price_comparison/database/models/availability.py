"""Availability models for the price comparison platform."""

from datetime import datetime, time
from typing import Optional
from sqlalchemy import (
    Integer, String, Text, Boolean, DateTime, Float, 
    ForeignKey, Index, UniqueConstraint, CheckConstraint, Time
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from ..base import Base
from ..core.logging import LoggerMixin


class Availability(Base, LoggerMixin):
    """Product availability model."""
    
    __tablename__ = "availability"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    platform_id: Mapped[int] = mapped_column(Integer, ForeignKey("platforms.id"), nullable=False, index=True)
    variant_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("product_variants.id"), index=True)
    
    # Availability status
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    availability_status: Mapped[str] = mapped_column(String(50), default="in_stock", index=True)  # in_stock, out_of_stock, limited, coming_soon
    stock_quantity: Mapped[Optional[int]] = mapped_column(Integer)
    min_order_quantity: Mapped[Optional[int]] = mapped_column(Integer, default=1)
    max_order_quantity: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Delivery information
    delivery_time_min: Mapped[Optional[int]] = mapped_column(Integer)  # minutes
    delivery_time_max: Mapped[Optional[int]] = mapped_column(Integer)  # minutes
    delivery_slots_available: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Restrictions
    is_restricted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    restriction_reason: Mapped[Optional[str]] = mapped_column(String(200))
    age_restriction: Mapped[Optional[int]] = mapped_column(Integer)  # minimum age
    
    # Metadata
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    source_url: Mapped[Optional[str]] = mapped_column(String(500))
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="availability")
    platform = relationship("Platform")
    variant = relationship("ProductVariant")
    inventory = relationship("Inventory", back_populates="availability")
    stock_levels = relationship("StockLevel", back_populates="availability")
    
    __table_args__ = (
        Index("idx_availability_product_platform", "product_id", "platform_id"),
        Index("idx_availability_status_available", "availability_status", "is_available"),
        Index("idx_availability_last_updated", "last_updated"),
        UniqueConstraint("product_id", "platform_id", "variant_id", name="uq_availability_product_platform_variant"),
        CheckConstraint("delivery_time_max IS NULL OR delivery_time_max >= delivery_time_min", name="ck_delivery_time"),
        CheckConstraint("max_order_quantity IS NULL OR max_order_quantity >= min_order_quantity", name="ck_order_quantity"),
    )


class Inventory(Base, LoggerMixin):
    """Inventory tracking model."""
    
    __tablename__ = "inventory"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    availability_id: Mapped[int] = mapped_column(Integer, ForeignKey("availability.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    platform_id: Mapped[int] = mapped_column(Integer, ForeignKey("platforms.id"), nullable=False, index=True)
    
    # Inventory details
    warehouse_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    location_code: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    current_stock: Mapped[int] = mapped_column(Integer, default=0)
    reserved_stock: Mapped[int] = mapped_column(Integer, default=0)
    available_stock: Mapped[int] = mapped_column(Integer, default=0)
    
    # Stock thresholds
    low_stock_threshold: Mapped[Optional[int]] = mapped_column(Integer)
    reorder_point: Mapped[Optional[int]] = mapped_column(Integer)
    max_stock_level: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    availability = relationship("Availability", back_populates="inventory")
    product = relationship("Product")
    platform = relationship("Platform")
    
    __table_args__ = (
        Index("idx_inventory_product_platform", "product_id", "platform_id"),
        Index("idx_inventory_warehouse_location", "warehouse_id", "location_code"),
        Index("idx_inventory_stock_levels", "current_stock", "available_stock"),
        CheckConstraint("current_stock >= 0", name="ck_current_stock_positive"),
        CheckConstraint("reserved_stock >= 0", name="ck_reserved_stock_positive"),
        CheckConstraint("available_stock >= 0", name="ck_available_stock_positive"),
        CheckConstraint("available_stock <= current_stock", name="ck_available_stock_limit"),
    )


class StockLevel(Base, LoggerMixin):
    """Stock level history tracking."""
    
    __tablename__ = "stock_levels"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    availability_id: Mapped[int] = mapped_column(Integer, ForeignKey("availability.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    platform_id: Mapped[int] = mapped_column(Integer, ForeignKey("platforms.id"), nullable=False, index=True)
    
    # Stock snapshot
    current_stock: Mapped[int] = mapped_column(Integer, nullable=False)
    reserved_stock: Mapped[int] = mapped_column(Integer, default=0)
    available_stock: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Change tracking
    stock_change: Mapped[Optional[int]] = mapped_column(Integer)
    change_reason: Mapped[Optional[str]] = mapped_column(String(100))  # purchase, return, adjustment, etc.
    
    # Timestamp
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    availability = relationship("Availability", back_populates="stock_levels")
    product = relationship("Product")
    platform = relationship("Platform")
    
    __table_args__ = (
        Index("idx_stock_levels_product_platform", "product_id", "platform_id"),
        Index("idx_stock_levels_recorded_at", "recorded_at"),
        Index("idx_stock_levels_stock_change", "stock_change"),
    )


class DeliverySlot(Base, LoggerMixin):
    """Delivery slot model."""
    
    __tablename__ = "delivery_slots"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    platform_id: Mapped[int] = mapped_column(Integer, ForeignKey("platforms.id"), nullable=False, index=True)
    delivery_zone_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("delivery_zones.id"), index=True)
    
    # Slot details
    slot_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    slot_type: Mapped[str] = mapped_column(String(50), nullable=False)  # express, standard, scheduled
    delivery_fee: Mapped[Optional[float]] = mapped_column(Float, default=0)
    
    # Capacity
    max_orders: Mapped[Optional[int]] = mapped_column(Integer)
    current_orders: Mapped[int] = mapped_column(Integer, default=0)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    
    # Restrictions
    min_order_value: Mapped[Optional[float]] = mapped_column(Float)
    max_order_value: Mapped[Optional[float]] = mapped_column(Float)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    platform = relationship("Platform")
    delivery_zone = relationship("DeliveryZone", back_populates="delivery_slots")
    
    __table_args__ = (
        Index("idx_delivery_slots_platform_date", "platform_id", "slot_date"),
        Index("idx_delivery_slots_available", "is_available", "slot_date"),
        Index("idx_delivery_slots_time_range", "start_time", "end_time"),
        CheckConstraint("end_time > start_time", name="ck_delivery_slot_time"),
        CheckConstraint("current_orders >= 0", name="ck_current_orders_positive"),
        CheckConstraint("max_orders IS NULL OR current_orders <= max_orders", name="ck_orders_limit"),
    )


class DeliveryZone(Base, LoggerMixin):
    """Delivery zone model."""
    
    __tablename__ = "delivery_zones"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    platform_id: Mapped[int] = mapped_column(Integer, ForeignKey("platforms.id"), nullable=False, index=True)
    
    # Zone details
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Geographic information
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(100), default="India", nullable=False)
    postal_codes: Mapped[Optional[list]] = mapped_column(JSONB)
    coordinates: Mapped[Optional[dict]] = mapped_column(JSONB)  # lat, lng, radius
    
    # Delivery settings
    base_delivery_fee: Mapped[float] = mapped_column(Float, default=0)
    free_delivery_threshold: Mapped[Optional[float]] = mapped_column(Float)
    max_delivery_time: Mapped[Optional[int]] = mapped_column(Integer)  # minutes
    min_delivery_time: Mapped[Optional[int]] = mapped_column(Integer)  # minutes
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_express_available: Mapped[bool] = mapped_column(Boolean, default=True)
    is_scheduled_available: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    platform = relationship("Platform")
    delivery_slots = relationship("DeliverySlot", back_populates="delivery_zone")
    serviceability = relationship("Serviceability", back_populates="delivery_zone")
    
    __table_args__ = (
        Index("idx_delivery_zones_platform_city", "platform_id", "city"),
        Index("idx_delivery_zones_active", "is_active", "platform_id"),
        UniqueConstraint("platform_id", "code", name="uq_delivery_zone_platform_code"),
    )


class Serviceability(Base, LoggerMixin):
    """Serviceability model for delivery zones and products."""
    
    __tablename__ = "serviceability"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    platform_id: Mapped[int] = mapped_column(Integer, ForeignKey("platforms.id"), nullable=False, index=True)
    delivery_zone_id: Mapped[int] = mapped_column(Integer, ForeignKey("delivery_zones.id"), nullable=False, index=True)
    
    # Serviceability status
    is_serviceable: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    delivery_fee: Mapped[Optional[float]] = mapped_column(Float)
    delivery_time_min: Mapped[Optional[int]] = mapped_column(Integer)  # minutes
    delivery_time_max: Mapped[Optional[int]] = mapped_column(Integer)  # minutes
    
    # Restrictions
    min_order_value: Mapped[Optional[float]] = mapped_column(Float)
    max_order_value: Mapped[Optional[float]] = mapped_column(Float)
    quantity_restrictions: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Special conditions
    is_express_available: Mapped[bool] = mapped_column(Boolean, default=True)
    is_scheduled_available: Mapped[bool] = mapped_column(Boolean, default=True)
    special_instructions: Mapped[Optional[str]] = mapped_column(Text)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product")
    platform = relationship("Platform")
    delivery_zone = relationship("DeliveryZone", back_populates="serviceability")
    
    __table_args__ = (
        Index("idx_serviceability_product_platform", "product_id", "platform_id"),
        Index("idx_serviceability_zone_active", "delivery_zone_id", "is_active"),
        Index("idx_serviceability_serviceable", "is_serviceable", "is_active"),
        UniqueConstraint("product_id", "platform_id", "delivery_zone_id", name="uq_serviceability_product_platform_zone"),
        CheckConstraint("delivery_time_max IS NULL OR delivery_time_max >= delivery_time_min", name="ck_serviceability_delivery_time"),
    ) 