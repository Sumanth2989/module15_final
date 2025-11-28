from sqlalchemy.orm import Session

from app.models.calculation import Calculation, CalculationType
from app.services.calculation_service import create_calculation
from app.schemas.calculation import CalculationCreate


def test_create_calculation_persists_in_db(db_session: Session):
    """
    db_session is a fixture you should already have that gives a test Session.
    If not, create one that connects to your test Postgres.
    """

    calc_in = CalculationCreate(a=10, b=5, type=CalculationType.DIV)
    created = create_calculation(db_session, calc_in, user_id=None)

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


def test_create_calculation_invalid_type_raises(db_session: Session):
    from app.schemas.calculation import CalculationCreate as StringCalcCreate

    # If you use string schema version. You can also test the factory error directly instead.
    # This should raise ValidationError before it hits db
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        StringCalcCreate(a=1, b=2, type="invalid")
