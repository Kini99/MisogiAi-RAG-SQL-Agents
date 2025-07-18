"""Integration models for the price comparison platform."""

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


class DataSource(Base, LoggerMixin):
    """Data source model for external integrations."""
    
    __tablename__ = "data_sources"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    platform_id: Mapped[int] = mapped_column(Integer, ForeignKey("platforms.id"), nullable=False, index=True)
    
    # Source information
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # api, web_scraping, csv, json, etc.
    source_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Authentication
    auth_type: Mapped[str] = mapped_column(String(50), default="none", index=True)  # none, api_key, oauth, basic
    auth_credentials: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Configuration
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    headers: Mapped[Optional[dict]] = mapped_column(JSONB)
    parameters: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Rate limiting
    rate_limit_requests: Mapped[Optional[int]] = mapped_column(Integer)
    rate_limit_period: Mapped[Optional[int]] = mapped_column(Integer)  # seconds
    current_rate_usage: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_healthy: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    last_health_check: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Performance
    avg_response_time_ms: Mapped[Optional[float]] = mapped_column(Float)
    success_rate: Mapped[Optional[float]] = mapped_column(Float)
    total_requests: Mapped[int] = mapped_column(Integer, default=0)
    successful_requests: Mapped[int] = mapped_column(Integer, default=0)
    
    # Metadata
    description: Mapped[Optional[str]] = mapped_column(Text)
    version: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    platform = relationship("Platform")
    data_syncs = relationship("DataSync", back_populates="data_source")
    
    __table_args__ = (
        Index("idx_data_sources_platform_type", "platform_id", "source_type"),
        Index("idx_data_sources_active_healthy", "is_active", "is_healthy"),
        Index("idx_data_sources_success_rate", "success_rate"),
        UniqueConstraint("platform_id", "name", name="uq_data_source_platform_name"),
        CheckConstraint("auth_type IN ('none', 'api_key', 'oauth', 'basic', 'bearer')", name="ck_auth_type"),
        CheckConstraint("source_type IN ('api', 'web_scraping', 'csv', 'json', 'xml', 'database', 'file')", name="ck_source_type"),
        CheckConstraint("success_rate IS NULL OR (success_rate >= 0 AND success_rate <= 100)", name="ck_success_rate"),
    )


class DataSync(Base, LoggerMixin):
    """Data synchronization model."""
    
    __tablename__ = "data_syncs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    data_source_id: Mapped[int] = mapped_column(Integer, ForeignKey("data_sources.id"), nullable=False, index=True)
    platform_id: Mapped[int] = mapped_column(Integer, ForeignKey("platforms.id"), nullable=False, index=True)
    
    # Sync information
    sync_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # full, incremental, real_time
    sync_status: Mapped[str] = mapped_column(String(50), default="pending", index=True)  # pending, running, completed, failed, cancelled
    
    # Progress tracking
    total_items: Mapped[Optional[int]] = mapped_column(Integer)
    processed_items: Mapped[int] = mapped_column(Integer, default=0)
    successful_items: Mapped[int] = mapped_column(Integer, default=0)
    failed_items: Mapped[int] = mapped_column(Integer, default=0)
    skipped_items: Mapped[int] = mapped_column(Integer, default=0)
    
    # Performance metrics
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    avg_items_per_second: Mapped[Optional[float]] = mapped_column(Float)
    
    # Data statistics
    data_size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    records_added: Mapped[int] = mapped_column(Integer, default=0)
    records_updated: Mapped[int] = mapped_column(Integer, default=0)
    records_deleted: Mapped[int] = mapped_column(Integer, default=0)
    
    # Error handling
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[Optional[str]] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    
    # Configuration
    sync_config: Mapped[Optional[dict]] = mapped_column(JSONB)
    filters: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    data_source = relationship("DataSource", back_populates="data_syncs")
    platform = relationship("Platform")
    validations = relationship("DataValidation", back_populates="data_sync")
    
    __table_args__ = (
        Index("idx_data_syncs_platform_status", "platform_id", "sync_status"),
        Index("idx_data_syncs_start_time", "start_time"),
        Index("idx_data_syncs_duration", "duration_seconds"),
        CheckConstraint("sync_type IN ('full', 'incremental', 'real_time', 'manual')", name="ck_sync_type"),
        CheckConstraint("sync_status IN ('pending', 'running', 'completed', 'failed', 'cancelled')", name="ck_sync_status"),
        CheckConstraint("processed_items >= 0", name="ck_processed_items"),
        CheckConstraint("successful_items >= 0", name="ck_successful_items"),
        CheckConstraint("failed_items >= 0", name="ck_failed_items"),
    )


