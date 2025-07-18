"""
FastAPI web application for demonstrating RAG vs SQL Agent systems
"""
import os
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from systems.rag_system import RAGSystem
from systems.sql_agent_system import SQLAgentSystem
from systems.base_system import QueryResult
from config.settings import settings

# Initialize FastAPI app
app = FastAPI(
    title="E-commerce Customer Support System",
    description="RAG vs SQL Agent Comparison Demo",
    version="1.0.0"
)

# Global system instances
rag_system = None
sql_agent_system = None

class QueryRequest(BaseModel):
    query: str
    system: str = "both"  # "rag", "sql_agent", or "both"

class QueryResponse(BaseModel):
    query: str
    rag_response: Optional[Dict[str, Any]] = None
    sql_agent_response: Optional[Dict[str, Any]] = None
    comparison: Optional[Dict[str, Any]] = None
    timestamp: str

@app.on_event("startup")
async def startup_event():
    """Initialize systems on startup"""
    global rag_system, sql_agent_system
    
    print("Initializing systems...")
    
    try {
        # Initialize RAG system
        rag_system = RAGSystem()
        if not rag_system.initialize():
            print("Warning: RAG system initialization failed")
            rag_system = None
        
        # Initialize SQL Agent system
        sql_agent_system = SQLAgentSystem()
        if not sql_agent_system.initialize():
            print("Warning: SQL Agent system initialization failed")
            sql_agent_system = None
            
        print("Systems initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing systems: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up systems on shutdown"""
    global rag_system, sql_agent_system
    
    if rag_system:
        rag_system.cleanup()
    if sql_agent_system:
        sql_agent_system.cleanup()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Main demo page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>E-commerce Customer Support System - RAG vs SQL Agent Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; margin-bottom: 30px; }
            .demo-section { margin-bottom: 30px; }
            .query-form { background: #f9f9f9; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input[type="text"], select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; }
            button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
            button:hover { background: #0056b3; }
            .results { margin-top: 20px; }
            .result-box { background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; padding: 15px; margin-bottom: 15px; }
            .result-title { font-weight: bold; margin-bottom: 10px; color: #495057; }
            .result-content { white-space: pre-wrap; font-family: monospace; }
            .comparison { background: #e7f3ff; border: 1px solid #b3d9ff; border-radius: 4px; padding: 15px; margin-top: 20px; }
            .sample-queries { background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px; padding: 15px; margin-top: 20px; }
            .sample-queries h3 { margin-top: 0; color: #856404; }
            .query-example { cursor: pointer; color: #007bff; margin: 5px 0; }
            .query-example:hover { text-decoration: underline; }
            .loading { text-align: center; color: #666; font-style: italic; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛒 E-commerce Customer Support System</h1>
            <h2 style="text-align: center; color: #666;">RAG vs SQL Agent Comparison Demo</h2>
            
            <div class="demo-section">
                <div class="query-form">
                    <form id="queryForm">
                        <div class="form-group">
                            <label for="query">Natural Language Query:</label>
                            <input type="text" id="query" name="query" placeholder="e.g., How many customers do we have?" required>
                        </div>
                        <div class="form-group">
                            <label for="system">System to Test:</label>
                            <select id="system" name="system">
                                <option value="both">Both Systems (Compare)</option>
                                <option value="rag">RAG System Only</option>
                                <option value="sql_agent">SQL Agent Only</option>
                            </select>
                        </div>
                        <button type="submit">Execute Query</button>
                    </form>
                </div>
                
                <div id="results" class="results" style="display: none;">
                    <div id="loading" class="loading">Processing query...</div>
                    <div id="ragResult" class="result-box" style="display: none;">
                        <div class="result-title">🤖 RAG System Response</div>
                        <div id="ragContent" class="result-content"></div>
                    </div>
                    <div id="sqlResult" class="result-box" style="display: none;">
                        <div class="result-title">🗄️ SQL Agent Response</div>
                        <div id="sqlContent" class="result-content"></div>
                    </div>
                    <div id="comparison" class="comparison" style="display: none;">
                        <div class="result-title">📊 Performance Comparison</div>
                        <div id="comparisonContent"></div>
                    </div>
                </div>
            </div>
            
            <div class="sample-queries">
                <h3>💡 Sample Queries to Try</h3>
                <div class="query-example" onclick="setQuery('How many customers do we have?')">How many customers do we have?</div>
                <div class="query-example" onclick="setQuery('What is the total revenue from all orders?')">What is the total revenue from all orders?</div>
                <div class="query-example" onclick="setQuery('Show me all products in the Electronics category')">Show me all products in the Electronics category</div>
                <div class="query-example" onclick="setQuery('Which customers have spent the most money?')">Which customers have spent the most money?</div>
                <div class="query-example" onclick="setQuery('What are our top 5 selling products?')">What are our top 5 selling products?</div>
                <div class="query-example" onclick="setQuery('Show me customers who haven\'t placed an order in the last 3 months')">Show me customers who haven't placed an order in the last 3 months</div>
                <div class="query-example" onclick="setQuery('What is the average rating across all products?')">What is the average rating across all products?</div>
                <div class="query-example" onclick="setQuery('List all support tickets with customer contact information')">List all support tickets with customer contact information</div>
            </div>
        </div>
        
        <script>
            function setQuery(query) {
                document.getElementById('query').value = query;
            }
            
            document.getElementById('queryForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const query = document.getElementById('query').value;
                const system = document.getElementById('system').value;
                
                // Show results area and loading
                document.getElementById('results').style.display = 'block';
                document.getElementById('loading').style.display = 'block';
                document.getElementById('ragResult').style.display = 'none';
                document.getElementById('sqlResult').style.display = 'none';
                document.getElementById('comparison').style.display = 'none';
                
                try {
                    const response = await fetch('/query', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            query: query,
                            system: system
                        })
                    });
                    
                    const result = await response.json();
                    
                    // Hide loading
                    document.getElementById('loading').style.display = 'none';
                    
                    // Display RAG results
                    if (result.rag_response) {
                        document.getElementById('ragResult').style.display = 'block';
                        document.getElementById('ragContent').textContent = 
                            `Response: ${result.rag_response.response}\n\n` +
                            `Execution Time: ${result.rag_response.execution_time.toFixed(3)}s\n` +
                            `Memory Usage: ${result.rag_response.memory_usage.toFixed(2)}MB\n` +
                            `Confidence: ${(result.rag_response.confidence_score * 100).toFixed(1)}%`;
                    }
                    
                    // Display SQL Agent results
                    if (result.sql_agent_response) {
                        document.getElementById('sqlResult').style.display = 'block';
                        document.getElementById('sqlContent').textContent = 
                            `Response: ${result.sql_agent_response.response}\n\n` +
                            `Generated SQL: ${result.sql_agent_response.generated_sql || 'N/A'}\n` +
                            `Execution Time: ${result.sql_agent_response.execution_time.toFixed(3)}s\n` +
                            `Memory Usage: ${result.sql_agent_response.memory_usage.toFixed(2)}MB\n` +
                            `Confidence: ${(result.sql_agent_response.confidence_score * 100).toFixed(1)}%`;
                    }
                    
                    // Display comparison
                    if (result.comparison) {
                        document.getElementById('comparison').style.display = 'block';
                        document.getElementById('comparisonContent').textContent = 
                            `Winner: ${result.comparison.winner}\n` +
                            `Response Time Difference: ${result.comparison.response_time_diff.toFixed(3)}s\n` +
                            `Memory Usage Difference: ${result.comparison.memory_diff.toFixed(2)}MB`;
                    }
                    
                } catch (error) {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('loading').textContent = 'Error: ' + error.message;
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/query")
async def execute_query(request: QueryRequest) -> QueryResponse:
    """Execute a natural language query using the specified system(s)"""
    global rag_system, sql_agent_system
    
    if not rag_system and not sql_agent_system:
        raise HTTPException(status_code=500, detail="No systems available")
    
    rag_response = None
    sql_agent_response = None
    comparison = None
    
    try:
        # Execute RAG query if requested
        if request.system in ["rag", "both"] and rag_system:
            rag_result = rag_system.measure_performance(request.query)
            rag_response = {
                "response": rag_result.response,
                "execution_time": rag_result.execution_time,
                "memory_usage": rag_result.memory_usage,
                "confidence_score": rag_result.confidence_score or 0.0,
                "source_documents": rag_result.source_documents
            }
        
        # Execute SQL Agent query if requested
        if request.system in ["sql_agent", "both"] and sql_agent_system:
            sql_result = sql_agent_system.measure_performance(request.query)
            sql_agent_response = {
                "response": sql_result.response,
                "execution_time": sql_result.execution_time,
                "memory_usage": sql_result.memory_usage,
                "confidence_score": sql_result.confidence_score or 0.0,
                "generated_sql": sql_result.generated_sql
            }
        
        # Generate comparison if both systems were used
        if request.system == "both" and rag_response and sql_agent_response:
            comparison = {
                "winner": "RAG" if rag_response["execution_time"] < sql_agent_response["execution_time"] else "SQL Agent",
                "response_time_diff": abs(rag_response["execution_time"] - sql_agent_response["execution_time"]),
                "memory_diff": abs(rag_response["memory_usage"] - sql_agent_response["memory_usage"]),
                "accuracy_diff": abs(rag_response["confidence_score"] - sql_agent_response["confidence_score"])
            }
        
        return QueryResponse(
            query=request.query,
            rag_response=rag_response,
            sql_agent_response=sql_agent_response,
            comparison=comparison,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "rag_system": rag_system is not None,
        "sql_agent_system": sql_agent_system is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/sample-queries")
async def get_sample_queries():
    """Get sample queries for testing"""
    from evaluation.test_queries import get_benchmark_queries
    
    return {
        "queries": get_benchmark_queries(),
        "categories": [
            "simple_lookup",
            "aggregation_queries", 
            "join_queries",
            "complex_analytics",
            "business_intelligence"
        ]
    }

def main():
    """Run the web application"""
    print("Starting E-commerce Customer Support System Demo...")
    print(f"Server will be available at: http://{settings.DEMO_HOST}:{settings.DEMO_PORT}")
    
    uvicorn.run(
        "demo.web_app:app",
        host=settings.DEMO_HOST,
        port=settings.DEMO_PORT,
        reload=True
    )

if __name__ == "__main__":
    main() 