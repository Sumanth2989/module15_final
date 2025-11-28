import pytest

from app.schemas.calculation import CalculationType
from app.services.calculation_factory import (
    CalculationFactory,
    AddStrategy,
    SubStrategy,
    MultiplyStrategy,
    DivideStrategy,
)


@pytest.mark.parametrize(
    "calc_type,expected_class",
    [
        (CalculationType.ADD, AddStrategy),
        (CalculationType.SUB, SubStrategy),
        (CalculationType.MUL, MultiplyStrategy),
        (CalculationType.DIV, DivideStrategy),
    ],
)
def test_factory_returns_correct_strategy(calc_type, expected_class):
    strategy = CalculationFactory.get_strategy(calc_type)
    assert isinstance(strategy, expected_class)


def test_divide_strategy_raises_on_zero():
    strategy = DivideStrategy()
    with pytest.raises(ZeroDivisionError):
        strategy.calculate(1, 0)
