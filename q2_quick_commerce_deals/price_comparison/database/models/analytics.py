"""Analytics models for the price comparison platform."""

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


class QueryLog(Base, LoggerMixin):
    """Query log model for tracking all queries."""
    
    __tablename__ = "query_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Query information
    query_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    original_query: Mapped[str] = mapped_column(Text, nullable=False)
    processed_query: Mapped[Optional[str]] = mapped_column(Text)
    query_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # natural_language, sql, api
    
    # User context
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Processing details
    intent_detected: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    entities_extracted: Mapped[Optional[dict]] = mapped_column(JSONB)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # Performance metrics
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    total_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Cache information
    cache_hit: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    cache_key: Mapped[Optional[str]] = mapped_column(String(200))
    
    # Status
    success: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    error_code: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User")
    results = relationship("QueryResult", back_populates="query_log")
    performance = relationship("QueryPerformance", back_populates="query_log")
    
    __table_args__ = (
        Index("idx_query_logs_hash_type", "query_hash", "query_type"),
        Index("idx_query_logs_user_time", "user_id", "created_at"),
        Index("idx_query_logs_success_time", "success", "created_at"),
        Index("idx_query_logs_cache_hit", "cache_hit", "created_at"),
    )


class QueryResult(Base, LoggerMixin):
    """Query result model for storing query results."""
    
    __tablename__ = "query_results"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    query_log_id: Mapped[int] = mapped_column(Integer, ForeignKey("query_logs.id"), nullable=False, index=True)
    
    # Result information
    result_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # table, chart, text, json
    result_format: Mapped[str] = mapped_column(String(20), default="json", index=True)  # json, csv, xml, html
    
    # Result data
    result_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    result_summary: Mapped[Optional[str]] = mapped_column(Text)
    result_metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Statistics
    row_count: Mapped[Optional[int]] = mapped_column(Integer)
    column_count: Mapped[Optional[int]] = mapped_column(Integer)
    data_size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Quality metrics
    data_freshness_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    query_log = relationship("QueryLog", back_populates="results")
    
    __table_args__ = (
        Index("idx_query_results_type_format", "result_type", "result_format"),
        Index("idx_query_results_created_at", "created_at"),
    )


class QueryPerformance(Base, LoggerMixin):
    """Query performance tracking model."""
    
    __tablename__ = "query_performance"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    query_log_id: Mapped[int] = mapped_column(Integer, ForeignKey("query_logs.id"), nullable=False, index=True)
    
    # Performance metrics
    parsing_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    planning_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    total_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Resource usage
    memory_usage_mb: Mapped[Optional[float]] = mapped_column(Float)
    cpu_usage_percent: Mapped[Optional[float]] = mapped_column(Float)
    io_operations: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Database metrics
    tables_accessed: Mapped[Optional[list]] = mapped_column(JSONB)
    indexes_used: Mapped[Optional[list]] = mapped_column(JSONB)
    rows_scanned: Mapped[Optional[int]] = mapped_column(Integer)
    rows_returned: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Optimization
    query_optimized: Mapped[bool] = mapped_column(Boolean, default=False)
    optimization_applied: Mapped[Optional[list]] = mapped_column(JSONB)
    
    # Timestamp
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    query_log = relationship("QueryLog", back_populates="performance")
    
    __table_args__ = (
        Index("idx_query_performance_total_time", "total_time_ms"),
        Index("idx_query_performance_recorded_at", "recorded_at"),
        CheckConstraint("total_time_ms >= 0", name="ck_total_time_positive"),
    )


class SearchAnalytics(Base, LoggerMixin):
    """Search analytics model."""
    
    __tablename__ = "search_analytics"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Search metrics
    total_searches: Mapped[int] = mapped_column(Integer, default=0)
    unique_searches: Mapped[int] = mapped_column(Integer, default=0)
    successful_searches: Mapped[int] = mapped_column(Integer, default=0)
    failed_searches: Mapped[int] = mapped_column(Integer, default=0)
    
    # Performance metrics
    avg_search_time_ms: Mapped[Optional[float]] = mapped_column(Float)
    avg_results_count: Mapped[Optional[float]] = mapped_column(Float)
    cache_hit_rate: Mapped[Optional[float]] = mapped_column(Float)
    
    # Popular searches
    top_searches: Mapped[Optional[list]] = mapped_column(JSONB)
    trending_searches: Mapped[Optional[list]] = mapped_column(JSONB)
    failed_searches_list: Mapped[Optional[list]] = mapped_column(JSONB)
    
    # User engagement
    avg_results_viewed: Mapped[Optional[float]] = mapped_column(Float)
    avg_results_clicked: Mapped[Optional[float]] = mapped_column(Float)
    conversion_rate: Mapped[Optional[float]] = mapped_column(Float)
    
    # Time period
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    period_type: Mapped[str] = mapped_column(String(20), default="hour", index=True)  # minute, hour, day, week, month
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_search_analytics_period", "period_start", "period_end"),
        Index("idx_search_analytics_type", "period_type", "period_start"),
        CheckConstraint("period_end > period_start", name="ck_period_dates"),
        CheckConstraint("period_type IN ('minute', 'hour', 'day', 'week', 'month')", name="ck_period_type"),
    )


