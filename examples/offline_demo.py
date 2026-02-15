#!/usr/bin/env python3
"""
Simple offline demo of the code parser without requiring network access.
"""

from pathlib import Path
from codebase_intelligence.parsers.code_parser import CodeParser


def main():
    print("=" * 70)
    print("Codebase Intelligence Analyzer - Parser Demo (Offline)")
    print("=" * 70)
    print()
    
    # Create parser
    parser = CodeParser()
    
    # Demo 1: Parse a Python file
    print("Demo 1: Parsing Python Code")
    print("-" * 70)
    
    python_code = '''
def calculate_fibonacci(n):
    """
    Calculate the nth Fibonacci number.
    
    Args:
        n: The position in the Fibonacci sequence
        
    Returns:
        The nth Fibonacci number
    """
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)


class MathOperations:
    """A class for various mathematical operations."""
    
    def __init__(self):
        self.result = 0
    
    def add(self, a, b):
        """Add two numbers."""
        self.result = a + b
        return self.result
    
    def multiply(self, a, b):
        """Multiply two numbers."""
        self.result = a * b
        return self.result
'''
    
    # Write to temporary file
    temp_file = Path('/tmp/demo_math.py')
    temp_file.write_text(python_code)
    
    # Parse the file
    result = parser.parse_file(temp_file)
    
    if result:
        print(f"✓ Successfully parsed: {result['file_path']}")
        print(f"  Language: {result['language']}")
        print(f"  Elements found: {len(result['elements'])}")
        print()
        
        for i, elem in enumerate(result['elements'], 1):
            print(f"{i}. {elem['type']}: {elem['name']}")
            print(f"   Lines: {elem['start_line']}-{elem['end_line']}")
            if elem.get('docstring'):
                # Show first line of docstring
                first_line = elem['docstring'].split('\n')[0][:60]
                print(f"   Doc: {first_line}...")
            print()
    
    # Demo 2: Parse JavaScript code
    print("=" * 70)
    print("Demo 2: Parsing JavaScript Code")
    print("-" * 70)
    
    js_code = '''
/**
 * Calculate the sum of an array of numbers
 * @param {Array<number>} numbers - Array of numbers
 * @returns {number} The sum
 */
function calculateSum(numbers) {
    return numbers.reduce((sum, num) => sum + num, 0);
}

class Calculator {
    constructor() {
        this.memory = 0;
    }
    
    add(a, b) {
        const result = a + b;
        this.memory = result;
        return result;
    }
    
    getMemory() {
        return this.memory;
    }
}
'''
    
    temp_js = Path('/tmp/demo_calc.js')
    temp_js.write_text(js_code)
    
    result = parser.parse_file(temp_js)
    
    if result:
        print(f"✓ Successfully parsed: {result['file_path']}")
        print(f"  Language: {result['language']}")
        print(f"  Elements found: {len(result['elements'])}")
        print()
        
        for i, elem in enumerate(result['elements'], 1):
            print(f"{i}. {elem['type']}: {elem['name']}")
            print(f"   Lines: {elem['start_line']}-{elem['end_line']}")
            print()
    
    # Demo 3: Parse the actual project source
    print("=" * 70)
    print("Demo 3: Parsing Project Source Code")
    print("-" * 70)
    
    project_files = [
        'src/codebase_intelligence/parsers/code_parser.py',
        'src/codebase_intelligence/indexer/code_indexer.py',
    ]
    
    for file_path in project_files:
        full_path = Path(file_path)
        if full_path.exists():
            result = parser.parse_file(full_path)
            if result:
                print(f"\n✓ {file_path}")
                print(f"  Elements: {len(result['elements'])}")
                
                # Show first few elements
                for elem in result['elements'][:3]:
                    print(f"    • {elem['type']}: {elem['name']} (line {elem['start_line']})")
    
    print()
    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print()
    print("The parser successfully extracted code structure from multiple languages.")
    print("With network access, you can also use the full indexing and query features:")
    print("  • codebase-analyze index <path>   - Index your codebase")
    print("  • codebase-analyze query <question> - Ask questions about your code")
    print("  • codebase-analyze trace <element>  - Trace dependencies")


if __name__ == "__main__":
    main()