class DataValidation(Base, LoggerMixin):
    """Data validation model."""
    
    __tablename__ = "data_validation"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    data_sync_id: Mapped[int] = mapped_column(Integer, ForeignKey("data_syncs.id"), nullable=False, index=True)
    
    # Validation information
    validation_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # schema, data_quality, business_rules, etc.
    validation_status: Mapped[str] = mapped_column(String(50), default="pending", index=True)  # pending, running, passed, failed
    
    # Validation metrics
    total_records: Mapped[int] = mapped_column(Integer, default=0)
    valid_records: Mapped[int] = mapped_column(Integer, default=0)
    invalid_records: Mapped[int] = mapped_column(Integer, default=0)
    warning_records: Mapped[int] = mapped_column(Integer, default=0)
    
    # Quality metrics
    completeness_score: Mapped[Optional[float]] = mapped_column(Float)
    accuracy_score: Mapped[Optional[float]] = mapped_column(Float)
    consistency_score: Mapped[Optional[float]] = mapped_column(Float)
    timeliness_score: Mapped[Optional[float]] = mapped_column(Float)
    overall_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # Validation rules
    rules_applied: Mapped[Optional[list]] = mapped_column(JSONB)
    validation_errors: Mapped[Optional[list]] = mapped_column(JSONB)
    validation_warnings: Mapped[Optional[list]] = mapped_column(JSONB)
    
    # Performance
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    data_sync = relationship("DataSync", back_populates="validations")
    
    __table_args__ = (
        Index("idx_data_validation_sync_status", "data_sync_id", "validation_status"),
        Index("idx_data_validation_overall_score", "overall_score"),
        Index("idx_data_validation_start_time", "start_time"),
        CheckConstraint("validation_type IN ('schema', 'data_quality', 'business_rules', 'format', 'range', 'custom')", name="ck_validation_type"),
        CheckConstraint("validation_status IN ('pending', 'running', 'passed', 'failed', 'warning')", name="ck_validation_status"),
        CheckConstraint("overall_score IS NULL OR (overall_score >= 0 AND overall_score <= 100)", name="ck_overall_score"),
    )


class IntegrationLog(Base, LoggerMixin):
    """Integration log model for tracking all integration activities."""
    
    __tablename__ = "integration_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    data_source_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("data_sources.id"), index=True)
    platform_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("platforms.id"), index=True)
    
    # Log information
    log_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # sync, validation, error, info, warning
    log_level: Mapped[str] = mapped_column(String(20), default="INFO", index=True)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # Message and context
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[Optional[dict]] = mapped_column(JSONB)
    context: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Performance metrics
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)
    memory_usage_mb: Mapped[Optional[float]] = mapped_column(Float)
    
    # Error information
    error_type: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    error_code: Mapped[Optional[str]] = mapped_column(String(50))
    stack_trace: Mapped[Optional[str]] = mapped_column(Text)
    
    # Request/Response data
    request_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    response_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    response_status: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    data_source = relationship("DataSource")
    platform = relationship("Platform")
    
    __table_args__ = (
        Index("idx_integration_logs_type_level", "log_type", "log_level"),
        Index("idx_integration_logs_platform_time", "platform_id", "created_at"),
        Index("idx_integration_logs_source_time", "data_source_id", "created_at"),
        CheckConstraint("log_type IN ('sync', 'validation', 'error', 'info', 'warning', 'debug')", name="ck_log_type"),
        CheckConstraint("log_level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')", name="ck_log_level"),
    )


class WebhookEvent(Base, LoggerMixin):
    """Webhook event model for external integrations."""
    
    __tablename__ = "webhook_events"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Event information
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True)
    
    # Payload
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    
    # Processing status
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)  # pending, processing, completed, failed, retry
    processing_attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    
    # Timing
    received_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    next_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True)
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    error_details: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Metadata
    headers: Mapped[Optional[dict]] = mapped_column(JSONB)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Priority
    priority: Mapped[str] = mapped_column(String(20), default="normal", index=True)  # low, normal, high, urgent
    
    __table_args__ = (
        Index("idx_webhook_events_type_source", "event_type", "event_source"),
        Index("idx_webhook_events_status_time", "status", "received_at"),
        Index("idx_webhook_events_retry", "next_retry_at"),
        CheckConstraint("status IN ('pending', 'processing', 'completed', 'failed', 'retry', 'cancelled')", name="ck_webhook_status"),
        CheckConstraint("priority IN ('low', 'normal', 'high', 'urgent')", name="ck_webhook_priority"),
        CheckConstraint("processing_attempts >= 0", name="ck_processing_attempts"),
    )


class APILog(Base, LoggerMixin):
    """API log model for tracking external API calls."""
    
    __tablename__ = "api_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    data_source_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("data_sources.id"), index=True)
    
    # Request information
    method: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    endpoint: Mapped[Optional[str]] = mapped_column(String(200), index=True)
    
    # Request details
    headers: Mapped[Optional[dict]] = mapped_column(JSONB)
    params: Mapped[Optional[dict]] = mapped_column(JSONB)
    body: Mapped[Optional[dict]] = mapped_column(JSONB)
    body_size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Response details
    response_status: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    response_headers: Mapped[Optional[dict]] = mapped_column(JSONB)
    response_body: Mapped[Optional[dict]] = mapped_column(JSONB)
    response_size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Performance metrics
    request_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    response_time: Mapped[Optional[datetime]] = mapped_column(DateTime)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Status
    success: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    error_type: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    
    # Rate limiting
    rate_limit_remaining: Mapped[Optional[int]] = mapped_column(Integer)
    rate_limit_reset: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Metadata
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    
    # Relationships
    data_source = relationship("DataSource")
    
    __table_args__ = (
        Index("idx_api_logs_method_status", "method", "response_status"),
        Index("idx_api_logs_duration", "duration_ms"),
        Index("idx_api_logs_success_time", "success", "request_time"),
        Index("idx_api_logs_endpoint", "endpoint", "request_time"),
        CheckConstraint("method IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS')", name="ck_http_method"),
        CheckConstraint("duration_ms IS NULL OR duration_ms >= 0", name="ck_duration_positive"),
    ) 