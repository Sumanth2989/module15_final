from abc import ABC, abstractmethod
from app.schemas.calculation import CalculationType


class CalculationStrategy(ABC):
    @abstractmethod
    def calculate(self, a: float, b: float) -> float:
        raise NotImplementedError


class AddStrategy(CalculationStrategy):
    def calculate(self, a: float, b: float) -> float:
        return a + b


class SubStrategy(CalculationStrategy):
    def calculate(self, a: float, b: float) -> float:
        return a - b


class MultiplyStrategy(CalculationStrategy):
    def calculate(self, a: float, b: float) -> float:
        return a * b


class DivideStrategy(CalculationStrategy):
    def calculate(self, a: float, b: float) -> float:
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return a / b


class CalculationFactory:
    @staticmethod
    def get_strategy(calc_type: CalculationType) -> CalculationStrategy:
        if calc_type == CalculationType.ADD:
            return AddStrategy()
        if calc_type == CalculationType.SUB:
            return SubStrategy()
        if calc_type == CalculationType.MUL:
            return MultiplyStrategy()
        if calc_type == CalculationType.DIV:
            return DivideStrategy()
        raise ValueError(f"Unsupported calculation type: {calc_type}")
