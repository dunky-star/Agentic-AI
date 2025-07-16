

def add(a, b):
    """Add two numbers and return the result."""
    return a + b

def multiply(a, b):
    """Multiply two numbers and return the result."""
    return a * b

def divide(a, b):
    """Divide two numbers and return the result. Raises ValueError if division by zero."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b