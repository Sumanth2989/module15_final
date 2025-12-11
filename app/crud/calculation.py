# app/crud/calculation.py
from sqlalchemy.orm import Session
from app.models.calculation import Calculation
from app.schemas.calculation import CalculationCreate, CalculationUpdate
from typing import List, Optional
from sqlalchemy.exc import NoResultFound

def compute_result(operation: str, a: float, b: float) -> float:
    # Normalize if an Enum member was passed
    if hasattr(operation, 'value'):
        operation = operation.value

    if operation == "add":
        return a + b
    if operation == "sub":
        return a - b
    if operation == "mul":
        return a * b
    if operation == "div":
        if b == 0:
            raise ValueError("Division by zero")
        return a / b
    raise ValueError("Unknown operation")

def create_calculation(db: Session, user_id: int, obj_in: CalculationCreate) -> Calculation:
    # Support both old schema (operation, operand_a, operand_b) and new (type, a, b)
    if hasattr(obj_in, 'operation'):
        op = obj_in.operation
        a = obj_in.operand_a
        b = obj_in.operand_b
    else:
        # pydantic enum -> use .value
        op = getattr(obj_in, 'type', None)
        if hasattr(op, 'value'):
            op = op.value
        a = getattr(obj_in, 'a', None)
        b = getattr(obj_in, 'b', None)

    result = compute_result(op, a, b)
    db_obj = Calculation(
        user_id=user_id,
        operation=op,
        operand_a=a,
        operand_b=b,
        result=result
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_calculation(db: Session, id: int, user_id: int) -> Optional[Calculation]:
    return db.query(Calculation).filter(Calculation.id == id, Calculation.user_id == user_id).first()

def list_calculations(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Calculation]:
    return db.query(Calculation).filter(Calculation.user_id == user_id).offset(skip).limit(limit).all()

def update_calculation(db: Session, id: int, user_id: int, obj_in: CalculationUpdate) -> Optional[Calculation]:
    db_obj = get_calculation(db, id, user_id)
    if not db_obj:
        return None
    if obj_in.operation is not None:
        db_obj.operation = obj_in.operation
    if obj_in.operand_a is not None:
        db_obj.operand_a = obj_in.operand_a
    if obj_in.operand_b is not None:
        db_obj.operand_b = obj_in.operand_b
    # recompute result
    db_obj.result = compute_result(db_obj.operation, db_obj.operand_a, db_obj.operand_b)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_calculation(db: Session, id: int, user_id: int) -> bool:
    db_obj = get_calculation(db, id, user_id)
    if not db_obj:
        return False
    db.delete(db_obj)
    db.commit()
    return True
