"""User models for the price comparison platform."""

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


class User(Base, LoggerMixin):
    """User model."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Authentication
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Basic information
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    username: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    # Timestamps
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    phone_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    preferences = relationship("UserPreference", back_populates="user")
    searches = relationship("UserSearch", back_populates="user")
    queries = relationship("UserQuery", back_populates="user")
    alerts = relationship("UserAlert", back_populates="user")
    price_alerts = relationship("PriceAlert", back_populates="user")
    
    __table_args__ = (
        Index("idx_users_active_verified", "is_active", "is_verified"),
        Index("idx_users_premium", "is_premium", "is_active"),
        Index("idx_users_last_login", "last_login_at"),
    )


class UserProfile(Base, LoggerMixin):
    """User profile model."""
    
    __tablename__ = "user_profiles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Personal information
    date_of_birth: Mapped[Optional[datetime]] = mapped_column(DateTime)
    gender: Mapped[Optional[str]] = mapped_column(String(20))
    profile_picture: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Location
    address: Mapped[Optional[str]] = mapped_column(Text)
    city: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    state: Mapped[Optional[str]] = mapped_column(String(100))
    country: Mapped[Optional[str]] = mapped_column(String(100), default="India")
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    
    # Preferences
    preferred_platforms: Mapped[Optional[list]] = mapped_column(JSONB)
    preferred_categories: Mapped[Optional[list]] = mapped_column(JSONB)
    preferred_brands: Mapped[Optional[list]] = mapped_column(JSONB)
    budget_range: Mapped[Optional[dict]] = mapped_column(JSONB)  # min, max
    
    # Communication preferences
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    push_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    sms_notifications: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Privacy settings
    profile_visibility: Mapped[str] = mapped_column(String(20), default="private")  # public, private, friends
    data_sharing: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="profile")
    
    __table_args__ = (
        Index("idx_user_profiles_city", "city"),
        Index("idx_user_profiles_location", "latitude", "longitude"),
        UniqueConstraint("user_id", name="uq_user_profile"),
        CheckConstraint("gender IN ('male', 'female', 'other', 'prefer_not_to_say')", name="ck_gender"),
        CheckConstraint("profile_visibility IN ('public', 'private', 'friends')", name="ck_profile_visibility"),
    )


class UserPreference(Base, LoggerMixin):
    """User preference model."""
    
    __tablename__ = "user_preferences"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Preference type
    preference_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # platform, category, brand, price_range, etc.
    preference_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    preference_value: Mapped[Optional[str]] = mapped_column(String(500))
    preference_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Priority and weight
    priority: Mapped[int] = mapped_column(Integer, default=1)  # 1-10, higher is more important
    weight: Mapped[float] = mapped_column(Float, default=1.0)  # 0.0-1.0
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="preferences")
    
    __table_args__ = (
        Index("idx_user_preferences_type_key", "preference_type", "preference_key"),
        Index("idx_user_preferences_priority", "priority", "is_active"),
        UniqueConstraint("user_id", "preference_type", "preference_key", name="uq_user_preference"),
        CheckConstraint("priority >= 1 AND priority <= 10", name="ck_priority_range"),
        CheckConstraint("weight >= 0.0 AND weight <= 1.0", name="ck_weight_range"),
    )


class UserSearch(Base, LoggerMixin):
    """User search history model."""
    
    __tablename__ = "user_searches"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Search details
    query: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    search_type: Mapped[str] = mapped_column(String(50), default="text", index=True)  # text, voice, image, filter
    filters: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Results
    total_results: Mapped[Optional[int]] = mapped_column(Integer)
    results_viewed: Mapped[Optional[int]] = mapped_column(Integer)
    results_clicked: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Performance
    search_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    cache_hit: Mapped[Optional[bool]] = mapped_column(Boolean)
    
    # Context
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    location: Mapped[Optional[dict]] = mapped_column(JSONB)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    
    # Timestamp
    searched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="searches")
    
    __table_args__ = (
        Index("idx_user_searches_user_time", "user_id", "searched_at"),
        Index("idx_user_searches_query", "query"),
        Index("idx_user_searches_type", "search_type", "searched_at"),
        CheckConstraint("search_type IN ('text', 'voice', 'image', 'filter', 'natural_language')", name="ck_search_type"),
    )


class UserQuery(Base, LoggerMixin):
    """User natural language query model."""
    
    __tablename__ = "user_queries"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Query details
    query: Mapped[str] = mapped_column(Text, nullable=False)
    query_type: Mapped[str] = mapped_column(String(50), default="comparison", index=True)  # comparison, search, recommendation, alert
    intent: Mapped[Optional[str]] = mapped_column(String(100), index=True)  # price_comparison, product_search, etc.
    
    # Processing
    processed_query: Mapped[Optional[str]] = mapped_column(Text)
    sql_generated: Mapped[Optional[str]] = mapped_column(Text)
    tables_used: Mapped[Optional[list]] = mapped_column(JSONB)
    
    # Results
    result_count: Mapped[Optional[int]] = mapped_column(Integer)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    success: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # User feedback
    rating: Mapped[Optional[int]] = mapped_column(Integer)  # 1-5 stars
    feedback: Mapped[Optional[str]] = mapped_column(Text)
    was_helpful: Mapped[Optional[bool]] = mapped_column(Boolean)
    
    # Context
    session_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    
    # Timestamp
    queried_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="queries")
    
    __table_args__ = (
        Index("idx_user_queries_user_time", "user_id", "queried_at"),
        Index("idx_user_queries_type_intent", "query_type", "intent"),
        Index("idx_user_queries_success", "success", "queried_at"),
        CheckConstraint("query_type IN ('comparison', 'search', 'recommendation', 'alert', 'analytics')", name="ck_query_type"),
        CheckConstraint("rating IS NULL OR (rating >= 1 AND rating <= 5)", name="ck_rating_range"),
    )


class UserAlert(Base, LoggerMixin):
    """User alert model for notifications."""
    
    __tablename__ = "user_alerts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Alert details
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # price_drop, stock_alert, new_product, etc.
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Target information
    product_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("products.id"), index=True)
    platform_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("platforms.id"), index=True)
    category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.id"), index=True)
    
    # Alert data
    alert_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    old_value: Mapped[Optional[str]] = mapped_column(String(100))
    new_value: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Status
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    priority: Mapped[str] = mapped_column(String(20), default="normal", index=True)  # low, normal, high, urgent
    
    # Delivery
    email_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    push_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    sms_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    archived_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="alerts")
    product = relationship("Product")
    platform = relationship("Platform")
    category = relationship("Category")
    
    __table_args__ = (
        Index("idx_user_alerts_user_read", "user_id", "is_read"),
        Index("idx_user_alerts_type_priority", "alert_type", "priority"),
        Index("idx_user_alerts_created_at", "created_at"),
        CheckConstraint("alert_type IN ('price_drop', 'stock_alert', 'new_product', 'discount_alert', 'delivery_alert', 'system_alert')", name="ck_alert_type"),
        CheckConstraint("priority IN ('low', 'normal', 'high', 'urgent')", name="ck_priority"),
    ) 