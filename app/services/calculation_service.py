from sqlalchemy.orm import Session
from app.models.calculation import Calculation
from app.schemas.calculation import CalculationCreate
from app.services.calculation_factory import CalculationFactory
from app.models.calculation import CalculationType as ModelCalcType # Import is required here for the ModelCalcType

# Note: Keeping user_id for future context, though the current function doesn't use it for creation.
def create_calculation(db: Session, calc_in: CalculationCreate, user_id: int | None = None) -> Calculation:
    """
    Create a Calculation row in the database.
    """
    # Use factory to compute result
    strategy = CalculationFactory.get_strategy(calc_in.type)
    result = strategy.calculate(calc_in.a, calc_in.b)

    # Convert schema enum to model enum value for the DB column
    operation_value = calc_in.type.value

    # Fix: Map schema fields (a, b) to model fields (operand1, operand2)
    # Fix: Map the operation type to the model's 'operation' column
    db_obj = Calculation(
        operand1=calc_in.a,  # FIXED: Mapped 'a' to 'operand1'
        operand2=calc_in.b,  # FIXED: Mapped 'b' to 'operand2'
        operation=operation_value, # Mapped to the 'operation' column
        result=result,
        user_id=user_id # Include user_id, assuming your Calculation model has this column
    )
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# Keep the perform_calculation helper function as is, since it's used elsewhere
def perform_calculation(a: float, b: float, operation_type: str) -> float:
    """
    Simple helper used by the /calculations endpoints.
    ... (rest of the function remains unchanged)
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
        raise ValueError(f"Unsupported operation type: {operation_type}")