from enum import Enum
from typing import Optional

from pydantic import BaseModel, model_validator


class CalculationType(str, Enum):
    ADD = "add"
    SUB = "sub"
    MUL = "multiply"
    DIV = "divide"


class CalculationBase(BaseModel):
    a: float
    b: float
    type: CalculationType


class CalculationCreate(CalculationBase):
    @model_validator(mode="after")
    def validate_division(self) -> "CalculationCreate":
        # prevent division by zero on create
        if self.type == CalculationType.DIV and self.b == 0:
            raise ValueError("b cannot be zero when type is 'divide'")
        return self


class CalculationUpdate(BaseModel):
    a: Optional[float] = None
    b: Optional[float] = None
    type: Optional[CalculationType] = None

    @model_validator(mode="after")
    def validate_division(self) -> "CalculationUpdate":
        # If update results in a division, ensure b is not zero.
        # Note. We allow partial updates, so only validate when we can determine b and type.
        t = self.type
        b_val = self.b
        if t == CalculationType.DIV and b_val == 0:
            raise ValueError("b cannot be zero when type is 'divide'")
        return self


class CalculationRead(BaseModel):
    id: int
    a: float
    b: float
    type: CalculationType
    result: float
    owner_id: Optional[int] = None

    class Config:
        from_attributes = True
