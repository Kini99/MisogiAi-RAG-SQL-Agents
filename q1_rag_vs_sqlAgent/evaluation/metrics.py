"""
Metrics calculation for evaluating RAG vs SQL Agent performance
"""
import re
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher

def calculate_accuracy_score(query: str, response: str) -> float:
    """
    Calculate accuracy score based on response relevance and completeness
    Returns a score between 0.0 and 1.0
    """
    if not response or response.strip() == "":
        return 0.0
    
    score = 0.0
    
    # Check for error indicators
    error_indicators = [
        "error", "exception", "failed", "invalid", "not found",
        "syntax error", "table not found", "column not found"
    ]
    
    response_lower = response.lower()
    for indicator in error_indicators:
        if indicator in response_lower:
            return 0.1  # Very low score for errors
    
    # Check for empty or no results
    no_result_indicators = [
        "no results found", "no data found", "empty result",
        "0 rows", "no records", "no matches"
    ]
    
    for indicator in no_result_indicators:
        if indicator in response_lower:
            score += 0.3  # Partial score for valid but empty results
            break
    else:
        # If we have actual results, give higher base score
        score += 0.6
    
    # Check for numerical data (counts, amounts, etc.)
    numbers = re.findall(r'\d+', response)
    if numbers:
        score += 0.2
    
    # Check for structured data (tables, lists)
    if '|' in response or '\t' in response or '\n' in response:
        score += 0.1
    
    # Check for relevant keywords from query
    query_keywords = extract_keywords(query)
    response_keywords = extract_keywords(response)
    
    keyword_overlap = len(query_keywords.intersection(response_keywords))
    if keyword_overlap > 0:
        score += min(0.1, keyword_overlap * 0.02)
    
    return min(1.0, score)

def calculate_response_quality(response: str) -> float:
    """
    Calculate response quality based on formatting, clarity, and structure
    Returns a score between 0.0 and 1.0
    """
    if not response or response.strip() == "":
        return 0.0
    
    score = 0.0
    
    # Base score for non-empty response
    score += 0.3
    
    # Check for structured formatting
    if '|' in response or '\t' in response:
        score += 0.2  # Table format
    elif '\n' in response and response.count('\n') > 2:
        score += 0.1  # Multi-line format
    
    # Check for clear section headers
    headers = re.findall(r'^[A-Z][^:]*:', response, re.MULTILINE)
    if headers:
        score += 0.1
    
    # Check for numerical precision
    numbers = re.findall(r'\d+\.\d+', response)
    if numbers:
        score += 0.1
    
    # Check for currency formatting
    if '$' in response or 'USD' in response:
        score += 0.1
    
    # Check for date formatting
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}',
        r'\d{2}/\d{2}/\d{4}',
        r'\w+ \d{1,2}, \d{4}'
    ]
    
    for pattern in date_patterns:
        if re.search(pattern, response):
            score += 0.1
            break
    
    # Check for reasonable response length
    if 50 <= len(response) <= 2000:
        score += 0.1
    elif len(response) > 2000:
        score += 0.05  # Slightly penalize very long responses
    
    return min(1.0, score)

