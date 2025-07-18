"""
Command-line interface demo for RAG vs SQL Agent comparison
"""
import os
import sys
import asyncio
from typing import List, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

from systems.rag_system import RAGSystem
from systems.sql_agent_system import SQLAgentSystem
from systems.base_system import QueryResult
from evaluation.test_queries import get_benchmark_queries, get_queries_by_category
from config.settings import settings

console = Console()

class CLIDemo:
    """Command-line interface demo"""
    
    def __init__(self):
        self.rag_system = None
        self.sql_agent_system = None
        self.initialized = False
    
    def initialize_systems(self) -> bool:
        """Initialize both systems"""
        with console.status("[bold blue]Initializing systems...", spinner="dots"):
            try:
                # Initialize RAG system
                console.print("Initializing RAG system...")
                self.rag_system = RAGSystem()
                if not self.rag_system.initialize():
                    console.print("[red]Warning: RAG system initialization failed[/red]")
                    self.rag_system = None
                
                # Initialize SQL Agent system
                console.print("Initializing SQL Agent system...")
                self.sql_agent_system = SQLAgentSystem()
                if not self.sql_agent_system.initialize():
                    console.print("[red]Warning: SQL Agent system initialization failed[/red]")
                    self.sql_agent_system = None
                
                if self.rag_system or self.sql_agent_system:
                    self.initialized = True
                    console.print("[green]Systems initialized successfully![/green]")
                    return True
                else:
                    console.print("[red]No systems could be initialized[/red]")
                    return False
                    
            except Exception as e:
                console.print(f"[red]Error initializing systems: {e}[/red]")
                return False
    
    def display_menu(self):
        """Display main menu"""
        console.print("\n" + "="*60)
        console.print("[bold blue]E-commerce Customer Support System Demo[/bold blue]")
        console.print("[bold blue]RAG vs SQL Agent Comparison[/bold blue]")
        console.print("="*60)
        
        if not self.initialized:
            console.print("[red]Systems not initialized. Please run setup first.[/red]")
            return
        
        console.print("\n[bold cyan]Available Systems:[/bold cyan]")
        if self.rag_system:
            console.print("  🤖 RAG System: [green]Available[/green]")
        else:
            console.print("  🤖 RAG System: [red]Not Available[/red]")
        
        if self.sql_agent_system:
            console.print("  🗄️ SQL Agent: [green]Available[/green]")
        else:
            console.print("  🗄️ SQL Agent: [red]Not Available[/red]")
        
        console.print("\n[bold cyan]Options:[/bold cyan]")
        console.print("  1. Interactive Query Mode")
        console.print("  2. Run Sample Queries")
        console.print("  3. Performance Benchmark")
        console.print("  4. System Information")
        console.print("  5. Exit")
    
    def interactive_query(self):
        """Interactive query mode"""
        console.print("\n[bold green]Interactive Query Mode[/bold green]")
        console.print("Type 'quit' to exit, 'help' for sample queries\n")
        
        while True:
            query = Prompt.ask("[bold cyan]Enter your query[/bold cyan]")
            
            if query.lower() == 'quit':
                break
            elif query.lower() == 'help':
                self.show_sample_queries()
                continue
            elif not query.strip():
                continue
            
            self.execute_single_query(query)
    
    def execute_single_query(self, query: str):
        """Execute a single query and display results"""
        console.print(f"\n[bold yellow]Executing:[/bold yellow] {query}")
        
        results = {}
        
        # Execute RAG query
        if self.rag_system:
            with console.status("[blue]RAG System processing...", spinner="dots"):
                rag_result = self.rag_system.measure_performance(query)
                results['rag'] = rag_result
        
        # Execute SQL Agent query
        if self.sql_agent_system:
            with console.status("[blue]SQL Agent processing...", spinner="dots"):
                sql_result = self.sql_agent_system.measure_performance(query)
                results['sql_agent'] = sql_result
        
        # Display results
        self.display_query_results(query, results)
    
    def display_query_results(self, query: str, results: dict):
        """Display query results in a formatted table"""
        if not results:
            console.print("[red]No results to display[/red]")
            return
        
        # Create results table
        table = Table(title=f"Query Results: {query}")
        table.add_column("System", style="cyan", no_wrap=True)
        table.add_column("Response", style="green")
        table.add_column("Time (s)", style="yellow", justify="right")
        table.add_column("Memory (MB)", style="magenta", justify="right")
        table.add_column("Confidence", style="blue", justify="right")
        table.add_column("Details", style="white")
        
        for system_name, result in results.items():
            if result.error:
                table.add_row(
                    system_name.upper(),
                    f"[red]Error: {result.error}[/red]",
                    f"{result.execution_time:.3f}",
                    f"{result.memory_usage:.2f}",
                    "N/A",
                    "Error occurred"
                )
            else:
                # Truncate response for display
                response = result.response[:200] + "..." if len(result.response) > 200 else result.response
                
                details = []
                if hasattr(result, 'generated_sql') and result.generated_sql:
                    details.append(f"SQL: {result.generated_sql[:50]}...")
                if hasattr(result, 'source_documents') and result.source_documents:
                    details.append(f"Sources: {len(result.source_documents)}")
                
                table.add_row(
                    system_name.upper(),
                    response,
                    f"{result.execution_time:.3f}",
                    f"{result.memory_usage:.2f}",
                    f"{(result.confidence_score or 0) * 100:.1f}%",
                    "; ".join(details) if details else "N/A"
                )
        
        console.print(table)
        
        # Show comparison if both systems were used
        if len(results) == 2 and 'rag' in results and 'sql_agent' in results:
            self.show_comparison(results['rag'], results['sql_agent'])
    
    def show_comparison(self, rag_result: QueryResult, sql_result: QueryResult):
        """Show comparison between RAG and SQL Agent results"""
        console.print("\n[bold cyan]Performance Comparison:[/bold cyan]")
        
        comparison_table = Table()
        comparison_table.add_column("Metric", style="cyan")
        comparison_table.add_column("RAG", style="green")
        comparison_table.add_column("SQL Agent", style="blue")
        comparison_table.add_column("Winner", style="yellow")
        
        # Response time comparison
        rag_time = rag_result.execution_time
        sql_time = sql_result.execution_time
        time_winner = "RAG" if rag_time < sql_time else "SQL Agent"
        
        comparison_table.add_row(
            "Response Time",
            f"{rag_time:.3f}s",
            f"{sql_time:.3f}s",
            time_winner
        )
        
        # Memory usage comparison
        rag_memory = rag_result.memory_usage
        sql_memory = sql_result.memory_usage
        memory_winner = "RAG" if rag_memory < sql_memory else "SQL Agent"
        
        comparison_table.add_row(
            "Memory Usage",
            f"{rag_memory:.2f}MB",
            f"{sql_memory:.2f}MB",
            memory_winner
        )
        
        # Confidence comparison
        rag_conf = rag_result.confidence_score or 0
        sql_conf = sql_result.confidence_score or 0
        conf_winner = "RAG" if rag_conf > sql_conf else "SQL Agent"
        
        comparison_table.add_row(
            "Confidence",
            f"{rag_conf * 100:.1f}%",
            f"{sql_conf * 100:.1f}%",
            conf_winner
        )
        
        console.print(comparison_table)
    
    def run_sample_queries(self):
        """Run a set of sample queries"""
        console.print("\n[bold green]Sample Queries Mode[/bold green]")
        
        # Get sample queries
        sample_queries = get_benchmark_queries()[:5]  # Limit to 5 for demo
        
        console.print(f"Running {len(sample_queries)} sample queries...\n")
        
        for i, query in enumerate(sample_queries, 1):
            console.print(f"[bold cyan]Query {i}/{len(sample_queries)}:[/bold cyan] {query}")
            self.execute_single_query(query)
            
            if i < len(sample_queries):
                if not Confirm.ask("\nContinue to next query?"):
                    break
                console.print()
    
    def show_sample_queries(self):
        """Show available sample queries"""
        console.print("\n[bold cyan]Sample Queries:[/bold cyan]")
        
        categories = [
            "simple_lookup",
            "aggregation_queries",
            "join_queries",
            "complex_analytics"
        ]
        
        for category in categories:
            queries = get_queries_by_category(category)
            console.print(f"\n[bold yellow]{category.replace('_', ' ').title()}:[/bold yellow]")
            for query in queries[:3]:  # Show first 3 from each category
                console.print(f"  • {query}")
    
    def show_system_info(self):
        """Show system information"""
        console.print("\n[bold green]System Information[/bold green]")
        
        info_table = Table()
        info_table.add_column("Component", style="cyan")
        info_table.add_column("Status", style="green")
        info_table.add_column("Details", style="white")
        
        # RAG System info
        if self.rag_system:
            info_table.add_row(
                "RAG System",
                "✅ Available",
                f"Embedding Model: {settings.EMBEDDING_MODEL}"
            )
        else:
            info_table.add_row("RAG System", "❌ Not Available", "Initialization failed")
        
        # SQL Agent info
        if self.sql_agent_system:
            info_table.add_row(
                "SQL Agent",
                "✅ Available",
                f"LLM Model: {settings.OPENAI_MODEL}"
            )
        else:
            info_table.add_row("SQL Agent", "❌ Not Available", "Initialization failed")
        
        # Database info
        db_url = settings.DATABASE_URL
        if db_url:
            info_table.add_row(
                "Database",
                "✅ Configured",
                f"URL: {db_url.split('@')[1] if '@' in db_url else 'Local'}"
            )
        else:
            info_table.add_row("Database", "❌ Not Configured", "DATABASE_URL not set")
        
        console.print(info_table)
    
    def cleanup(self):
        """Clean up resources"""
        if self.rag_system:
            self.rag_system.cleanup()
        if self.sql_agent_system:
            self.sql_agent_system.cleanup()

