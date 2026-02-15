"""
Command-line interface for Codebase Intelligence Analyzer.
"""

import click
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich import print as rprint
from dotenv import load_dotenv
import os

from codebase_intelligence.indexer.code_indexer import CodebaseIndexer
from codebase_intelligence.query.query_engine import QueryEngine

# Load environment variables
load_dotenv()

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """
    Codebase Intelligence Analyzer
    
    Context-aware code intelligence with natural language queries.
    Provides traceable references and private deployment options.
    """
    pass


@main.command()
@click.argument('codebase_path', type=click.Path(exists=True))
@click.option('--db-path', default='./chroma_db', help='Path to store vector database')
@click.option('--patterns', '-p', multiple=True, help='File patterns to index (e.g., "**/*.py")')
def index(codebase_path, db_path, patterns):
    """Index a codebase for intelligent querying."""
    console.print(f"\n[bold blue]🔍 Indexing codebase at:[/bold blue] {codebase_path}\n")
    
    try:
        indexer = CodebaseIndexer(db_path=db_path)
        
        # Convert patterns to list or None
        pattern_list = list(patterns) if patterns else None
        
        with console.status("[bold green]Parsing and indexing files..."):
            indexer.index_codebase(Path(codebase_path), file_patterns=pattern_list)
        
        # Show statistics
        stats = indexer.get_statistics()
        
        console.print("\n[bold green]✓ Indexing complete![/bold green]\n")
        console.print(f"Total elements indexed: [cyan]{stats['total_elements']}[/cyan]")
        console.print(f"Database location: [cyan]{stats['db_path']}[/cyan]\n")
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {e}\n")
        raise click.Abort()


@main.command()
@click.argument('question')
@click.option('--db-path', default='./chroma_db', help='Path to vector database')
@click.option('--no-llm', is_flag=True, help='Disable LLM-powered responses')
@click.option('--context', '-c', default=5, help='Number of code snippets to retrieve')
@click.option('--model', default='gpt-3.5-turbo', help='OpenAI model to use')
def query(question, db_path, no_llm, context, model):
    """Query the codebase with natural language."""
    console.print(f"\n[bold blue]💭 Question:[/bold blue] {question}\n")
    
    try:
        # Check if database exists
        if not Path(db_path).exists():
            console.print(f"[bold red]✗ Error:[/bold red] Database not found at {db_path}")
            console.print("Please index a codebase first using the 'index' command.\n")
            raise click.Abort()
        
        indexer = CodebaseIndexer(db_path=db_path)
        engine = QueryEngine(indexer, model=model)
        
        with console.status("[bold green]Searching codebase..."):
            result = engine.query(question, n_context=context, use_llm=not no_llm)
        
        # Display answer
        console.print(Panel(
            result['answer'],
            title="[bold green]Answer[/bold green]",
            border_style="green"
        ))
        
        # Display references
        if result['references']:
            console.print(f"\n[bold blue]📍 References ({len(result['references'])} found):[/bold blue]\n")
            
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("File", style="cyan")
            table.add_column("Element", style="yellow")
            table.add_column("Type", style="magenta")
            table.add_column("Lines", style="green")
            table.add_column("Relevance", style="blue")
            
            for ref in result['references']:
                relevance = f"{ref['relevance_score']:.2%}"
                lines = f"{ref['start_line']}-{ref['end_line']}"
                table.add_row(
                    ref['file'],
                    ref['element_name'],
                    ref['element_type'],
                    lines,
                    relevance
                )
            
            console.print(table)
        
        console.print()
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {e}\n")
        raise click.Abort()


