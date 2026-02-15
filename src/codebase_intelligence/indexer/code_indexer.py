"""
Codebase indexer that creates and manages vector database of code elements.
Enables semantic search and retrieval of code snippets.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
except ImportError:
    chromadb = None
    SentenceTransformer = None

from ..parsers.code_parser import CodeParser


class CodebaseIndexer:
    """Index and search codebase using vector embeddings."""
    
    def __init__(self, db_path: str = "./chroma_db", collection_name: str = "codebase"):
        """
        Initialize the codebase indexer.
        
        Args:
            db_path: Path to store the vector database
            collection_name: Name of the collection in the database
        """
        if chromadb is None:
            raise ImportError(
                "chromadb and sentence-transformers are required. "
                "Install with: pip install chromadb sentence-transformers"
            )
        
        self.db_path = db_path
        self.collection_name = collection_name
        self.parser = CodeParser()
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Code elements from codebase"}
        )
        
        # Initialize embedding model (using sentence transformers)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def index_codebase(self, codebase_path: Path, file_patterns: Optional[List[str]] = None):
        """
        Index an entire codebase.
        
        Args:
            codebase_path: Root path of the codebase
            file_patterns: Optional list of file patterns to include (e.g., ['**/*.py'])
        """
        codebase_path = Path(codebase_path)
        
        if not codebase_path.exists():
            raise ValueError(f"Codebase path does not exist: {codebase_path}")
        
        print(f"Indexing codebase at: {codebase_path}")
        
        # Find all source files
        source_files = self._find_source_files(codebase_path, file_patterns)
        print(f"Found {len(source_files)} source files")
        
        # Parse and index each file
        indexed_count = 0
        for file_path in source_files:
            if self._index_file(file_path, codebase_path):
                indexed_count += 1
                
        print(f"Successfully indexed {indexed_count} files")
        
        # Store metadata
        self._store_metadata(codebase_path, indexed_count)
        
    def _find_source_files(self, root_path: Path, patterns: Optional[List[str]] = None) -> List[Path]:
        """Find all source code files in the directory."""
        if patterns is None:
            # Default patterns for supported languages
            patterns = ['**/*.py', '**/*.js', '**/*.jsx', '**/*.ts', '**/*.tsx',
                       '**/*.java', '**/*.go', '**/*.rs', '**/*.cpp', '**/*.c',
                       '**/*.rb', '**/*.php']
        
        files = []
        for pattern in patterns:
            files.extend(root_path.glob(pattern))
        
        # Filter out common directories to ignore
        ignore_dirs = {'node_modules', '.git', '__pycache__', 'venv', 'env', 
                      'dist', 'build', '.next', 'target', 'vendor'}
        
        filtered_files = []
        for file in files:
            # Check if any parent directory should be ignored
            if not any(part in ignore_dirs for part in file.parts):
                filtered_files.append(file)
        
        return filtered_files
    
    def _index_file(self, file_path: Path, root_path: Path) -> bool:
        """Parse and index a single file."""
        try:
            parsed = self.parser.parse_file(file_path)
            if not parsed or not parsed['elements']:
                return False
            
            # Get relative path for better display
            try:
                relative_path = file_path.relative_to(root_path)
            except ValueError:
                relative_path = file_path
            
            # Index each code element
            for element in parsed['elements']:
                self._add_element(element, str(relative_path), parsed['language'])
            
            return True
            
        except Exception as e:
            print(f"Error indexing {file_path}: {e}")
            return False
    
    def _add_element(self, element: Dict[str, Any], file_path: str, language: str):
        """Add a code element to the vector database."""
        # Create a searchable text representation
        text_parts = [
            f"File: {file_path}",
            f"Language: {language}",
            f"Type: {element['type']}",
            f"Name: {element['name']}",
        ]
        
        if element.get('docstring'):
            text_parts.append(f"Documentation: {element['docstring']}")
        
        # Add actual code content
        text_parts.append(f"Code:\n{element['content']}")
        
        searchable_text = "\n".join(text_parts)
        
        # Create unique ID for this element
        element_id = f"{file_path}:{element['start_line']}-{element['end_line']}:{element['name']}"
        
        # Generate embedding
        embedding = self.embedding_model.encode(searchable_text).tolist()
        
        # Add to collection
        self.collection.add(
            ids=[element_id],
            embeddings=[embedding],
            documents=[searchable_text],
            metadatas=[{
                'file_path': file_path,
                'language': language,
                'element_type': element['type'],
                'element_name': element['name'],
                'start_line': element['start_line'],
                'end_line': element['end_line'],
                'docstring': element.get('docstring', ''),
            }]
        )
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search the codebase using natural language query.
        
        Args:
            query: Natural language search query
            n_results: Number of results to return
            
        Returns:
            List of matching code elements with metadata
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Search in vector database
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None,
                })
        
        return formatted_results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the indexed codebase."""
        count = self.collection.count()
        
        # Get language distribution
        # Note: ChromaDB doesn't have easy aggregation, so we'll keep it simple
        return {
            'total_elements': count,
            'collection_name': self.collection_name,
            'db_path': self.db_path,
        }
    
    def _store_metadata(self, codebase_path: Path, file_count: int):
        """Store indexing metadata."""
        metadata = {
            'codebase_path': str(codebase_path),
            'indexed_at': datetime.now().isoformat(),
            'file_count': file_count,
        }
        
        metadata_path = Path(self.db_path) / 'metadata.json'
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def clear(self):
        """Clear all indexed data."""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Code elements from codebase"}
        )
