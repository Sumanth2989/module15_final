# /app/schemas/calculation.py
from enum import Enum
from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional
from datetime import datetime


class CalculationType(str, Enum):
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    DIVISION = "div"  # alias
    POW = "pow"
    MOD = "mod"


class CalculationCreate(BaseModel):
    a: float
    b: float
    type: CalculationType

    @root_validator(skip_on_failure=True)
    def check_division_by_zero(cls, values):
        t = values.get("type")
        b = values.get("b")
        if t in (CalculationType.DIV, CalculationType.DIVISION) and b == 0:
            raise ValueError("Division by zero")
        return values


class CalculationUpdate(BaseModel):
    a: Optional[float]
    b: Optional[float]
    type: Optional[CalculationType]


class CalculationOut(BaseModel):
    id: int
    a: float
    b: float
    type: CalculationType
    result: float
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
