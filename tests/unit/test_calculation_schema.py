import pytest

from pydantic import ValidationError

from app.schemas.calculation import CalculationCreate, CalculationType


def test_calculation_create_valid_add():
    obj = CalculationCreate(a=1, b=2, type=CalculationType.ADD)
    assert obj.a == 1
    assert obj.type == CalculationType.ADD


def test_calculation_create_divide_by_zero_invalid():
    with pytest.raises(ValidationError):
        CalculationCreate(a=1, b=0, type=CalculationType.DIV)


def test_calculation_create_invalid_type_string():
    # Only needed if you use string type schema version
    from app.schemas.calculation import CalculationCreate as StringCalcCreate

    with pytest.raises(ValidationError):
        StringCalcCreate(a=1, b=2, type="power")
