"""Natural language query endpoint for the price comparison platform."""

import time
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.logging import get_logger, log_query_execution
from ....database.base import get_db
from ....agents.sql_agent import SQLAgent
from ....services.cache_service import CacheService
from ....services.query_service import QueryService
from ....database.models.analytics import QueryLog, QueryResult, QueryPerformance

logger = get_logger(__name__)
router = APIRouter()


class QueryRequest(BaseModel):
    """Natural language query request model."""
    
    query: str = Field(..., min_length=1, max_length=1000, description="Natural language query")
    user_id: Optional[int] = Field(None, description="User ID (optional)")
    session_id: Optional[str] = Field(None, description="Session ID (optional)")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    max_results: Optional[int] = Field(100, ge=1, le=1000, description="Maximum number of results")
    include_metadata: Optional[bool] = Field(True, description="Include query metadata")
    cache_results: Optional[bool] = Field(True, description="Cache query results")


class QueryResponse(BaseModel):
    """Natural language query response model."""
    
    success: bool = Field(..., description="Query execution success")
    query: str = Field(..., description="Original query")
    processed_query: Optional[str] = Field(None, description="Processed query")
    sql_generated: Optional[str] = Field(None, description="Generated SQL query")
    results: List[Dict[str, Any]] = Field(..., description="Query results")
    result_count: int = Field(..., description="Number of results")
    execution_time_ms: float = Field(..., description="Query execution time in milliseconds")
    cache_hit: bool = Field(..., description="Whether result was served from cache")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Query metadata")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    query_id: str = Field(..., description="Unique query identifier")


@router.post("/natural-language", response_model=QueryResponse)
async def natural_language_query(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    http_request: Request = None,
) -> QueryResponse:
    """Execute a natural language query."""
    
    start_time = time.time()
    query_hash = hashlib.sha256(request.query.encode()).hexdigest()
    
    # Initialize services
    cache_service = CacheService()
    query_service = QueryService(db)
    sql_agent = SQLAgent(db)
    
    try:
        # Check cache first
        cache_key = f"query:{query_hash}:{request.max_results}"
        cached_result = await cache_service.get(cache_key)
        
        if cached_result and request.cache_results:
            logger.info("Query result served from cache", query_hash=query_hash)
            return QueryResponse(
                success=True,
                query=request.query,
                results=cached_result["results"],
                result_count=len(cached_result["results"]),
                execution_time_ms=(time.time() - start_time) * 1000,
                cache_hit=True,
                metadata=cached_result.get("metadata"),
                query_id=query_hash,
            )
        
        # Process query with SQL agent
        logger.info("Processing natural language query", query=request.query)
        
        # Generate SQL and execute
        sql_result = await sql_agent.process_query(
            query=request.query,
            max_results=request.max_results,
            context=request.context,
        )
        
        execution_time = (time.time() - start_time) * 1000
        
        # Cache results if successful
        if sql_result.success and request.cache_results:
            cache_data = {
                "results": sql_result.results,
                "metadata": sql_result.metadata,
                "timestamp": datetime.utcnow().isoformat(),
            }
            await cache_service.set(cache_key, cache_data, ttl=300)  # 5 minutes
        
        # Log query execution
        log_query_execution(
            query=request.query,
            execution_time=execution_time / 1000,
            success=sql_result.success,
            result_count=len(sql_result.results),
            cache_hit=False,
        )
        
        # Store query analytics in background
        background_tasks.add_task(
            store_query_analytics,
            db=db,
            query_request=request,
            sql_result=sql_result,
            execution_time=execution_time,
            cache_hit=False,
            query_hash=query_hash,
            http_request=http_request,
        )
        
        return QueryResponse(
            success=sql_result.success,
            query=request.query,
            processed_query=sql_result.processed_query,
            sql_generated=sql_result.sql_generated,
            results=sql_result.results,
            result_count=len(sql_result.results),
            execution_time_ms=execution_time,
            cache_hit=False,
            metadata=sql_result.metadata if request.include_metadata else None,
            error_message=sql_result.error_message,
            query_id=query_hash,
        )
        
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        logger.error(
            "Query execution failed",
            query=request.query,
            error=str(e),
            execution_time_ms=execution_time,
        )
        
        # Log failed query
        log_query_execution(
            query=request.query,
            execution_time=execution_time / 1000,
            success=False,
            error=str(e),
        )
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Query execution failed",
                "message": str(e),
                "query_id": query_hash,
            },
        )


