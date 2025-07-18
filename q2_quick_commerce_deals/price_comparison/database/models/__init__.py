"""Database models for the price comparison platform."""

# Core models
from .core import (
    Platform,
    Category,
    Brand,
    Product,
    ProductVariant,
    ProductImage,
    ProductSpecification,
    ProductReview,
)

# Pricing models
from .pricing import (
    Price,
    PriceHistory,
    Discount,
    DiscountType,
    Promotion,
    Coupon,
    PriceAlert,
)

# Availability models
from .availability import (
    Availability,
    Inventory,
    StockLevel,
    DeliverySlot,
    DeliveryZone,
    Serviceability,
)

# Platform-specific models
from .platforms import (
    PlatformProduct,
    PlatformCategory,
    PlatformBrand,
    PlatformPricing,
    PlatformAvailability,
    PlatformMetadata,
)

# User and analytics models
from .users import (
    User,
    UserProfile,
    UserPreference,
    UserSearch,
    UserQuery,
    UserAlert,
)

# Query and analytics models
from .analytics import (
    QueryLog,
    QueryResult,
    QueryPerformance,
    SearchAnalytics,
    PriceAnalytics,
    PlatformAnalytics,
    UserAnalytics,
)

# Performance and monitoring models
from .monitoring import (
    SystemMetrics,
    DatabaseMetrics,
    CacheMetrics,
    QueryMetrics,
    ErrorLog,
    PerformanceLog,
)

# Integration models
from .integrations import (
    DataSource,
    DataSync,
    DataValidation,
    IntegrationLog,
    WebhookEvent,
    APILog,
)

__all__ = [
    # Core models
    "Platform",
    "Category", 
    "Brand",
    "Product",
    "ProductVariant",
    "ProductImage",
    "ProductSpecification",
    "ProductReview",
    
    # Pricing models
    "Price",
    "PriceHistory",
    "Discount",
    "DiscountType",
    "Promotion",
    "Coupon",
    "PriceAlert",
    
    # Availability models
    "Availability",
    "Inventory",
    "StockLevel",
    "DeliverySlot",
    "DeliveryZone",
    "Serviceability",
    
    # Platform-specific models
    "PlatformProduct",
    "PlatformCategory",
    "PlatformBrand",
    "PlatformPricing",
    "PlatformAvailability",
    "PlatformMetadata",
    
    # User and analytics models
    "User",
    "UserProfile",
    "UserPreference",
    "UserSearch",
    "UserQuery",
    "UserAlert",
    
    # Query and analytics models
    "QueryLog",
    "QueryResult",
    "QueryPerformance",
    "SearchAnalytics",
    "PriceAnalytics",
    "PlatformAnalytics",
    "UserAnalytics",
    
    # Performance and monitoring models
    "SystemMetrics",
    "DatabaseMetrics",
    "CacheMetrics",
    "QueryMetrics",
    "ErrorLog",
    "PerformanceLog",
    
    # Integration models
    "DataSource",
    "DataSync",
    "DataValidation",
    "IntegrationLog",
    "WebhookEvent",
    "APILog",
] 