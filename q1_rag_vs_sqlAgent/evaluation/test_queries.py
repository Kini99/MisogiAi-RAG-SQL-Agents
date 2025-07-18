"""
Test queries for benchmarking RAG vs SQL Agent systems
"""
from typing import List, Dict, Any

# Test queries categorized by complexity and type
TEST_QUERIES = {
    "simple_lookup": [
        "How many customers do we have?",
        "What is the total number of orders?",
        "Show me all products in the Electronics category",
        "List all customers from California",
        "How many support tickets are currently open?",
        "What is the average product price?",
        "Show me all orders with status 'delivered'",
        "List all products with stock quantity less than 10",
        "How many reviews have 5-star ratings?",
        "Show me all customers who signed up in the last month"
    ],
    
    "aggregation_queries": [
        "What is the total revenue from all orders?",
        "What is the average order value?",
        "How much revenue did we generate last month?",
        "What is the total number of items sold?",
        "What is the average rating across all products?",
        "How many orders does each customer have on average?",
        "What is the total value of pending orders?",
        "What is the average time to resolve support tickets?",
        "How many products are in each category?",
        "What is the total number of verified purchase reviews?"
    ],
    
    "join_queries": [
        "Show me all orders with customer names and email addresses",
        "List all products with their average ratings",
        "Show me customers who have placed orders and their total spending",
        "List all support tickets with customer contact information",
        "Show me products that have been reviewed with customer names",
        "List all orders with product details and quantities",
        "Show me customers who have both orders and support tickets",
        "List all reviews with product names and customer emails",
        "Show me orders with payment status and customer information",
        "List all products with their total sales quantity"
    ],
    
    "complex_analytics": [
        "Which customers have spent the most money?",
        "What are our top 5 selling products?",
        "Which products have the highest average ratings?",
        "Show me customers who haven't placed an order in the last 3 months",
        "What is the customer retention rate?",
        "Which categories generate the most revenue?",
        "Show me products with low stock that have high demand",
        "What is the average order value by customer location?",
        "Which customers have the most support tickets?",
        "What is the correlation between product price and rating?"
    ],
    
    "business_intelligence": [
        "What is our monthly revenue trend over the last 6 months?",
        "Which payment methods are most popular?",
        "What is the average time between customer registration and first order?",
        "Show me the distribution of order statuses",
        "What is the customer lifetime value?",
        "Which products have the highest return rate?",
        "What is the average response time for support tickets?",
        "Show me seasonal trends in order volume",
        "What is the conversion rate from customer registration to first purchase?",
        "Which customers are at risk of churning?"
    ],
    
    "edge_cases": [
        "Find customers with multiple email addresses",
        "Show me orders with negative total amounts",
        "List products with zero price",
        "Find customers with invalid phone numbers",
        "Show me orders placed in the future",
        "List products with duplicate SKUs",
        "Find customers with orders but no reviews",
        "Show me support tickets without assigned agents",
        "List orders with missing customer information",
        "Find products with more reviews than sales"
    ]
}

# Query complexity scoring (1-5 scale)
QUERY_COMPLEXITY = {
    "simple_lookup": 1,
    "aggregation_queries": 2,
    "join_queries": 3,
    "complex_analytics": 4,
    "business_intelligence": 5,
    "edge_cases": 3
}

# Expected response characteristics
QUERY_EXPECTATIONS = {
    "simple_lookup": {
        "response_type": "count/list",
        "accuracy_importance": "high",
        "speed_importance": "high"
    },
    "aggregation_queries": {
        "response_type": "calculation",
        "accuracy_importance": "very_high",
        "speed_importance": "medium"
    },
    "join_queries": {
        "response_type": "tabular",
        "accuracy_importance": "high",
        "speed_importance": "medium"
    },
    "complex_analytics": {
        "response_type": "analysis",
        "accuracy_importance": "very_high",
        "speed_importance": "low"
    },
    "business_intelligence": {
        "response_type": "insights",
        "accuracy_importance": "very_high",
        "speed_importance": "low"
    },
    "edge_cases": {
        "response_type": "validation",
        "accuracy_importance": "medium",
        "speed_importance": "medium"
    }
}

def get_all_test_queries() -> List[str]:
    """Get all test queries as a flat list"""
    all_queries = []
    for category, queries in TEST_QUERIES.items():
        all_queries.extend(queries)
    return all_queries

def get_queries_by_category(category: str) -> List[str]:
    """Get queries for a specific category"""
    return TEST_QUERIES.get(category, [])

