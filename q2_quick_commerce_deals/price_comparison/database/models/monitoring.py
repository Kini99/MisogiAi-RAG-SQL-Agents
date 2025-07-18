"""Monitoring models for the price comparison platform."""

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


class SystemMetrics(Base, LoggerMixin):
    """System metrics model."""
    
    __tablename__ = "system_metrics"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # System information
    hostname: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    service_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    instance_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    
    # CPU metrics
    cpu_usage_percent: Mapped[float] = mapped_column(Float, nullable=False)
    cpu_count: Mapped[int] = mapped_column(Integer, nullable=False)
    cpu_load_1min: Mapped[Optional[float]] = mapped_column(Float)
    cpu_load_5min: Mapped[Optional[float]] = mapped_column(Float)
    cpu_load_15min: Mapped[Optional[float]] = mapped_column(Float)
    
    # Memory metrics
    memory_total_gb: Mapped[float] = mapped_column(Float, nullable=False)
    memory_used_gb: Mapped[float] = mapped_column(Float, nullable=False)
    memory_available_gb: Mapped[float] = mapped_column(Float, nullable=False)
    memory_usage_percent: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Disk metrics
    disk_total_gb: Mapped[Optional[float]] = mapped_column(Float)
    disk_used_gb: Mapped[Optional[float]] = mapped_column(Float)
    disk_available_gb: Mapped[Optional[float]] = mapped_column(Float)
    disk_usage_percent: Mapped[Optional[float]] = mapped_column(Float)
    
    # Network metrics
    network_bytes_sent: Mapped[Optional[int]] = mapped_column(Integer)
    network_bytes_recv: Mapped[Optional[int]] = mapped_column(Integer)
    network_packets_sent: Mapped[Optional[int]] = mapped_column(Integer)
    network_packets_recv: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Process metrics
    process_count: Mapped[Optional[int]] = mapped_column(Integer)
    thread_count: Mapped[Optional[int]] = mapped_column(Integer)
    open_files: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Timestamp
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index("idx_system_metrics_host_service", "hostname", "service_name"),
        Index("idx_system_metrics_recorded_at", "recorded_at"),
        Index("idx_system_metrics_cpu_memory", "cpu_usage_percent", "memory_usage_percent"),
        CheckConstraint("cpu_usage_percent >= 0 AND cpu_usage_percent <= 100", name="ck_cpu_usage"),
        CheckConstraint("memory_usage_percent >= 0 AND memory_usage_percent <= 100", name="ck_memory_usage"),
        CheckConstraint("disk_usage_percent IS NULL OR (disk_usage_percent >= 0 AND disk_usage_percent <= 100)", name="ck_disk_usage"),
    )


class DatabaseMetrics(Base, LoggerMixin):
    """Database metrics model."""
    
    __tablename__ = "database_metrics"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Connection metrics
    active_connections: Mapped[int] = mapped_column(Integer, nullable=False)
    max_connections: Mapped[int] = mapped_column(Integer, nullable=False)
    connection_usage_percent: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Query metrics
    queries_per_second: Mapped[Optional[float]] = mapped_column(Float)
    slow_queries_per_second: Mapped[Optional[float]] = mapped_column(Float)
    avg_query_time_ms: Mapped[Optional[float]] = mapped_column(Float)
    max_query_time_ms: Mapped[Optional[float]] = mapped_column(Float)
    
    # Cache metrics
    cache_hit_ratio: Mapped[Optional[float]] = mapped_column(Float)
    cache_miss_ratio: Mapped[Optional[float]] = mapped_column(Float)
    buffer_cache_hit_ratio: Mapped[Optional[float]] = mapped_column(Float)
    
    # Storage metrics
    database_size_gb: Mapped[Optional[float]] = mapped_column(Float)
    table_sizes: Mapped[Optional[dict]] = mapped_column(JSONB)
    index_sizes: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Lock metrics
    active_locks: Mapped[Optional[int]] = mapped_column(Integer)
    lock_wait_time_ms: Mapped[Optional[float]] = mapped_column(Float)
    deadlocks: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Transaction metrics
    active_transactions: Mapped[Optional[int]] = mapped_column(Integer)
    transactions_per_second: Mapped[Optional[float]] = mapped_column(Float)
    rollback_ratio: Mapped[Optional[float]] = mapped_column(Float)
    
    # Timestamp
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index("idx_database_metrics_recorded_at", "recorded_at"),
        Index("idx_database_metrics_connections", "active_connections", "connection_usage_percent"),
        Index("idx_database_metrics_performance", "avg_query_time_ms", "queries_per_second"),
        CheckConstraint("connection_usage_percent >= 0 AND connection_usage_percent <= 100", name="ck_connection_usage"),
        CheckConstraint("cache_hit_ratio IS NULL OR (cache_hit_ratio >= 0 AND cache_hit_ratio <= 100)", name="ck_cache_hit_ratio"),
    )


