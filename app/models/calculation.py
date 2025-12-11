# app/models/calculation.py
from enum import Enum
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, synonym
from datetime import datetime
from .base_class import Base  # only from base_class


class CalculationType(Enum):
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    DIVISION = "div"  # alias for tests that use DIVISION
    POW = "pow"
    MOD = "mod"


class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    # store operation in DB column 'operation' as plain string but expose as attribute 'type'
    type = Column("operation", String(length=20), nullable=False)
    # expose attributes a/b but keep DB column names operand_a/operand_b for templates/legacy code
    a = Column("operand_a", Float, nullable=False)
    b = Column("operand_b", Float, nullable=False)
    result = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="calculations")  # ensure User model has calculations relationship
    # Backwards compatibility for templates and existing code that expect operand_a/operand_b/operation
    operand_a = synonym('a')
    operand_b = synonym('b')
    operation = synonym('type')
