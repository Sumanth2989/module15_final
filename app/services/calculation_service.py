from sqlalchemy.orm import Session
from app.models.calculation import Calculation
from app.schemas.calculation import CalculationCreate, CalculationType

def create_calculation(db: Session, calc_in: CalculationCreate, user_id: int) -> Calculation:
    result = None
    if calc_in.type == CalculationType.ADD:
        result = calc_in.a + calc_in.b
    elif calc_in.type == CalculationType.SUB:
        result = calc_in.a - calc_in.b
    elif calc_in.type == CalculationType.MUL:
        result = calc_in.a * calc_in.b
    elif calc_in.type in (CalculationType.DIV, CalculationType.DIVISION):
        # b is already validated in the schema, but keep a guard here
        if calc_in.b == 0:
            raise ValueError("Division by zero")
        result = calc_in.a / calc_in.b

    # store the enum value (string) in the DB column
    calc = Calculation(
        user_id=user_id,
        type=calc_in.type.value,
        a=calc_in.a,
        b=calc_in.b,
        result=result
    )
    db.add(calc)
    db.commit()
    db.refresh(calc)
    return calc
