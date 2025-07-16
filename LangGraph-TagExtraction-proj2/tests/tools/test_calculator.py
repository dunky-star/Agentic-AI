# test_calculator.py

import pytest

from code.tools.calculator import add, multiply, divide

def test_add_positive_numbers():
    result = add(2, 3)
    assert result == 5

def test_add_negative_numbers():
    result = add(-1, -1)
    assert result == -2

def test_multiply_basic():
    result = multiply(4, 3)
    assert result == 12

def test_divide_basic():
    result = divide(10, 2)
    assert result == 5.0

def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)