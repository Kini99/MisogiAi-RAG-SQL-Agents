"""Logging configuration for the price comparison platform."""

import logging
import sys
from typing import Any, Dict, Optional

import structlog
from structlog.stdlib import LoggerFactory

from .config import settings


def configure_logging() -> None:
    """Configure structured logging for the application."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.monitoring.log_format == "json" else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.monitoring.log_level),
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.INFO)
    logging.getLogger("redis").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin to add logging capabilities to classes."""
    
    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        """Get logger for this class."""
        return get_logger(self.__class__.__name__)


def log_function_call(func_name: str, **kwargs: Any) -> None:
    """Log function call with parameters."""
    logger = get_logger("function_calls")
    logger.info(
        "Function called",
        function=func_name,
        parameters=kwargs,
    )


def log_query_execution(query: str, execution_time: float, success: bool, **kwargs: Any) -> None:
    """Log SQL query execution details."""
    logger = get_logger("query_execution")
    log_data = {
        "query": query,
        "execution_time_ms": round(execution_time * 1000, 2),
        "success": success,
    }
    log_data.update(kwargs)
    
    if success:
        logger.info("Query executed successfully", **log_data)
    else:
        logger.error("Query execution failed", **log_data)


def log_api_request(
    method: str,
    path: str,
    status_code: int,
    response_time: float,
    user_id: Optional[str] = None,
    **kwargs: Any
) -> None:
    """Log API request details."""
    logger = get_logger("api_requests")
    log_data = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "response_time_ms": round(response_time * 1000, 2),
        "user_id": user_id,
    }
    log_data.update(kwargs)
    
    if 200 <= status_code < 400:
        logger.info("API request successful", **log_data)
    elif 400 <= status_code < 500:
        logger.warning("API request client error", **log_data)
    else:
        logger.error("API request server error", **log_data)


def log_cache_operation(operation: str, key: str, hit: bool, ttl: Optional[int] = None) -> None:
    """Log cache operations."""
    logger = get_logger("cache_operations")
    logger.info(
        "Cache operation",
        operation=operation,
        key=key,
        hit=hit,
        ttl=ttl,
    )


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """Log error with context."""
    logger = get_logger("errors")
    log_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }
    if context:
        log_data.update(context)
    
    logger.error("Error occurred", **log_data, exc_info=True)


# Initialize logging on module import
configure_logging() 