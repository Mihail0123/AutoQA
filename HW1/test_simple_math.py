import pytest
from HW1.simple_math import SimpleMath

@pytest.fixture
def math_obj():
    return SimpleMath()

def test_square_positive(math_obj):
    assert math_obj.square(2) == 4

def test_square_zero(math_obj):
    assert math_obj.square(0) == 0

def test_square_negative(math_obj):
    assert math_obj.square(-3) == 9

def test_cube_positive(math_obj):
    assert math_obj.cube(3) == 27

def test_cube_zero(math_obj):
    assert math_obj.cube(0) == 0

def test_cube_negative(math_obj):
    assert math_obj.cube(-3) == -27