class CacheMetrics(Base, LoggerMixin):
    """Cache metrics model."""
    
    __tablename__ = "cache_metrics"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Cache information
    cache_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    cache_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # redis, memory, disk
    
    # Performance metrics
    hit_count: Mapped[int] = mapped_column(Integer, default=0)
    miss_count: Mapped[int] = mapped_column(Integer, default=0)
    hit_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Memory metrics
    memory_used_mb: Mapped[Optional[float]] = mapped_column(Float)
    memory_max_mb: Mapped[Optional[float]] = mapped_column(Float)
    memory_usage_percent: Mapped[Optional[float]] = mapped_column(Float)
    
    # Key metrics
    total_keys: Mapped[Optional[int]] = mapped_column(Integer)
    expired_keys: Mapped[Optional[int]] = mapped_column(Integer)
    evicted_keys: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Operation metrics
    operations_per_second: Mapped[Optional[float]] = mapped_column(Float)
    avg_response_time_ms: Mapped[Optional[float]] = mapped_column(Float)
    max_response_time_ms: Mapped[Optional[float]] = mapped_column(Float)
    
    # Error metrics
    connection_errors: Mapped[int] = mapped_column(Integer, default=0)
    timeout_errors: Mapped[int] = mapped_column(Integer, default=0)
    other_errors: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamp
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index("idx_cache_metrics_name_type", "cache_name", "cache_type"),
        Index("idx_cache_metrics_recorded_at", "recorded_at"),
        Index("idx_cache_metrics_hit_ratio", "hit_ratio"),
        CheckConstraint("hit_ratio >= 0 AND hit_ratio <= 100", name="ck_hit_ratio"),
        CheckConstraint("memory_usage_percent IS NULL OR (memory_usage_percent >= 0 AND memory_usage_percent <= 100)", name="ck_memory_usage_percent"),
    )


class QueryMetrics(Base, LoggerMixin):
    """Query metrics model for detailed query performance tracking."""
    
    __tablename__ = "query_metrics"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Query identification
    query_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    query_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # natural_language, sql, api
    query_category: Mapped[Optional[str]] = mapped_column(String(100), index=True)  # price_comparison, product_search, etc.
    
    # Performance metrics
    execution_count: Mapped[int] = mapped_column(Integer, default=0)
    total_execution_time_ms: Mapped[float] = mapped_column(Float, default=0)
    avg_execution_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    min_execution_time_ms: Mapped[Optional[float]] = mapped_column(Float)
    max_execution_time_ms: Mapped[Optional[float]] = mapped_column(Float)
    
    # Resource usage
    avg_memory_usage_mb: Mapped[Optional[float]] = mapped_column(Float)
    avg_cpu_usage_percent: Mapped[Optional[float]] = mapped_column(Float)
    avg_rows_processed: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Cache performance
    cache_hits: Mapped[int] = mapped_column(Integer, default=0)
    cache_misses: Mapped[int] = mapped_column(Integer, default=0)
    cache_hit_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Error tracking
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    success_rate: Mapped[float] = mapped_column(Float, nullable=False)
    last_error: Mapped[Optional[str]] = mapped_column(Text)
    last_error_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Optimization
    optimization_applied: Mapped[bool] = mapped_column(Boolean, default=False)
    optimization_improvement_percent: Mapped[Optional[float]] = mapped_column(Float)
    
    # Timestamps
    first_executed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_executed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_query_metrics_hash_type", "query_hash", "query_type"),
        Index("idx_query_metrics_performance", "avg_execution_time_ms", "execution_count"),
        Index("idx_query_metrics_success_rate", "success_rate", "execution_count"),
        Index("idx_query_metrics_last_executed", "last_executed_at"),
        CheckConstraint("success_rate >= 0 AND success_rate <= 100", name="ck_success_rate"),
        CheckConstraint("cache_hit_ratio >= 0 AND cache_hit_ratio <= 100", name="ck_cache_hit_ratio"),
        CheckConstraint("avg_execution_time_ms >= 0", name="ck_avg_execution_time"),
    )


class ErrorLog(Base, LoggerMixin):
    """Error log model."""
    
    __tablename__ = "error_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Error information
    error_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    error_code: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    error_level: Mapped[str] = mapped_column(String(20), default="ERROR", index=True)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # Context
    service_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    function_name: Mapped[Optional[str]] = mapped_column(String(200))
    line_number: Mapped[Optional[int]] = mapped_column(Integer)
    stack_trace: Mapped[Optional[str]] = mapped_column(Text)
    
    # User context
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Request context
    request_method: Mapped[Optional[str]] = mapped_column(String(10))
    request_path: Mapped[Optional[str]] = mapped_column(String(500))
    request_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    
    # Additional data
    context_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    tags: Mapped[Optional[list]] = mapped_column(JSONB)
    
    # Timestamp
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User")
    
    __table_args__ = (
        Index("idx_error_logs_type_level", "error_type", "error_level"),
        Index("idx_error_logs_service_time", "service_name", "occurred_at"),
        Index("idx_error_logs_user_time", "user_id", "occurred_at"),
        CheckConstraint("error_level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')", name="ck_error_level"),
    )


class PerformanceLog(Base, LoggerMixin):
    """Performance log model for detailed performance tracking."""
    
    __tablename__ = "performance_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Operation information
    operation_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # api_call, database_query, cache_operation, etc.
    service_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Performance metrics
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Resource usage
    memory_usage_mb: Mapped[Optional[float]] = mapped_column(Float)
    cpu_usage_percent: Mapped[Optional[float]] = mapped_column(Float)
    io_operations: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Status
    success: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # Context
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    request_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    
    # Additional data
    parameters: Mapped[Optional[dict]] = mapped_column(JSONB)
    result_summary: Mapped[Optional[str]] = mapped_column(Text)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Relationships
    user = relationship("User")
    
    __table_args__ = (
        Index("idx_performance_logs_operation", "operation_name", "operation_type"),
        Index("idx_performance_logs_duration", "duration_ms"),
        Index("idx_performance_logs_service_time", "service_name", "start_time"),
        Index("idx_performance_logs_success", "success", "start_time"),
        CheckConstraint("duration_ms >= 0", name="ck_duration_positive"),
        CheckConstraint("end_time >= start_time", name="ck_time_order"),
    ) 