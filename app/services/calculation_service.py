from sqlalchemy.orm import Session

from app.models.calculation import Calculation, CalculationType as ModelCalcType
from app.schemas.calculation import CalculationCreate, CalculationType
from app.services.calculation_factory import CalculationFactory


def create_calculation(db: Session, calc_in: CalculationCreate, user_id: int | None = None) -> Calculation:
    """
    Create a Calculation row in the database.

    user_id is kept in the signature for future use, but the current model
    does not have a user_id column, so it is ignored here.
    """
    # Use factory to compute result
    strategy = CalculationFactory.get_strategy(calc_in.type)
    result = strategy.calculate(calc_in.a, calc_in.b)

    # Convert schema enum to model enum for the DB column
    calc_type_model = ModelCalcType(calc_in.type.value)

    db_obj = Calculation(
        a=calc_in.a,
        b=calc_in.b,
        type=calc_type_model,
        result=result,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
def perform_calculation(a: float, b: float, operation_type: str) -> float:
    """
    Simple helper used by the /calculations endpoints.
    It takes two numbers (a, b) and a string operation_type.
    Supported types: "add", "subtract", "multiply", "divide".
    """
    if operation_type == "add":
        return a + b
    elif operation_type == "subtract":
        return a - b
    elif operation_type == "multiply":
        return a * b
    elif operation_type == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    else:
        # this will be treated as "invalid input" by the router
        raise ValueError(f"Unsupported operation type: {operation_type}")

