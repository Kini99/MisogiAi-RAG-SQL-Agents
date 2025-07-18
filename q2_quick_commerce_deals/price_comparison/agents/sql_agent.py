"""SQL Agent for the price comparison platform using LangChain."""

import time
import json
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func, MetaData
from sqlalchemy.exc import SQLAlchemyError

from ..core.config import settings
from ..core.logging import get_logger
from ..database.base import engine
from ..services.cache_service import CacheService

logger = get_logger(__name__)


@dataclass
class SQLAgentResult:
    """Result from SQL agent processing."""
    success: bool
    results: List[Dict[str, Any]]
    sql_generated: Optional[str] = None
    processed_query: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0


class SQLAgent:
    """SQL Agent for intelligent query processing using LangChain."""
    
    def __init__(self, db: AsyncSession):
        """Initialize SQL agent."""
        self.db = db
        self.cache_service = CacheService()
        self.llm = None
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize LangChain SQL agent."""
        try:
            if settings.langchain.openai_api_key:
                # Initialize OpenAI LLM
                self.llm = ChatOpenAI(
                    model=settings.langchain.openai_model,
                    temperature=settings.langchain.temperature,
                    max_tokens=settings.langchain.max_tokens,
                    api_key=settings.langchain.openai_api_key,
                )
                
                # Create SQL database connection for LangChain
                sync_engine = engine.sync_engine if hasattr(engine, 'sync_engine') else engine
                db = SQLDatabase(engine=sync_engine)
                
                # Create SQL toolkit
                toolkit = SQLDatabaseToolkit(db=db, llm=self.llm)
                
                # Create SQL agent
                self.agent = create_sql_agent(
                    llm=self.llm,
                    toolkit=toolkit,
                    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                    verbose=True,
                )
                
                logger.info("SQL Agent initialized successfully")
            else:
                logger.warning("OpenAI API key not configured, using fallback mode")
                
        except Exception as e:
            logger.error("Failed to initialize SQL agent", error=str(e))
    
    async def process_query(
        self,
        query: str,
        max_results: int = 100,
        context: Optional[Dict[str, Any]] = None,
    ) -> SQLAgentResult:
        """Process natural language query using SQL agent."""
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = f"sql_agent:{hash(query)}:{max_results}"
            cached_result = await self.cache_service.get(cache_key)
            
            if cached_result:
                logger.info("Serving cached SQL agent result")
                return SQLAgentResult(
                    success=True,
                    results=cached_result["results"],
                    sql_generated=cached_result.get("sql_generated"),
                    processed_query=cached_result.get("processed_query"),
                    metadata=cached_result.get("metadata"),
                    execution_time_ms=(time.time() - start_time) * 1000,
                )
            
            # Process with LangChain agent if available
            if self.agent:
                result = await self._process_with_langchain(query, max_results, context)
            else:
                # Fallback to rule-based processing
                result = await self._process_with_fallback(query, max_results, context)
            
            # Cache the result
            cache_data = {
                "results": result.results,
                "sql_generated": result.sql_generated,
                "processed_query": result.processed_query,
                "metadata": result.metadata,
            }
            await self.cache_service.set(cache_key, cache_data, ttl=300)
            
            result.execution_time_ms = (time.time() - start_time) * 1000
            return result
            
        except Exception as e:
            logger.error("SQL agent processing failed", query=query, error=str(e))
            return SQLAgentResult(
                success=False,
                results=[],
                error_message=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
            )
    
    async def _process_with_langchain(
        self,
        query: str,
        max_results: int,
        context: Optional[Dict[str, Any]] = None,
    ) -> SQLAgentResult:
        """Process query using LangChain SQL agent."""
        try:
            # Enhance query with context and constraints
            enhanced_query = self._enhance_query(query, max_results, context)
            
            # Execute with LangChain agent
            response = await self.agent.ainvoke({"input": enhanced_query})
            
            # Parse response
            sql_generated = self._extract_sql_from_response(response)
            results = self._parse_agent_response(response)
            
            return SQLAgentResult(
                success=True,
                results=results,
                sql_generated=sql_generated,
                processed_query=enhanced_query,
                metadata={
                    "agent_type": "langchain",
                    "response_length": len(str(response)),
                    "context_used": bool(context),
                },
            )
            
        except Exception as e:
            logger.error("LangChain processing failed", error=str(e))
            raise
    
    async def _process_with_fallback(
        self,
        query: str,
        max_results: int,
        context: Optional[Dict[str, Any]] = None,
    ) -> SQLAgentResult:
        """Fallback processing using rule-based approach."""
        try:
            # Simple rule-based query generation
            sql_query = self._generate_sql_from_rules(query, max_results)
            
            if sql_query:
                # Execute SQL query
                result = await self.db.execute(text(sql_query))
                rows = result.fetchall()
                
                # Convert to dictionary format
                results = []
                for row in rows[:max_results]:
                    if hasattr(row, '_mapping'):
                        results.append(dict(row._mapping))
                    else:
                        results.append(dict(row))
                
                return SQLAgentResult(
                    success=True,
                    results=results,
                    sql_generated=sql_query,
                    processed_query=query,
                    metadata={
                        "agent_type": "fallback",
                        "rules_applied": True,
                    },
                )
            else:
                # Return mock results for demonstration
                return SQLAgentResult(
                    success=True,
                    results=self._get_mock_results(query),
                    processed_query=query,
                    metadata={
                        "agent_type": "fallback",
                        "mock_results": True,
                    },
                )
                
        except Exception as e:
            logger.error("Fallback processing failed", error=str(e))
            raise
    
    def _enhance_query(self, query: str, max_results: int, context: Optional[Dict[str, Any]]) -> str:
        """Enhance query with additional context and constraints."""
        enhanced_parts = [query]
        
        # Add result limit
        enhanced_parts.append(f"Limit results to {max_results} items.")
        
        # Add context if available
        if context:
            if "location" in context:
                enhanced_parts.append(f"Focus on location: {context['location']}")
            if "platform" in context:
                enhanced_parts.append(f"Focus on platform: {context['platform']}")
            if "category" in context:
                enhanced_parts.append(f"Focus on category: {context['category']}")
        
        # Add common constraints for price comparison
        enhanced_parts.append("Only include products that are currently available.")
        enhanced_parts.append("Sort by relevance and price.")
        
        return " ".join(enhanced_parts)
    
    def _extract_sql_from_response(self, response: Any) -> Optional[str]:
        """Extract SQL query from LangChain response."""
        try:
            response_str = str(response)
            
            # Look for SQL in the response
            if "SELECT" in response_str.upper():
                # Simple extraction - in production, use more sophisticated parsing
                lines = response_str.split('\n')
                for line in lines:
                    if line.strip().upper().startswith('SELECT'):
                        return line.strip()
            
            return None
        except Exception as e:
            logger.error("Failed to extract SQL from response", error=str(e))
            return None
    
    def _parse_agent_response(self, response: Any) -> List[Dict[str, Any]]:
        """Parse LangChain agent response into structured results."""
        try:
            response_str = str(response)
            
            # Try to extract structured data
            if "output" in response_str:
                # Look for JSON-like structures
                import re
                json_pattern = r'\{[^{}]*\}'
                matches = re.findall(json_pattern, response_str)
                
                results = []
                for match in matches:
                    try:
                        data = json.loads(match)
                        results.append(data)
                    except json.JSONDecodeError:
                        continue
                
                if results:
                    return results
            
            # Fallback: return response as text
            return [{"response": response_str}]
            
        except Exception as e:
            logger.error("Failed to parse agent response", error=str(e))
            return [{"error": "Failed to parse response"}]
    
    def _generate_sql_from_rules(self, query: str, max_results: int) -> Optional[str]:
        """Generate SQL query using rule-based approach."""
        query_lower = query.lower()
        
        # Basic rule-based SQL generation
        if "cheapest" in query_lower and "onions" in query_lower:
            return f"""
                SELECT 
                    p.name as platform,
                    pr.name as product,
                    pc.selling_price,
                    pc.mrp,
                    ROUND(((pc.mrp - pc.selling_price) / pc.mrp * 100), 2) as discount_percentage
                FROM prices pc
                JOIN products pr ON pc.product_id = pr.id
                JOIN platforms p ON pc.platform_id = p.id
                WHERE pr.name ILIKE '%onion%'
                AND pc.is_active = true
                ORDER BY pc.selling_price ASC
                LIMIT {max_results}
            """
        
        elif "discount" in query_lower and "blinkit" in query_lower:
            return f"""
                SELECT 
                    pr.name as product,
                    pc.selling_price,
                    pc.mrp,
                    ROUND(((pc.mrp - pc.selling_price) / pc.mrp * 100), 2) as discount_percentage
                FROM prices pc
                JOIN products pr ON pc.product_id = pr.id
                JOIN platforms p ON pc.platform_id = p.id
                WHERE p.name ILIKE '%blinkit%'
                AND pc.is_active = true
                AND pc.discount_percentage > 30
                ORDER BY pc.discount_percentage DESC
                LIMIT {max_results}
            """
        
        elif "compare" in query_lower and "fruit" in query_lower:
            return f"""
                SELECT 
                    p.name as platform,
                    pr.name as product,
                    pc.selling_price,
                    pc.mrp
                FROM prices pc
                JOIN products pr ON pc.product_id = pr.id
                JOIN platforms p ON pc.platform_id = p.id
                JOIN categories c ON pr.category_id = c.id
                WHERE c.name ILIKE '%fruit%'
                AND pc.is_active = true
                ORDER BY p.name, pc.selling_price
                LIMIT {max_results}
            """
        
        return None
    
    def _get_mock_results(self, query: str) -> List[Dict[str, Any]]:
        """Get mock results for demonstration."""
        query_lower = query.lower()
        
        if "cheapest" in query_lower:
            return [
                {
                    "platform": "Blinkit",
                    "product": "Fresh Onions",
                    "selling_price": 45.0,
                    "mrp": 60.0,
                    "discount_percentage": 25.0,
                },
                {
                    "platform": "Zepto",
                    "product": "Organic Onions",
                    "selling_price": 48.0,
                    "mrp": 65.0,
                    "discount_percentage": 26.15,
                },
            ]
        elif "discount" in query_lower:
            return [
                {
                    "product": "Premium Basmati Rice",
                    "selling_price": 120.0,
                    "mrp": 180.0,
                    "discount_percentage": 33.33,
                },
                {
                    "product": "Organic Tomatoes",
                    "selling_price": 35.0,
                    "mrp": 50.0,
                    "discount_percentage": 30.0,
                },
            ]
        else:
            return [
                {
                    "message": "Query processed successfully",
                    "platform": "Multiple",
                    "product": "Various Products",
                }
            ]
    
    async def get_schema_info(self) -> Dict[str, Any]:
        """Get database schema information for the agent."""
        try:
            # Get table information
            metadata = MetaData()
            metadata.reflect(bind=engine.sync_engine)
            
            schema_info = {}
            for table_name, table in metadata.tables.items():
                columns = []
                for column in table.columns:
                    columns.append({
                        "name": column.name,
                        "type": str(column.type),
                        "nullable": column.nullable,
                        "primary_key": column.primary_key,
                    })
                
                schema_info[table_name] = {
                    "columns": columns,
                    "primary_key": [col.name for col in table.primary_key.columns],
                    "foreign_keys": [
                        {
                            "column": fk.parent.name,
                            "references": f"{fk.column.table.name}.{fk.column.name}"
                        }
                        for fk in table.foreign_keys
                    ],
                }
            
            return schema_info
            
        except Exception as e:
            logger.error("Failed to get schema info", error=str(e))
            return {}
    
    async def health_check(self) -> bool:
        """Check SQL agent health."""
        try:
            if self.agent:
                # Test with a simple query
                test_result = await self.process_query("Show me 1 product", max_results=1)
                return test_result.success
            else:
                # Fallback mode is always healthy
                return True
        except Exception as e:
            logger.error("SQL agent health check failed", error=str(e))
            return False 