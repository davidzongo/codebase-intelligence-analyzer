"""
Query engine for natural language queries over codebase.
Uses LLM to provide context-aware responses with traceable references.
"""

from typing import List, Dict, Any, Optional
import os
import json
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from ..indexer.code_indexer import CodebaseIndexer


class QueryEngine:
    """Process natural language queries about the codebase."""
    
    # System message for LLM prompts
    SYSTEM_MESSAGE = "You are a helpful code analysis assistant that provides accurate, traceable answers about codebases."
    
    # Instructions for LLM responses
    LLM_INSTRUCTIONS = """Instructions:
- Provide a clear, concise answer to the question
- Reference specific files, functions, and line numbers when relevant
- If the code context doesn't fully answer the question, mention what information is available
- Keep your answer focused and technical"""
    
    def __init__(self, indexer: CodebaseIndexer, api_key: Optional[str] = None, 
                 model: str = "gpt-3.5-turbo"):
        """
        Initialize the query engine.
        
        Args:
            indexer: CodebaseIndexer instance with indexed codebase
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: OpenAI model to use
        """
        self.indexer = indexer
        self.model = model
        
        # Initialize OpenAI client if available
        if OpenAI is not None:
            self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
            self.llm_available = True
        else:
            self.client = None
            self.llm_available = False
    
    def query(self, question: str, n_context: int = 5, use_llm: bool = True) -> Dict[str, Any]:
        """
        Query the codebase with a natural language question.
        
        Args:
            question: Natural language question about the code
            n_context: Number of code snippets to retrieve as context
            use_llm: Whether to use LLM for generating response
            
        Returns:
            Dictionary containing answer and references
        """
        # Search for relevant code snippets
        search_results = self.indexer.search(question, n_results=n_context)
        
        if not search_results:
            return {
                'answer': 'No relevant code found for your question.',
                'references': [],
                'question': question,
            }
        
        # Format references
        references = self._format_references(search_results)
        
        # Generate answer
        if use_llm and self.llm_available and self.client:
            answer = self._generate_llm_answer(question, search_results)
        else:
            answer = self._generate_simple_answer(search_results)
        
        return {
            'answer': answer,
            'references': references,
            'question': question,
            'context_count': len(search_results),
        }
    
    def _format_references(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format search results into traceable references."""
        references = []
        
        for result in search_results:
            metadata = result['metadata']
            references.append({
                'file': metadata['file_path'],
                'element_type': metadata['element_type'],
                'element_name': metadata['element_name'],
                'start_line': metadata['start_line'],
                'end_line': metadata['end_line'],
                'language': metadata['language'],
                'relevance_score': 1 - result['distance'] if result.get('distance') else 1.0,
            })
        
        return references
    
    def _generate_simple_answer(self, search_results: List[Dict[str, Any]]) -> str:
        """Generate a simple answer without LLM."""
        if not search_results:
            return "No relevant code found."
        
        top_result = search_results[0]
        metadata = top_result['metadata']
        
        answer_parts = [
            f"Found relevant code in {metadata['file_path']}:",
            f"- {metadata['element_type']}: {metadata['element_name']}",
            f"- Location: lines {metadata['start_line']}-{metadata['end_line']}",
        ]
        
        if metadata.get('docstring'):
            answer_parts.append(f"- Documentation: {metadata['docstring'][:200]}")
        
        answer_parts.append(f"\nFound {len(search_results)} relevant code elements.")
        
        return "\n".join(answer_parts)
    
    def _generate_llm_answer(self, question: str, search_results: List[Dict[str, Any]]) -> str:
        """Generate answer using LLM with context from search results."""
        # Build context from search results
        context_parts = []
        for i, result in enumerate(search_results, 1):
            metadata = result['metadata']
            context_parts.append(
                f"[Context {i}]\n"
                f"File: {metadata['file_path']}\n"
                f"Element: {metadata['element_type']} '{metadata['element_name']}'\n"
                f"Location: lines {metadata['start_line']}-{metadata['end_line']}\n"
                f"Code:\n{result['document'][:500]}\n"
            )
        
        context = "\n---\n".join(context_parts)
        
        # Create prompt for LLM
        prompt = f"""You are a code analysis assistant. Answer the user's question about the codebase using the provided code snippets as context.

Question: {question}

Code Context:
{context}

{self.LLM_INSTRUCTIONS}

Answer:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_MESSAGE},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500,
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            return self._generate_simple_answer(search_results)
    
    def trace_dependencies(self, element_name: str) -> Dict[str, Any]:
        """
        Trace dependencies for a given element (function, class, etc.).
        
        Args:
            element_name: Name of the element to trace
            
        Returns:
            Dictionary containing dependency information
        """
        # Search for the element
        results = self.indexer.search(f"definition of {element_name}", n_results=10)
        
        if not results:
            return {
                'element': element_name,
                'found': False,
                'message': f'Element "{element_name}" not found in codebase.',
            }
        
        # Find exact matches
        exact_matches = [
            r for r in results 
            if r['metadata']['element_name'] == element_name
        ]
        
        if not exact_matches:
            exact_matches = results[:3]  # Use top 3 if no exact match
        
        # For each match, search for usages
        dependencies = []
        for match in exact_matches:
            usage_query = f"uses {element_name} calls {element_name}"
            usages = self.indexer.search(usage_query, n_results=5)
            
            dependencies.append({
                'definition': {
                    'file': match['metadata']['file_path'],
                    'type': match['metadata']['element_type'],
                    'line': match['metadata']['start_line'],
                },
                'potential_usages': [
                    {
                        'file': u['metadata']['file_path'],
                        'element': u['metadata']['element_name'],
                        'line': u['metadata']['start_line'],
                    }
                    for u in usages
                ]
            })
        
        return {
            'element': element_name,
            'found': True,
            'dependencies': dependencies,
        }
    
    def analyze_impact(self, file_path: str, changes_description: str = "") -> Dict[str, Any]:
        """
        Analyze the potential impact of changes to a file.
        
        Args:
            file_path: Path to the file being changed
            changes_description: Optional description of changes
            
        Returns:
            Dictionary containing impact analysis
        """
        # Search for the file
        file_query = f"file {file_path}"
        file_results = self.indexer.search(file_query, n_results=10)
        
        if not file_results:
            return {
                'file': file_path,
                'found': False,
                'message': f'File "{file_path}" not found in indexed codebase.',
            }
        
        # Get all elements in the file
        file_elements = [
            r for r in file_results 
            if r['metadata']['file_path'] == file_path
        ]
        
        # For each element, check for potential dependencies
        impacted_files = set()
        element_impacts = []
        
        for element in file_elements[:5]:  # Limit to top 5 elements
            element_name = element['metadata']['element_name']
            deps = self.trace_dependencies(element_name)
            
            if deps.get('found') and deps.get('dependencies'):
                for dep in deps['dependencies']:
                    for usage in dep.get('potential_usages', []):
                        if usage['file'] != file_path:
                            impacted_files.add(usage['file'])
                
                element_impacts.append({
                    'element': element_name,
                    'type': element['metadata']['element_type'],
                    'line': element['metadata']['start_line'],
                    'dependency_count': len(deps.get('dependencies', [])),
                })
        
        return {
            'file': file_path,
            'found': True,
            'elements_analyzed': len(element_impacts),
            'element_details': element_impacts,
            'potentially_impacted_files': list(impacted_files),
            'impact_summary': f"Changes to {file_path} may impact {len(impacted_files)} other files.",
        }
