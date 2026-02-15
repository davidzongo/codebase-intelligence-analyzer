"""
Example: Using Codebase Intelligence Analyzer programmatically
"""

from pathlib import Path
from codebase_intelligence import CodebaseIndexer, QueryEngine


def main():
    # Example 1: Index a codebase
    print("=" * 60)
    print("Example 1: Indexing a codebase")
    print("=" * 60)
    
    # Initialize indexer
    indexer = CodebaseIndexer(db_path="./example_db")
    
    # Index the current project as an example
    codebase_path = Path("../src")  # Adjust path as needed
    
    if codebase_path.exists():
        print(f"Indexing codebase at: {codebase_path}")
        indexer.index_codebase(codebase_path)
        
        # Get statistics
        stats = indexer.get_statistics()
        print(f"\nIndexed {stats['total_elements']} code elements")
    else:
        print(f"Path {codebase_path} does not exist. Using pre-indexed data.")
    
    # Example 2: Simple search
    print("\n" + "=" * 60)
    print("Example 2: Searching code with semantic search")
    print("=" * 60)
    
    query = "code parsing and analysis"
    print(f"\nSearching for: '{query}'")
    
    results = indexer.search(query, n_results=3)
    
    print(f"\nFound {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        print(f"{i}. {metadata['file_path']}")
        print(f"   Element: {metadata['element_name']} ({metadata['element_type']})")
        print(f"   Lines: {metadata['start_line']}-{metadata['end_line']}")
        print()
    
    # Example 3: Natural language query with LLM
    print("=" * 60)
    print("Example 3: Natural language query")
    print("=" * 60)
    
    engine = QueryEngine(indexer)
    
    # Note: This requires OPENAI_API_KEY environment variable
    question = "What components handle code parsing?"
    print(f"\nQuestion: {question}")
    
    # Use no-LLM mode if API key is not set
    result = engine.query(question, n_context=3, use_llm=False)
    
    print(f"\nAnswer:\n{result['answer']}\n")
    
    print("References:")
    for ref in result['references']:
        print(f"  • {ref['file']}:{ref['start_line']} - {ref['element_name']}")
    
    # Example 4: Dependency tracing
    print("\n" + "=" * 60)
    print("Example 4: Tracing dependencies")
    print("=" * 60)
    
    element_name = "CodeParser"
    print(f"\nTracing dependencies for: {element_name}")
    
    trace_result = engine.trace_dependencies(element_name)
    
    if trace_result.get('found'):
        print(f"\nFound {len(trace_result.get('dependencies', []))} definitions")
        for dep in trace_result.get('dependencies', []):
            definition = dep['definition']
            print(f"\nDefinition in {definition['file']} at line {definition['line']}")
            
            usages = dep.get('potential_usages', [])
            if usages:
                print(f"  Potential usages: {len(usages)}")
                for usage in usages[:3]:  # Show first 3
                    print(f"    - {usage['file']}:{usage['line']}")
    
    # Example 5: Impact analysis
    print("\n" + "=" * 60)
    print("Example 5: Analyzing impact of changes")
    print("=" * 60)
    
    file_to_change = "code_parser.py"
    print(f"\nAnalyzing impact of changes to: {file_to_change}")
    
    impact_result = engine.analyze_impact(file_to_change)
    
    if impact_result.get('found'):
        print(f"\n{impact_result['impact_summary']}")
        print(f"\nElements in file: {impact_result['elements_analyzed']}")
        
        impacted = impact_result.get('potentially_impacted_files', [])
        if impacted:
            print(f"\nPotentially impacted files:")
            for file in impacted[:5]:  # Show first 5
                print(f"  • {file}")
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
