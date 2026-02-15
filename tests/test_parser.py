"""
Tests for the code parser module.
"""

import pytest
from pathlib import Path
from codebase_intelligence.parsers.code_parser import CodeParser


class TestCodeParser:
    """Test cases for CodeParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = CodeParser()
    
    def test_language_detection(self):
        """Test language detection from file extensions."""
        test_cases = [
            (Path("test.py"), "python"),
            (Path("test.js"), "javascript"),
            (Path("test.ts"), "typescript"),
            (Path("test.java"), "java"),
            (Path("test.go"), "go"),
            (Path("test.unknown"), None),
        ]
        
        for file_path, expected_lang in test_cases:
            assert self.parser.detect_language(file_path) == expected_lang
    
    def test_parser_initialization(self):
        """Test that parser can be initialized."""
        assert self.parser is not None
        assert isinstance(self.parser.LANGUAGE_MAP, dict)
    
    def test_get_parser_python(self):
        """Test getting a Python parser."""
        parser = self.parser.get_parser("python")
        assert parser is not None
    
    def test_get_parser_javascript(self):
        """Test getting a JavaScript parser."""
        parser = self.parser.get_parser("javascript")
        assert parser is not None
    
    def test_get_parser_unsupported(self):
        """Test that unsupported language raises error."""
        with pytest.raises(ValueError):
            self.parser.get_parser("unsupported_language_xyz")
    
    def test_parse_simple_python_file(self, tmp_path):
        """Test parsing a simple Python file."""
        # Create a test Python file
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def hello_world():
    '''Say hello'''
    print("Hello, World!")

class MyClass:
    def my_method(self):
        pass
""")
        
        result = self.parser.parse_file(test_file)
        
        assert result is not None
        assert result['language'] == 'python'
        assert result['file_path'] == str(test_file)
        assert len(result['elements']) >= 2  # At least function and class
        
        # Check that function was parsed
        function_found = any(
            elem['name'] == 'hello_world' 
            for elem in result['elements']
        )
        assert function_found
        
        # Check that class was parsed
        class_found = any(
            elem['name'] == 'MyClass' 
            for elem in result['elements']
        )
        assert class_found
    
    def test_parse_nonexistent_file(self, tmp_path):
        """Test parsing a file that doesn't exist."""
        test_file = tmp_path / "nonexistent.py"
        result = self.parser.parse_file(test_file)
        
        assert result is None
    
    def test_parse_unsupported_extension(self, tmp_path):
        """Test parsing a file with unsupported extension."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Some text content")
        
        result = self.parser.parse_file(test_file)
        assert result is None
