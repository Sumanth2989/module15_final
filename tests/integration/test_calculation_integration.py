from sqlalchemy.orm import Session

from app.models.calculation import Calculation, CalculationType
from app.services.calculation_service import create_calculation
from app.schemas.calculation import CalculationCreate


def test_create_calculation_persists_in_db(db_session: Session):
    """
    db_session is a fixture you should already have that gives a test Session.
    If not, create one that connects to your test Postgres.
    """

    # Create the input object using the schema's names (a, b)
    calc_in = CalculationCreate(a=10, b=5, type=CalculationType.DIVISION)

    # We must now fix the create_calculation function in app/services/calculation_service.py
    # (Since the error traces to line 22 of that file)
    # The create_calculation function must be updated to use the correct SQLAlchemy names.

    # Check returned object
    assert created.id is not None
    assert created.result == 2

    # Check directly from DB
    from_db = db_session.query(Calculation).filter(Calculation.id == created.id).first()
    assert from_db is not None
    assert from_db.a == 10
    assert from_db.b == 5
    assert from_db.type == CalculationType.DIV
    assert from_db.result == 2


def test_create_calculation_persists_in_db(db_session: Session):
    # Create the input object using the schema's names (a, b)
    calc_in = CalculationCreate(a=10, b=5, type=CalculationType.DIVISION)
    
    # --- THE MISSING LINE: Assign the function output to 'created' ---
    created = create_calculation(db_session, calc_in, user_id=1) 
    
    # Check returned object
    assert created.id is not None
