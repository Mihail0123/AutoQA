from calculator import Calculator

import pytest

@pytest.fixture
def calculator():
    return Calculator()

def test_sum_positive_numbers(calculator):
    assert calculator.sum(4, 5) == 9

def test_sum_negative_numbers(calculator):
    assert calculator.sum(-6, -10) == -16

def test_sum_positive_and_negative(calculator):
    assert calculator.sum(-6, 6) == 0

def test_sum_floats(calculator):
    res = calculator.sum(5.6, 4.3)
    assert round(res, 1) == 9.9

def test_sum_with_zero(calculator):
    assert calculator.sum(10, 0) == 10

def test_division(calculator):
    assert calculator.div(10, 2) == 5

def test_division_by_zero(calculator):
    with pytest.raises(ArithmeticError, match="На ноль делить нельзя"):
        calculator.div(10, 0)

def test_avg_empty_list(calculator):
    assert calculator.avg([]) == 0

def test_avg_list(calculator):
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 5]
    assert calculator.avg(numbers) == 5