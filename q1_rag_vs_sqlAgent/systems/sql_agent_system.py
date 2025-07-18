"""
SQL Agent system implementation for natural language to SQL conversion
"""
import re
from typing import List, Dict, Any, Optional
from sqlalchemy import text, create_engine
from sqlalchemy.orm import Session
import pandas as pd

from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_experimental.sql import SQLDatabaseChain
from langchain_experimental.sql.base import SQLDatabase

from systems.base_system import BaseQuerySystem, QueryResult
from config.database import SessionLocal, engine
from config.settings import settings
from models.schema import Customer, Order, Product, Review, SupportTicket

class SQLAgentSystem(BaseQuerySystem):
    """SQL Agent system for natural language queries"""
    
    def __init__(self):
        super().__init__("SQL Agent System")
        self.llm = None
        self.db_chain = None
        self.sql_db = None
        
    def initialize(self) -> bool:
        """Initialize the SQL Agent system"""
        try:
            # Initialize LLM
            if settings.OPENAI_API_KEY:
                self.llm = OpenAI(
                    openai_api_key=settings.OPENAI_API_KEY,
                    model_name=settings.OPENAI_MODEL,
                    temperature=settings.OPENAI_TEMPERATURE,
                    max_tokens=settings.MAX_TOKENS
                )
            else:
                raise ValueError("OpenAI API key is required for SQL Agent system")
            
            # Create SQL database wrapper
            self.sql_db = SQLDatabase(engine)
            
            # Create database chain
            self.db_chain = SQLDatabaseChain.from_llm(
                llm=self.llm,
                db=self.sql_db,
                verbose=False,
                return_intermediate_steps=True
            )
            
            return True
        except Exception as e:
            print(f"Error initializing SQL Agent system: {e}")
            return False
    
    def query(self, natural_language_query: str) -> QueryResult:
        """Execute a natural language query using SQL Agent"""
        try:
            # Execute the query using the database chain
            result = self.db_chain(natural_language_query)
            
            # Extract SQL query and response
            sql_query = result.get('intermediate_steps', [{}])[0].get('sql', '')
            response = result.get('result', '')
            
            # Format the response
            formatted_response = self._format_response(response, sql_query)
            
            # Calculate confidence based on response quality
            confidence_score = self._calculate_confidence(response, sql_query)
            
            return QueryResult(
                query=natural_language_query,
                response=formatted_response,
                execution_time=0.0,  # Will be set by measure_performance
                memory_usage=0.0,    # Will be set by measure_performance
                confidence_score=confidence_score,
                generated_sql=sql_query
            )
            
        except Exception as e:
            return QueryResult(
                query=natural_language_query,
                response="",
                execution_time=0.0,
                memory_usage=0.0,
                error=str(e)
            )
    
    def _format_response(self, response: str, sql_query: str) -> str:
        """Format the response for better readability"""
        if not response:
            return "No results found."
        
        # If response is a DataFrame-like string, format it nicely
        if isinstance(response, str) and ('|' in response or '\t' in response):
            try:
                # Try to parse as DataFrame
                lines = response.strip().split('\n')
                if len(lines) > 1:
                    formatted_response = "Query Results:\n\n"
                    formatted_response += response
                    return formatted_response
            except:
                pass
        
        # Simple text response
        return f"Query Results:\n\n{response}"
    
    def _calculate_confidence(self, response: str, sql_query: str) -> float:
        """Calculate confidence score based on response quality"""
        confidence = 0.5  # Base confidence
        
        # Check if SQL was generated
        if sql_query and sql_query.strip():
            confidence += 0.2
        
        # Check if response contains data
        if response and response.strip() and response != "No results found.":
            confidence += 0.2
        
        # Check for common error patterns
        error_patterns = [
            'error', 'exception', 'failed', 'invalid', 'syntax error',
            'table not found', 'column not found'
        ]
        
        response_lower = response.lower()
        for pattern in error_patterns:
            if pattern in response_lower:
                confidence -= 0.3
                break
        
        return max(0.0, min(1.0, confidence))
    
    def execute_sql_directly(self, sql_query: str) -> QueryResult:
        """Execute SQL query directly for testing purposes"""
        try:
            with engine.connect() as connection:
                result = connection.execute(text(sql_query))
                
                if result.returns_rows:
                    # Fetch results
                    rows = result.fetchall()
                    columns = result.keys()
                    
                    # Convert to DataFrame for better formatting
                    df = pd.DataFrame(rows, columns=columns)
                    response = df.to_string(index=False)
                else:
                    response = f"Query executed successfully. {result.rowcount} rows affected."
                
                return QueryResult(
                    query=f"Direct SQL: {sql_query}",
                    response=response,
                    execution_time=0.0,
                    memory_usage=0.0,
                    confidence_score=1.0,
                    generated_sql=sql_query
                )
                
        except Exception as e:
            return QueryResult(
                query=f"Direct SQL: {sql_query}",
                response="",
                execution_time=0.0,
                memory_usage=0.0,
                error=str(e),
                generated_sql=sql_query
            )
    
    def get_schema_info(self) -> str:
        """Get database schema information for the LLM"""
        schema_info = """
        Database Schema:
        
        customers table:
        - id (INTEGER, PRIMARY KEY)
        - email (VARCHAR(255), UNIQUE)
        - first_name (VARCHAR(100))
        - last_name (VARCHAR(100))
        - phone (VARCHAR(20))
        - address (TEXT)
        - city (VARCHAR(100))
        - state (VARCHAR(100))
        - country (VARCHAR(100))
        - postal_code (VARCHAR(20))
        - created_at (TIMESTAMP)
        - updated_at (TIMESTAMP)
        - is_active (BOOLEAN)
        
        orders table:
        - id (INTEGER, PRIMARY KEY)
        - customer_id (INTEGER, FOREIGN KEY to customers.id)
        - order_number (VARCHAR(100), UNIQUE)
        - status (VARCHAR(50)) - values: pending, processing, shipped, delivered, cancelled
        - total_amount (FLOAT)
        - shipping_address (TEXT)
        - billing_address (TEXT)
        - payment_method (VARCHAR(100))
        - payment_status (VARCHAR(50)) - values: pending, paid, failed, refunded
        - created_at (TIMESTAMP)
        - updated_at (TIMESTAMP)
        
        order_items table:
        - id (INTEGER, PRIMARY KEY)
        - order_id (INTEGER, FOREIGN KEY to orders.id)
        - product_id (INTEGER, FOREIGN KEY to products.id)
        - quantity (INTEGER)
        - unit_price (FLOAT)
        - total_price (FLOAT)
        
        products table:
        - id (INTEGER, PRIMARY KEY)
        - name (VARCHAR(255))
        - description (TEXT)
        - price (FLOAT)
        - category (VARCHAR(100))
        - brand (VARCHAR(100))
        - sku (VARCHAR(100), UNIQUE)
        - stock_quantity (INTEGER)
        - is_active (BOOLEAN)
        - created_at (TIMESTAMP)
        - updated_at (TIMESTAMP)
        
        reviews table:
        - id (INTEGER, PRIMARY KEY)
        - customer_id (INTEGER, FOREIGN KEY to customers.id)
        - product_id (INTEGER, FOREIGN KEY to products.id)
        - rating (INTEGER) - values: 1-5
        - title (VARCHAR(255))
        - comment (TEXT)
        - is_verified_purchase (BOOLEAN)
        - created_at (TIMESTAMP)
        - updated_at (TIMESTAMP)
        
        support_tickets table:
        - id (INTEGER, PRIMARY KEY)
        - customer_id (INTEGER, FOREIGN KEY to customers.id)
        - ticket_number (VARCHAR(100), UNIQUE)
        - subject (VARCHAR(255))
        - description (TEXT)
        - priority (VARCHAR(50)) - values: low, medium, high, urgent
        - status (VARCHAR(50)) - values: open, in_progress, resolved, closed
        - category (VARCHAR(100)) - values: technical, billing, shipping, general
        - assigned_to (VARCHAR(100))
        - resolution (TEXT)
        - created_at (TIMESTAMP)
        - updated_at (TIMESTAMP)
        - resolved_at (TIMESTAMP)
        
        Relationships:
        - customers.id -> orders.customer_id
        - customers.id -> reviews.customer_id
        - customers.id -> support_tickets.customer_id
        - orders.id -> order_items.order_id
        - products.id -> order_items.product_id
        - products.id -> reviews.product_id
        """
        return schema_info
    
    def cleanup(self):
        """Clean up resources"""
        if self.sql_db:
            self.sql_db = None
        if self.db_chain:
            self.db_chain = None 