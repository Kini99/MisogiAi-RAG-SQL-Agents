"""Main FastAPI application for the price comparison platform."""

import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import structlog

from .core.config import settings
from .core.logging import get_logger, log_api_request
from .database.base import init_db, close_db, check_db_health
from .api.v1.router import api_router
from .api.health import health_router

# Initialize logger
logger = get_logger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Price Comparison Platform...")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise
    
    # Check database health
    if not await check_db_health():
        logger.error("Database health check failed")
        raise RuntimeError("Database is not healthy")
    
    logger.info("Price Comparison Platform started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Price Comparison Platform...")
    await close_db()
    logger.info("Price Comparison Platform shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.api.title,
    description=settings.api.description,
    version=settings.api.version,
    debug=settings.api.debug,
    lifespan=lifespan,
    docs_url="/docs" if settings.api.debug else None,
    redoc_url="/redoc" if settings.api.debug else None,
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.cors_origins,
    allow_credentials=settings.api.cors_allow_credentials,
    allow_methods=settings.api.cors_allow_methods,
    allow_headers=settings.api.cors_allow_headers,
)

# Add GZip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add custom middleware for logging and monitoring
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header and log API requests."""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log API request
    try:
        log_api_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            response_time=process_time,
            user_id=getattr(request.state, "user_id", None),
        )
    except Exception as e:
        logger.error("Failed to log API request", error=str(e))
    
    return response


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to responses."""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(
        "Unhandled exception",
        error_type=type(exc).__name__,
        error_message=str(exc),
        path=request.url.path,
        method=request.method,
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "error_id": f"{int(time.time())}",
        },
    )


# Rate limiting decorator
def rate_limit(requests: int = 60, window: int = 60):
    """Rate limiting decorator."""
    return limiter.limit(f"{requests}/{window}seconds")


# Health check endpoint
@app.get("/health", tags=["Health"])
@rate_limit(requests=120, window=60)
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.api.version,
        "environment": settings.environment,
    }
    
    # Check database health
    try:
        db_healthy = await check_db_health()
        health_status["database"] = "healthy" if db_healthy else "unhealthy"
        if not db_healthy:
            health_status["status"] = "unhealthy"
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        health_status["database"] = "error"
        health_status["status"] = "unhealthy"
    
    # Check Redis health (if configured)
    try:
        import redis
        r = redis.Redis.from_url(settings.redis.url)
        r.ping()
        health_status["redis"] = "healthy"
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
        health_status["redis"] = "unhealthy"
        health_status["status"] = "unhealthy"
    
    return health_status


# Root endpoint
@app.get("/", tags=["Root"])
@rate_limit(requests=60, window=60)
async def root() -> Dict[str, Any]:
    """Root endpoint."""
    return {
        "message": "Price Comparison Platform API",
        "version": settings.api.version,
        "description": settings.api.description,
        "docs": "/docs" if settings.api.debug else None,
        "health": "/health",
    }


# Include routers
app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(api_router, prefix="/api/v1", tags=["API"])

# Add rate limiting to all routes
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware."""
    # Skip rate limiting for health checks
    if request.url.path.startswith("/health"):
        return await call_next(request)
    
    # Apply rate limiting
    try:
        await limiter.check_request_limit(request)
    except RateLimitExceeded:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
            },
        )
    
    return await call_next(request)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "price_comparison.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.api.debug,
        log_level=settings.monitoring.log_level.lower(),
    ) 