def extract_keywords(text: str) -> set:
    """Extract meaningful keywords from text"""
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
        'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
    }
    
    # Extract words and filter
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    keywords = {word for word in words if word not in stop_words and len(word) > 2}
    
    return keywords

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two text strings"""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def evaluate_sql_quality(sql_query: str) -> float:
    """
    Evaluate the quality of generated SQL queries
    Returns a score between 0.0 and 1.0
    """
    if not sql_query or sql_query.strip() == "":
        return 0.0
    
    score = 0.0
    
    # Check for basic SQL structure
    sql_lower = sql_query.lower()
    
    # Must have SELECT
    if 'select' in sql_lower:
        score += 0.3
    else:
        return 0.0  # Not a valid SELECT query
    
    # Check for FROM clause
    if 'from' in sql_lower:
        score += 0.2
    
    # Check for proper table names
    valid_tables = ['customers', 'orders', 'products', 'reviews', 'support_tickets', 'order_items']
    found_tables = [table for table in valid_tables if table in sql_lower]
    if found_tables:
        score += 0.2
    
    # Check for JOIN clauses (complexity bonus)
    if 'join' in sql_lower:
        score += 0.1
    
    # Check for WHERE clauses
    if 'where' in sql_lower:
        score += 0.1
    
    # Check for GROUP BY (aggregation)
    if 'group by' in sql_lower:
        score += 0.1
    
    # Check for ORDER BY
    if 'order by' in sql_lower:
        score += 0.1
    
    # Check for LIMIT (good practice)
    if 'limit' in sql_lower:
        score += 0.05
    
    # Penalize for common SQL errors
    error_patterns = [
        r'select\s+\*',  # SELECT * is often not ideal
        r';\s*;',        # Double semicolons
        r'from\s+from',  # Double FROM
        r'where\s+where' # Double WHERE
    ]
    
    for pattern in error_patterns:
        if re.search(pattern, sql_lower):
            score -= 0.1
    
    return max(0.0, min(1.0, score))

def calculate_comprehensiveness(query: str, response: str) -> float:
    """
    Calculate how comprehensive the response is compared to the query
    Returns a score between 0.0 and 1.0
    """
    if not response or response.strip() == "":
        return 0.0
    
    score = 0.0
    
    # Extract query intent
    query_intent = extract_query_intent(query)
    
    # Check if response addresses the intent
    if query_intent == "count":
        if any(word in response.lower() for word in ['count', 'total', 'number', 'amount']):
            score += 0.5
        if re.search(r'\d+', response):
            score += 0.3
    
    elif query_intent == "list":
        if any(word in response.lower() for word in ['list', 'show', 'display', 'all']):
            score += 0.4
        if '\n' in response or '|' in response:
            score += 0.3
    
    elif query_intent == "average":
        if any(word in response.lower() for word in ['average', 'avg', 'mean']):
            score += 0.5
        if re.search(r'\d+\.\d+', response):
            score += 0.3
    
    elif query_intent == "sum":
        if any(word in response.lower() for word in ['sum', 'total', 'amount', 'revenue']):
            score += 0.5
        if re.search(r'\d+', response):
            score += 0.3
    
    # Check for relevant data types
    if 'customer' in query.lower() and 'customer' in response.lower():
        score += 0.2
    if 'order' in query.lower() and 'order' in response.lower():
        score += 0.2
    if 'product' in query.lower() and 'product' in response.lower():
        score += 0.2
    
    return min(1.0, score)

def extract_query_intent(query: str) -> str:
    """Extract the intent of a natural language query"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['how many', 'count', 'number of', 'total number']):
        return "count"
    elif any(word in query_lower for word in ['list', 'show', 'display', 'all']):
        return "list"
    elif any(word in query_lower for word in ['average', 'avg', 'mean']):
        return "average"
    elif any(word in query_lower for word in ['sum', 'total', 'revenue', 'amount']):
        return "sum"
    elif any(word in query_lower for word in ['find', 'search', 'locate']):
        return "search"
    else:
        return "general"

def calculate_overall_score(accuracy: float, quality: float, comprehensiveness: float, 
                          sql_quality: float = 0.0) -> float:
    """
    Calculate overall score from individual metrics
    Returns a weighted score between 0.0 and 1.0
    """
    weights = {
        'accuracy': 0.4,
        'quality': 0.3,
        'comprehensiveness': 0.2,
        'sql_quality': 0.1
    }
    
    overall_score = (
        accuracy * weights['accuracy'] +
        quality * weights['quality'] +
        comprehensiveness * weights['comprehensiveness'] +
        sql_quality * weights['sql_quality']
    )
    
    return min(1.0, overall_score) 