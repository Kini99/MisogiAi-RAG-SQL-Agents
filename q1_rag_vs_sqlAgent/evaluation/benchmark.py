"""
Benchmarking framework for RAG vs SQL Agent comparison
"""
import time
import json
import statistics
from typing import List, Dict, Any, Tuple
from datetime import datetime
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.progress import track

from systems.rag_system import RAGSystem
from systems.sql_agent_system import SQLAgentSystem
from systems.base_system import QueryResult, PerformanceMetrics
from evaluation.test_queries import get_benchmark_queries, get_all_test_queries, QUERY_COMPLEXITY
from evaluation.metrics import calculate_accuracy_score, calculate_response_quality

console = Console()

class BenchmarkRunner:
    """Main benchmarking class"""
    
    def __init__(self):
        self.rag_system = None
        self.sql_agent_system = None
        self.results = {
            "rag": {},
            "sql_agent": {},
            "comparison": {}
        }
    
    def initialize_systems(self) -> bool:
        """Initialize both systems"""
        console.print("Initializing systems...", style="bold blue")
        
        try:
            # Initialize RAG system
            console.print("Initializing RAG system...")
            self.rag_system = RAGSystem()
            if not self.rag_system.initialize():
                console.print("Failed to initialize RAG system", style="bold red")
                return False
            
            # Initialize SQL Agent system
            console.print("Initializing SQL Agent system...")
            self.sql_agent_system = SQLAgentSystem()
            if not self.sql_agent_system.initialize():
                console.print("Failed to initialize SQL Agent system", style="bold red")
                return False
            
            console.print("Both systems initialized successfully!", style="bold green")
            return True
            
        except Exception as e:
            console.print(f"Error initializing systems: {e}", style="bold red")
            return False
    
    def run_benchmark(self, queries: List[str] = None, iterations: int = 3) -> Dict[str, Any]:
        """Run comprehensive benchmark"""
        if queries is None:
            queries = get_benchmark_queries()
        
        console.print(f"Running benchmark with {len(queries)} queries, {iterations} iterations each", style="bold blue")
        
        # Run RAG system benchmark
        console.print("\n[bold cyan]Testing RAG System...[/bold cyan]")
        rag_results = self._benchmark_system(self.rag_system, queries, iterations)
        
        # Run SQL Agent system benchmark
        console.print("\n[bold cyan]Testing SQL Agent System...[/bold cyan]")
        sql_agent_results = self._benchmark_system(self.sql_agent_system, queries, iterations)
        
        # Compare results
        comparison = self._compare_results(rag_results, sql_agent_results)
        
        self.results = {
            "rag": rag_results,
            "sql_agent": sql_agent_results,
            "comparison": comparison,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_queries": len(queries),
                "iterations": iterations,
                "systems_tested": ["RAG", "SQL Agent"]
            }
        }
        
        return self.results
    
    def _benchmark_system(self, system, queries: List[str], iterations: int) -> Dict[str, Any]:
        """Benchmark a single system"""
        all_results = []
        
        for i in range(iterations):
            console.print(f"Iteration {i+1}/{iterations}")
            
            for query in track(queries, description=f"Processing queries (iteration {i+1})"):
                result = system.measure_performance(query)
                all_results.append(result)
        
        # Calculate metrics
        metrics = system.calculate_metrics(all_results)
        
        # Calculate accuracy scores
        accuracy_scores = []
        quality_scores = []
        
        for result in all_results:
            if result.error is None:
                accuracy = calculate_accuracy_score(result.query, result.response)
                quality = calculate_response_quality(result.response)
                accuracy_scores.append(accuracy)
                quality_scores.append(quality)
        
        # Update metrics with accuracy and quality
        if accuracy_scores:
            metrics.accuracy_score = statistics.mean(accuracy_scores)
        if quality_scores:
            metrics.quality_score = statistics.mean(quality_scores)
        
        return {
            "metrics": metrics,
            "detailed_results": all_results,
            "accuracy_scores": accuracy_scores,
            "quality_scores": quality_scores
        }
    
    def _compare_results(self, rag_results: Dict, sql_agent_results: Dict) -> Dict[str, Any]:
        """Compare results between systems"""
        rag_metrics = rag_results["metrics"]
        sql_metrics = sql_agent_results["metrics"]
        
        comparison = {
            "performance_comparison": {
                "response_time": {
                    "rag": rag_metrics.avg_response_time,
                    "sql_agent": sql_metrics.avg_response_time,
                    "winner": "RAG" if rag_metrics.avg_response_time < sql_metrics.avg_response_time else "SQL Agent",
                    "difference": abs(rag_metrics.avg_response_time - sql_metrics.avg_response_time)
                },
                "memory_usage": {
                    "rag": rag_metrics.avg_memory_usage,
                    "sql_agent": sql_metrics.avg_memory_usage,
                    "winner": "RAG" if rag_metrics.avg_memory_usage < sql_metrics.avg_memory_usage else "SQL Agent",
                    "difference": abs(rag_metrics.avg_memory_usage - sql_metrics.avg_memory_usage)
                },
                "success_rate": {
                    "rag": rag_metrics.success_rate,
                    "sql_agent": sql_metrics.success_rate,
                    "winner": "RAG" if rag_metrics.success_rate > sql_metrics.success_rate else "SQL Agent",
                    "difference": abs(rag_metrics.success_rate - sql_metrics.success_rate)
                },
                "accuracy": {
                    "rag": rag_metrics.accuracy_score,
                    "sql_agent": sql_metrics.accuracy_score,
                    "winner": "RAG" if rag_metrics.accuracy_score > sql_metrics.accuracy_score else "SQL Agent",
                    "difference": abs(rag_metrics.accuracy_score - sql_metrics.accuracy_score)
                }
            },
            "overall_winner": self._determine_overall_winner(rag_metrics, sql_metrics),
            "recommendations": self._generate_recommendations(rag_metrics, sql_metrics)
        }
        
        return comparison
    
    def _determine_overall_winner(self, rag_metrics: PerformanceMetrics, sql_metrics: PerformanceMetrics) -> str:
        """Determine overall winner based on weighted criteria"""
        # Weighted scoring system
        weights = {
            "response_time": 0.25,
            "memory_usage": 0.15,
            "success_rate": 0.30,
            "accuracy": 0.30
        }
        
        rag_score = (
            (1 / (rag_metrics.avg_response_time + 0.1)) * weights["response_time"] +
            (1 / (rag_metrics.avg_memory_usage + 0.1)) * weights["memory_usage"] +
            rag_metrics.success_rate * weights["success_rate"] +
            rag_metrics.accuracy_score * weights["accuracy"]
        )
        
        sql_score = (
            (1 / (sql_metrics.avg_response_time + 0.1)) * weights["response_time"] +
            (1 / (sql_metrics.avg_memory_usage + 0.1)) * weights["memory_usage"] +
            sql_metrics.success_rate * weights["success_rate"] +
            sql_metrics.accuracy_score * weights["accuracy"]
        )
        
        if rag_score > sql_score:
            return "RAG"
        elif sql_score > rag_score:
            return "SQL Agent"
        else:
            return "Tie"
    
    def _generate_recommendations(self, rag_metrics: PerformanceMetrics, sql_metrics: PerformanceMetrics) -> List[str]:
        """Generate recommendations based on results"""
        recommendations = []
        
        # Performance recommendations
        if rag_metrics.avg_response_time < sql_metrics.avg_response_time:
            recommendations.append("RAG system provides faster response times for real-time queries")
        else:
            recommendations.append("SQL Agent provides faster response times for structured queries")
        
        if rag_metrics.success_rate > sql_metrics.success_rate:
            recommendations.append("RAG system has higher success rate for natural language queries")
        else:
            recommendations.append("SQL Agent has higher success rate for database queries")
        
        if rag_metrics.accuracy_score > sql_metrics.accuracy_score:
            recommendations.append("RAG system provides more accurate responses")
        else:
            recommendations.append("SQL Agent provides more accurate responses")
        
        # Use case recommendations
        recommendations.append("Use RAG for exploratory queries and natural language interactions")
        recommendations.append("Use SQL Agent for precise data retrieval and complex analytics")
        recommendations.append("Consider hybrid approach for comprehensive coverage")
        
        return recommendations
    
    def display_results(self):
        """Display benchmark results in a formatted table"""
        if not self.results.get("comparison"):
            console.print("No results to display. Run benchmark first.", style="bold red")
            return
        
        comparison = self.results["comparison"]
        
        # Performance comparison table
        table = Table(title="Performance Comparison: RAG vs SQL Agent")
        table.add_column("Metric", style="cyan")
        table.add_column("RAG System", style="green")
        table.add_column("SQL Agent", style="blue")
        table.add_column("Winner", style="yellow")
        table.add_column("Difference", style="magenta")
        
        perf_comp = comparison["performance_comparison"]
        
        for metric, data in perf_comp.items():
            table.add_row(
                metric.replace("_", " ").title(),
                f"{data['rag']:.4f}",
                f"{data['sql_agent']:.4f}",
                data["winner"],
                f"{data['difference']:.4f}"
            )
        
        console.print(table)
        
        # Overall winner
        console.print(f"\n[bold green]Overall Winner: {comparison['overall_winner']}[/bold green]")
        
        # Recommendations
        console.print("\n[bold cyan]Recommendations:[/bold cyan]")
        for i, rec in enumerate(comparison["recommendations"], 1):
            console.print(f"{i}. {rec}")
    
    def save_results(self, filename: str = None):
        """Save benchmark results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_results_{timestamp}.json"
        
        # Convert results to serializable format
        serializable_results = self._make_serializable(self.results)
        
        with open(filename, 'w') as f:
            json.dump(serializable_results, f, indent=2, default=str)
        
        console.print(f"Results saved to {filename}", style="bold green")
    
    def _make_serializable(self, obj):
        """Convert objects to serializable format"""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return obj
    
    def cleanup(self):
        """Clean up resources"""
        if self.rag_system:
            self.rag_system.cleanup()
        if self.sql_agent_system:
            self.sql_agent_system.cleanup()

def main():
    """Main benchmark execution"""
    console.print("E-commerce Customer Support System Benchmark", style="bold blue")
    console.print("RAG vs SQL Agent Comparison\n", style="bold blue")
    
    # Initialize benchmark runner
    runner = BenchmarkRunner()
    
    try:
        # Initialize systems
        if not runner.initialize_systems():
            console.print("Failed to initialize systems. Exiting.", style="bold red")
            return
        
        # Run benchmark
        results = runner.run_benchmark()
        
        # Display results
        runner.display_results()
        
        # Save results
        runner.save_results()
        
    except KeyboardInterrupt:
        console.print("\nBenchmark interrupted by user", style="bold yellow")
    except Exception as e:
        console.print(f"Error during benchmark: {e}", style="bold red")
    finally:
        runner.cleanup()

if __name__ == "__main__":
    main() 