class PriceAnalytics(Base, LoggerMixin):
    """Price analytics model."""
    
    __tablename__ = "price_analytics"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Product and platform
    product_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("products.id"), index=True)
    platform_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("platforms.id"), index=True)
    category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.id"), index=True)
    
    # Price metrics
    avg_price: Mapped[Optional[float]] = mapped_column(Float)
    min_price: Mapped[Optional[float]] = mapped_column(Float)
    max_price: Mapped[Optional[float]] = mapped_column(Float)
    price_variance: Mapped[Optional[float]] = mapped_column(Float)
    price_volatility: Mapped[Optional[float]] = mapped_column(Float)
    
    # Discount metrics
    avg_discount_percentage: Mapped[Optional[float]] = mapped_column(Float)
    max_discount_percentage: Mapped[Optional[float]] = mapped_column(Float)
    discount_frequency: Mapped[Optional[float]] = mapped_column(Float)
    
    # Price changes
    price_increases: Mapped[int] = mapped_column(Integer, default=0)
    price_decreases: Mapped[int] = mapped_column(Integer, default=0)
    price_stable: Mapped[int] = mapped_column(Integer, default=0)
    
    # Market position
    price_rank: Mapped[Optional[int]] = mapped_column(Integer)
    price_percentile: Mapped[Optional[float]] = mapped_column(Float)
    is_cheapest: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_most_expensive: Mapped[Optional[bool]] = mapped_column(Boolean)
    
    # Time period
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # Metadata
    data_points: Mapped[int] = mapped_column(Integer, default=0)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product")
    platform = relationship("Platform")
    category = relationship("Category")
    
    __table_args__ = (
        Index("idx_price_analytics_product_platform", "product_id", "platform_id"),
        Index("idx_price_analytics_period", "period_start", "period_end"),
        Index("idx_price_analytics_avg_price", "avg_price"),
        CheckConstraint("period_end > period_start", name="ck_price_period_dates"),
    )


class PlatformAnalytics(Base, LoggerMixin):
    """Platform analytics model."""
    
    __tablename__ = "platform_analytics"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    platform_id: Mapped[int] = mapped_column(Integer, ForeignKey("platforms.id"), nullable=False, index=True)
    
    # Product coverage
    total_products: Mapped[int] = mapped_column(Integer, default=0)
    active_products: Mapped[int] = mapped_column(Integer, default=0)
    new_products: Mapped[int] = mapped_column(Integer, default=0)
    discontinued_products: Mapped[int] = mapped_column(Integer, default=0)
    
    # Pricing metrics
    avg_price: Mapped[Optional[float]] = mapped_column(Float)
    avg_discount_percentage: Mapped[Optional[float]] = mapped_column(Float)
    price_competitiveness_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # Availability metrics
    avg_availability_rate: Mapped[Optional[float]] = mapped_column(Float)
    avg_delivery_time_minutes: Mapped[Optional[float]] = mapped_column(Float)
    avg_delivery_fee: Mapped[Optional[float]] = mapped_column(Float)
    
    # Performance metrics
    data_freshness_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    sync_success_rate: Mapped[Optional[float]] = mapped_column(Float)
    avg_response_time_ms: Mapped[Optional[float]] = mapped_column(Float)
    
    # User engagement
    search_volume: Mapped[int] = mapped_column(Integer, default=0)
    click_through_rate: Mapped[Optional[float]] = mapped_column(Float)
    conversion_rate: Mapped[Optional[float]] = mapped_column(Float)
    
    # Time period
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # Metadata
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    platform = relationship("Platform")
    
    __table_args__ = (
        Index("idx_platform_analytics_platform_period", "platform_id", "period_start", "period_end"),
        Index("idx_platform_analytics_competitiveness", "price_competitiveness_score"),
        Index("idx_platform_analytics_availability", "avg_availability_rate"),
        CheckConstraint("period_end > period_start", name="ck_platform_period_dates"),
        CheckConstraint("sync_success_rate IS NULL OR (sync_success_rate >= 0 AND sync_success_rate <= 100)", name="ck_sync_success_rate"),
    )


class UserAnalytics(Base, LoggerMixin):
    """User analytics model."""
    
    __tablename__ = "user_analytics"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    
    # Usage metrics
    total_queries: Mapped[int] = mapped_column(Integer, default=0)
    successful_queries: Mapped[int] = mapped_column(Integer, default=0)
    failed_queries: Mapped[int] = mapped_column(Integer, default=0)
    unique_queries: Mapped[int] = mapped_column(Integer, default=0)
    
    # Search behavior
    avg_query_length: Mapped[Optional[float]] = mapped_column(Float)
    most_common_intents: Mapped[Optional[list]] = mapped_column(JSONB)
    preferred_platforms: Mapped[Optional[list]] = mapped_column(JSONB)
    preferred_categories: Mapped[Optional[list]] = mapped_column(JSONB)
    
    # Engagement metrics
    avg_session_duration_minutes: Mapped[Optional[float]] = mapped_column(Float)
    avg_queries_per_session: Mapped[Optional[float]] = mapped_column(Float)
    avg_results_viewed: Mapped[Optional[float]] = mapped_column(Float)
    avg_results_clicked: Mapped[Optional[float]] = mapped_column(Float)
    
    # Performance metrics
    avg_query_time_ms: Mapped[Optional[float]] = mapped_column(Float)
    cache_hit_rate: Mapped[Optional[float]] = mapped_column(Float)
    satisfaction_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # Time period
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # Metadata
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    
    __table_args__ = (
        Index("idx_user_analytics_user_period", "user_id", "period_start", "period_end"),
        Index("idx_user_analytics_satisfaction", "satisfaction_score"),
        Index("idx_user_analytics_engagement", "avg_session_duration_minutes"),
        CheckConstraint("period_end > period_start", name="ck_user_period_dates"),
        CheckConstraint("satisfaction_score IS NULL OR (satisfaction_score >= 0 AND satisfaction_score <= 5)", name="ck_satisfaction_score"),
    ) 