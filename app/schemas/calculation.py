from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator


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
        # No division by zero
        if self.type == CalculationType.DIV and self.b == 0:
            raise ValueError("b cannot be zero when type is 'divide'")
        return self


class CalculationRead(BaseModel):
    id: int
    a: float
    b: float
    type: CalculationType
    result: float
    user_id: Optional[int] = None

    class Config:
        from_attributes = True  # Pydantic v2. For v1 use orm_mode = True