@click.command()
@click.option('--setup', is_flag=True, help='Initialize systems')
@click.option('--interactive', is_flag=True, help='Start interactive mode')
@click.option('--sample', is_flag=True, help='Run sample queries')
@click.option('--info', is_flag=True, help='Show system information')
def main(setup, interactive, sample, info):
    """E-commerce Customer Support System CLI Demo"""
    
    demo = CLIDemo()
    
    try:
        # Initialize systems if requested or if no other mode specified
        if setup or (not interactive and not sample and not info):
            if not demo.initialize_systems():
                console.print("[red]Failed to initialize systems. Exiting.[/red]")
                return
        
        # Run requested mode
        if interactive:
            if not demo.initialized:
                console.print("[red]Systems not initialized. Use --setup first.[/red]")
                return
            demo.interactive_query()
        elif sample:
            if not demo.initialized:
                console.print("[red]Systems not initialized. Use --setup first.[/red]")
                return
            demo.run_sample_queries()
        elif info:
            demo.show_system_info()
        else:
            # Default to menu mode
            while True:
                demo.display_menu()
                choice = Prompt.ask("\nSelect option", choices=["1", "2", "3", "4", "5"])
                
                if choice == "1":
                    demo.interactive_query()
                elif choice == "2":
                    demo.run_sample_queries()
                elif choice == "3":
                    console.print("[yellow]Performance benchmark not implemented in CLI mode. Use the web interface or run evaluation/benchmark.py[/yellow]")
                elif choice == "4":
                    demo.show_system_info()
                elif choice == "5":
                    break
                
                if choice != "5":
                    input("\nPress Enter to continue...")
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    finally:
        demo.cleanup()

if __name__ == "__main__":
    main() 