def get_queries_by_complexity(complexity: int) -> List[str]:
    """Get queries with specific complexity level"""
    queries = []
    for category, cat_complexity in QUERY_COMPLEXITY.items():
        if cat_complexity == complexity:
            queries.extend(TEST_QUERIES[category])
    return queries

def get_random_sample(size: int = 10) -> List[str]:
    """Get a random sample of test queries"""
    import random
    all_queries = get_all_test_queries()
    return random.sample(all_queries, min(size, len(all_queries)))

def get_benchmark_queries() -> List[str]:
    """Get a curated set of queries for comprehensive benchmarking"""
    benchmark_queries = []
    
    # Include queries from each category
    for category in TEST_QUERIES.keys():
        # Take 2 queries from each category for balanced testing
        category_queries = TEST_QUERIES[category][:2]
        benchmark_queries.extend(category_queries)
    
    return benchmark_queries

# Specific test scenarios for detailed analysis
SPECIALIZED_TEST_SCENARIOS = {
    "customer_service": [
        "Find all orders for customer john.doe@email.com",
        "Show me the support ticket history for customer ID 123",
        "What products has customer sarah.smith@email.com purchased?",
        "List all open support tickets for customers from New York",
        "Show me customers with multiple failed payment attempts"
    ],
    
    "inventory_management": [
        "Which products are running low on stock?",
        "Show me products with zero inventory",
        "What is the total inventory value?",
        "List products that need restocking",
        "Show me inventory turnover by product category"
    ],
    
    "financial_analysis": [
        "What is our total revenue this year?",
        "Show me monthly revenue breakdown",
        "What is the average order value by payment method?",
        "List customers with highest lifetime value",
        "Show me revenue by product category"
    ],
    
    "quality_assurance": [
        "Find products with average rating below 3 stars",
        "Show me customers with multiple support tickets",
        "List orders with delivery delays",
        "Find products with high return rates",
        "Show me support tickets that took more than 7 days to resolve"
    ]
}

def get_specialized_queries(scenario: str) -> List[str]:
    """Get queries for a specific business scenario"""
    return SPECIALIZED_TEST_SCENARIOS.get(scenario, [])

# Query templates for generating variations
QUERY_TEMPLATES = {
    "customer_lookup": [
        "Find customer with email {email}",
        "Show me customer {customer_id}",
        "List customers from {city}",
        "Find customers who signed up in {month}",
        "Show me active customers"
    ],
    
    "order_analysis": [
        "Show me orders from {date_range}",
        "List orders with status {status}",
        "Find orders above ${amount}",
        "Show me orders by {payment_method}",
        "List orders for customer {customer_id}"
    ],
    
    "product_analysis": [
        "Show me products in category {category}",
        "List products by brand {brand}",
        "Find products under ${price}",
        "Show me products with rating above {rating}",
        "List products with stock below {quantity}"
    ]
}

def generate_query_variations(template: str, **kwargs) -> List[str]:
    """Generate query variations from templates"""
    variations = []
    
    if template == "customer_lookup":
        if "email" in kwargs:
            variations.append(f"Find customer with email {kwargs['email']}")
        if "customer_id" in kwargs:
            variations.append(f"Show me customer {kwargs['customer_id']}")
        if "city" in kwargs:
            variations.append(f"List customers from {kwargs['city']}")
        if "month" in kwargs:
            variations.append(f"Find customers who signed up in {kwargs['month']}")
        variations.append("Show me active customers")
    
    elif template == "order_analysis":
        if "date_range" in kwargs:
            variations.append(f"Show me orders from {kwargs['date_range']}")
        if "status" in kwargs:
            variations.append(f"List orders with status {kwargs['status']}")
        if "amount" in kwargs:
            variations.append(f"Find orders above ${kwargs['amount']}")
        if "payment_method" in kwargs:
            variations.append(f"Show me orders by {kwargs['payment_method']}")
        if "customer_id" in kwargs:
            variations.append(f"List orders for customer {kwargs['customer_id']}")
    
    elif template == "product_analysis":
        if "category" in kwargs:
            variations.append(f"Show me products in category {kwargs['category']}")
        if "brand" in kwargs:
            variations.append(f"List products by brand {kwargs['brand']}")
        if "price" in kwargs:
            variations.append(f"Find products under ${kwargs['price']}")
        if "rating" in kwargs:
            variations.append(f"Show me products with rating above {kwargs['rating']}")
        if "quantity" in kwargs:
            variations.append(f"List products with stock below {kwargs['quantity']}")
    
    return variations 