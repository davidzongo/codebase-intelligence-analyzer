"""
Code parser using Tree-sitter for multiple programming languages.
Extracts functions, classes, imports, and other code elements.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import tree_sitter_languages


class CodeParser:
    """Parse source code files and extract structured information."""
    
    # Supported language extensions
    LANGUAGE_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.go': 'go',
        '.rs': 'rust',
        '.cpp': 'cpp',
        '.c': 'c',
        '.rb': 'ruby',
        '.php': 'php',
    }
    
    def __init__(self):
        """Initialize the parser with tree-sitter languages."""
        self.parsers = {}
        
    def get_parser(self, language: str):
        """Get or create a parser for the given language."""
        if language not in self.parsers:
            try:
                self.parsers[language] = tree_sitter_languages.get_parser(language)
            except Exception as e:
                raise ValueError(f"Unsupported language: {language}") from e
        return self.parsers[language]
    
    def detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language from file extension."""
        return self.LANGUAGE_MAP.get(file_path.suffix.lower())
    
    def parse_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse a source code file and extract its structure.
        
        Returns:
            Dictionary containing file metadata and parsed elements.
        """
        try:
            language = self.detect_language(file_path)
            if not language:
                return None
                
            with open(file_path, 'rb') as f:
                code_bytes = f.read()
                
            parser = self.get_parser(language)
            tree = parser.parse(code_bytes)
            
            # Extract code elements based on language
            elements = self._extract_elements(tree.root_node, code_bytes, language)
            
            return {
                'file_path': str(file_path),
                'language': language,
                'elements': elements,
                'content': code_bytes.decode('utf-8', errors='ignore')
            }
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None
    
    def _extract_elements(self, node, code_bytes: bytes, language: str) -> List[Dict[str, Any]]:
        """Extract code elements (functions, classes, etc.) from the AST."""
        elements = []
        
        # Element types to extract based on language
        target_types = {
            'python': ['function_definition', 'class_definition', 'import_statement', 
                      'import_from_statement'],
            'javascript': ['function_declaration', 'class_declaration', 'import_statement',
                          'arrow_function', 'method_definition'],
            'typescript': ['function_declaration', 'class_declaration', 'import_statement',
                          'arrow_function', 'method_definition', 'interface_declaration'],
            'java': ['class_declaration', 'method_declaration', 'import_declaration',
                    'interface_declaration'],
            'go': ['function_declaration', 'method_declaration', 'import_declaration',
                  'type_declaration'],
            'rust': ['function_item', 'impl_item', 'struct_item', 'trait_item'],
            'cpp': ['function_definition', 'class_specifier', 'struct_specifier'],
            'c': ['function_definition', 'struct_specifier'],
            'ruby': ['method', 'class', 'module'],
            'php': ['function_definition', 'class_declaration', 'method_declaration'],
        }
        
        types_to_find = target_types.get(language, [])
        
        def traverse(node):
            """Recursively traverse the AST."""
            if node.type in types_to_find:
                element = self._extract_element_info(node, code_bytes, language)
                if element:
                    elements.append(element)
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
        return elements
    
    def _extract_element_info(self, node, code_bytes: bytes, language: str) -> Dict[str, Any]:
        """Extract detailed information about a code element."""
        start_line = node.start_point[0] + 1
        end_line = node.end_point[0] + 1
        
        # Get element name
        name = self._get_element_name(node, code_bytes)
        
        # Get element text
        element_text = code_bytes[node.start_byte:node.end_byte].decode('utf-8', errors='ignore')
        
        # Get docstring/comments if available
        docstring = self._extract_docstring(node, code_bytes, language)
        
        return {
            'type': node.type,
            'name': name,
            'start_line': start_line,
            'end_line': end_line,
            'content': element_text,
            'docstring': docstring,
        }
    
    def _get_element_name(self, node, code_bytes: bytes) -> str:
        """Extract the name of a code element."""
        # Look for name/identifier nodes
        for child in node.children:
            if child.type in ['identifier', 'name', 'type_identifier']:
                return code_bytes[child.start_byte:child.end_byte].decode('utf-8', errors='ignore')
        return "anonymous"
    
    def _extract_docstring(self, node, code_bytes: bytes, language: str) -> Optional[str]:
        """Extract docstring or documentation comment for an element."""
        if language == 'python':
            # Look for string literal as first child in function/class body
            for child in node.children:
                if child.type == 'block':
                    for stmt in child.children:
                        if stmt.type == 'expression_statement':
                            for expr in stmt.children:
                                if expr.type == 'string':
                                    return code_bytes[expr.start_byte:expr.end_byte].decode(
                                        'utf-8', errors='ignore'
                                    ).strip('"\'')
        return None
