from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, Float, Enum

from app.db import Base


class CalculationType(str, PyEnum):
    ADD = "add"
    SUB = "sub"
    MUL = "multiply"
    DIV = "divide"


class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True, index=True)
    a = Column(Float, nullable=False)
    b = Column(Float, nullable=False)
    type = Column(Enum(CalculationType, name="calculation_type"), nullable=False)
    result = Column(Float, nullable=True)