@router.post("/batch", response_model=List[QueryResponse])
async def batch_query(
    requests: List[QueryRequest],
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> List[QueryResponse]:
    """Execute multiple natural language queries in batch."""
    
    if len(requests) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 queries allowed in batch",
        )
    
    results = []
    for request in requests:
        try:
            result = await natural_language_query(
                request=request,
                background_tasks=background_tasks,
                db=db,
            )
            results.append(result)
        except Exception as e:
            # Add failed result
            results.append(QueryResponse(
                success=False,
                query=request.query,
                results=[],
                result_count=0,
                execution_time_ms=0,
                cache_hit=False,
                error_message=str(e),
                query_id=hashlib.sha256(request.query.encode()).hexdigest(),
            ))
    
    return results


@router.get("/suggestions")
async def get_query_suggestions(
    partial_query: str = "",
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get query suggestions based on partial input."""
    
    try:
        query_service = QueryService(db)
        suggestions = await query_service.get_query_suggestions(
            partial_query=partial_query,
            limit=limit,
        )
        
        return {
            "suggestions": suggestions,
            "count": len(suggestions),
        }
        
    except Exception as e:
        logger.error("Failed to get query suggestions", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to get query suggestions",
        )


@router.get("/popular")
async def get_popular_queries(
    limit: int = 10,
    time_period: str = "24h",
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get popular queries based on usage statistics."""
    
    try:
        query_service = QueryService(db)
        popular_queries = await query_service.get_popular_queries(
            limit=limit,
            time_period=time_period,
        )
        
        return {
            "popular_queries": popular_queries,
            "count": len(popular_queries),
            "time_period": time_period,
        }
        
    except Exception as e:
        logger.error("Failed to get popular queries", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to get popular queries",
        )


async def store_query_analytics(
    db: AsyncSession,
    query_request: QueryRequest,
    sql_result: Any,
    execution_time: float,
    cache_hit: bool,
    query_hash: str,
    http_request: Request = None,
):
    """Store query analytics in background."""
    
    try:
        # Create query log entry
        query_log = QueryLog(
            query_hash=query_hash,
            original_query=query_request.query,
            processed_query=sql_result.processed_query,
            query_type="natural_language",
            user_id=query_request.user_id,
            session_id=query_request.session_id,
            ip_address=http_request.client.host if http_request else None,
            user_agent=http_request.headers.get("user-agent") if http_request else None,
            intent_detected=sql_result.metadata.get("intent") if sql_result.metadata else None,
            entities_extracted=sql_result.metadata.get("entities") if sql_result.metadata else None,
            confidence_score=sql_result.metadata.get("confidence") if sql_result.metadata else None,
            processing_time_ms=execution_time * 0.3,  # Estimate 30% for processing
            execution_time_ms=execution_time * 0.7,  # Estimate 70% for execution
            total_time_ms=execution_time,
            cache_hit=cache_hit,
            cache_key=f"query:{query_hash}:{query_request.max_results}",
            success=sql_result.success,
            error_message=sql_result.error_message,
        )
        
        db.add(query_log)
        await db.flush()  # Get the ID
        
        # Create query result entry
        if sql_result.success:
            query_result = QueryResult(
                query_log_id=query_log.id,
                result_type="table",
                result_format="json",
                result_data={"results": sql_result.results},
                result_summary=sql_result.metadata.get("summary") if sql_result.metadata else None,
                result_metadata=sql_result.metadata,
                row_count=len(sql_result.results),
                column_count=len(sql_result.results[0]) if sql_result.results else 0,
                data_size_bytes=len(str(sql_result.results).encode()),
                data_freshness_minutes=sql_result.metadata.get("data_freshness_minutes") if sql_result.metadata else None,
                confidence_score=sql_result.metadata.get("confidence") if sql_result.metadata else None,
            )
            
            db.add(query_result)
        
        # Create performance entry
        performance = QueryPerformance(
            query_log_id=query_log.id,
            parsing_time_ms=execution_time * 0.1,  # Estimate 10% for parsing
            planning_time_ms=execution_time * 0.2,  # Estimate 20% for planning
            execution_time_ms=execution_time * 0.7,  # Estimate 70% for execution
            total_time_ms=execution_time,
            tables_accessed=sql_result.metadata.get("tables_used") if sql_result.metadata else None,
            rows_scanned=sql_result.metadata.get("rows_scanned") if sql_result.metadata else None,
            rows_returned=len(sql_result.results),
            query_optimized=sql_result.metadata.get("optimized", False) if sql_result.metadata else False,
            optimization_applied=sql_result.metadata.get("optimizations") if sql_result.metadata else None,
        )
        
        db.add(performance)
        await db.commit()
        
    except Exception as e:
        logger.error("Failed to store query analytics", error=str(e))
        await db.rollback() 