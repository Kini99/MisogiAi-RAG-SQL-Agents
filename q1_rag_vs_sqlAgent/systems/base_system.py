"""
Base system interface for natural language query systems
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import time
import psutil
import os

@dataclass
class QueryResult:
    """Result of a natural language query"""
    query: str
    response: str
    execution_time: float
    memory_usage: float
    confidence_score: Optional[float] = None
    source_documents: Optional[List[str]] = None
    generated_sql: Optional[str] = None
    error: Optional[str] = None

@dataclass
class PerformanceMetrics:
    """Performance metrics for system evaluation"""
    avg_response_time: float
    avg_memory_usage: float
    success_rate: float
    accuracy_score: float
    total_queries: int
    failed_queries: int

class BaseQuerySystem(ABC):
    """Base class for natural language query systems"""
    
    def __init__(self, name: str):
        self.name = name
        self.process = psutil.Process(os.getpid())
    
    @abstractmethod
    def query(self, natural_language_query: str) -> QueryResult:
        """Execute a natural language query and return results"""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the system (load models, connect to databases, etc.)"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Clean up resources"""
        pass
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def measure_performance(self, query: str) -> QueryResult:
        """Measure performance of a query execution"""
        start_time = time.time()
        start_memory = self.get_memory_usage()
        
        try:
            result = self.query(query)
            end_time = time.time()
            end_memory = self.get_memory_usage()
            
            result.execution_time = end_time - start_time
            result.memory_usage = end_memory - start_memory
            
            return result
        except Exception as e:
            end_time = time.time()
            end_memory = self.get_memory_usage()
            
            return QueryResult(
                query=query,
                response="",
                execution_time=end_time - start_time,
                memory_usage=end_memory - start_memory,
                error=str(e)
            )
    
    def batch_query(self, queries: List[str]) -> List[QueryResult]:
        """Execute multiple queries and return results"""
        results = []
        for query in queries:
            result = self.measure_performance(query)
            results.append(result)
        return results
    
    def calculate_metrics(self, results: List[QueryResult]) -> PerformanceMetrics:
        """Calculate performance metrics from query results"""
        if not results:
            return PerformanceMetrics(0, 0, 0, 0, 0, 0)
        
        successful_results = [r for r in results if r.error is None]
        failed_results = [r for r in results if r.error is not None]
        
        avg_response_time = sum(r.execution_time for r in successful_results) / len(successful_results) if successful_results else 0
        avg_memory_usage = sum(r.memory_usage for r in successful_results) / len(successful_results) if successful_results else 0
        success_rate = len(successful_results) / len(results)
        
        return PerformanceMetrics(
            avg_response_time=avg_response_time,
            avg_memory_usage=avg_memory_usage,
            success_rate=success_rate,
            accuracy_score=0.0,  # To be implemented by specific systems
            total_queries=len(results),
            failed_queries=len(failed_results)
        ) 