@main.command()
@click.argument('element_name')
@click.option('--db-path', default='./chroma_db', help='Path to vector database')
def trace(element_name, db_path):
    """Trace dependencies for a code element."""
    console.print(f"\n[bold blue]🔗 Tracing dependencies for:[/bold blue] {element_name}\n")
    
    try:
        if not Path(db_path).exists():
            console.print(f"[bold red]✗ Error:[/bold red] Database not found at {db_path}")
            console.print("Please index a codebase first using the 'index' command.\n")
            raise click.Abort()
        
        indexer = CodebaseIndexer(db_path=db_path)
        engine = QueryEngine(indexer)
        
        with console.status("[bold green]Analyzing dependencies..."):
            result = engine.trace_dependencies(element_name)
        
        if not result.get('found'):
            console.print(f"[yellow]{result.get('message', 'Not found')}[/yellow]\n")
            return
        
        # Display dependencies
        for i, dep in enumerate(result.get('dependencies', []), 1):
            definition = dep['definition']
            console.print(f"[bold]Definition {i}:[/bold]")
            console.print(f"  File: [cyan]{definition['file']}[/cyan]")
            console.print(f"  Type: [yellow]{definition['type']}[/yellow]")
            console.print(f"  Line: [green]{definition['line']}[/green]\n")
            
            if dep.get('potential_usages'):
                console.print(f"  [bold]Potential usages:[/bold]")
                for usage in dep['potential_usages']:
                    console.print(f"    • {usage['file']}:{usage['line']} in '{usage['element']}'")
                console.print()
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {e}\n")
        raise click.Abort()


@main.command()
@click.argument('file_path')
@click.option('--db-path', default='./chroma_db', help='Path to vector database')
@click.option('--description', '-d', help='Description of planned changes')
def impact(file_path, db_path, description):
    """Analyze the impact of changes to a file."""
    console.print(f"\n[bold blue]🎯 Analyzing impact of changes to:[/bold blue] {file_path}\n")
    
    if description:
        console.print(f"[bold]Planned changes:[/bold] {description}\n")
    
    try:
        if not Path(db_path).exists():
            console.print(f"[bold red]✗ Error:[/bold red] Database not found at {db_path}")
            console.print("Please index a codebase first using the 'index' command.\n")
            raise click.Abort()
        
        indexer = CodebaseIndexer(db_path=db_path)
        engine = QueryEngine(indexer)
        
        with console.status("[bold green]Analyzing impact..."):
            result = engine.analyze_impact(file_path, description or "")
        
        if not result.get('found'):
            console.print(f"[yellow]{result.get('message', 'Not found')}[/yellow]\n")
            return
        
        # Display impact summary
        console.print(Panel(
            result['impact_summary'],
            title="[bold yellow]Impact Summary[/bold yellow]",
            border_style="yellow"
        ))
        
        # Display elements in the file
        if result.get('element_details'):
            console.print(f"\n[bold]Elements in {file_path}:[/bold]\n")
            
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Element", style="yellow")
            table.add_column("Type", style="magenta")
            table.add_column("Line", style="green")
            table.add_column("Dependencies", style="blue")
            
            for elem in result['element_details']:
                table.add_row(
                    elem['element'],
                    elem['type'],
                    str(elem['line']),
                    str(elem['dependency_count'])
                )
            
            console.print(table)
        
        # Display potentially impacted files
        if result.get('potentially_impacted_files'):
            console.print(f"\n[bold red]⚠️  Potentially impacted files:[/bold red]\n")
            for impacted_file in result['potentially_impacted_files']:
                console.print(f"  • [cyan]{impacted_file}[/cyan]")
        
        console.print()
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {e}\n")
        raise click.Abort()


@main.command()
@click.option('--db-path', default='./chroma_db', help='Path to vector database')
def stats(db_path):
    """Show statistics about the indexed codebase."""
    try:
        if not Path(db_path).exists():
            console.print(f"\n[bold red]✗ Error:[/bold red] Database not found at {db_path}\n")
            return
        
        indexer = CodebaseIndexer(db_path=db_path)
        stats = indexer.get_statistics()
        
        console.print("\n[bold blue]📊 Codebase Statistics[/bold blue]\n")
        console.print(f"Total indexed elements: [cyan]{stats['total_elements']}[/cyan]")
        console.print(f"Collection name: [cyan]{stats['collection_name']}[/cyan]")
        console.print(f"Database path: [cyan]{stats['db_path']}[/cyan]\n")
        
        # Try to read metadata if available
        metadata_path = Path(db_path) / 'metadata.json'
        if metadata_path.exists():
            with open(metadata_path) as f:
                metadata = json.load(f)
            
            console.print(f"Codebase path: [cyan]{metadata.get('codebase_path', 'N/A')}[/cyan]")
            console.print(f"Indexed files: [cyan]{metadata.get('file_count', 'N/A')}[/cyan]")
            console.print(f"Last indexed: [cyan]{metadata.get('indexed_at', 'N/A')}[/cyan]\n")
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {e}\n")
        raise click.Abort()


if __name__ == '__main__':
    main()
