"""Test configuration and fixtures."""

import pytest


@pytest.fixture
def sample_python_code():
    """Sample Python code for testing."""
    return '''
def example_function(x, y):
    """
    An example function that adds two numbers.
    
    Args:
        x: First number
        y: Second number
    
    Returns:
        The sum of x and y
    """
    return x + y


class ExampleClass:
    """An example class."""
    
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        """Return a greeting."""
        return f"Hello, {self.name}!"
'''


@pytest.fixture
def sample_javascript_code():
    """Sample JavaScript code for testing."""
    return '''
function calculateTotal(items) {
    /**
     * Calculate the total price of items
     * @param {Array} items - Array of items with price property
     * @returns {number} Total price
     */
    return items.reduce((sum, item) => sum + item.price, 0);
}

class ShoppingCart {
    constructor() {
        this.items = [];
    }
    
    addItem(item) {
        this.items.push(item);
    }
    
    getTotal() {
        return calculateTotal(this.items);
    }
}
'''
