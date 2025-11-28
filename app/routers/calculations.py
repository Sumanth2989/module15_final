from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.calculation import Calculation
from app.schemas.calculation import CalculationCreate, CalculationRead
from app.services.calculation_service import perform_calculation

router = APIRouter(
    prefix="/calculations",
    tags=["calculations"],
)


@router.get("/", response_model=list[CalculationRead])
def browse_calculations(db: Session = Depends(get_db)):
    calcs = db.query(Calculation).all()
    return calcs


@router.get("/{calc_id}", response_model=CalculationRead)
def read_calculation(calc_id: int, db: Session = Depends(get_db)):
    calc = db.query(Calculation).get(calc_id)
    if not calc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found",
        )
    return calc


@router.post("/", response_model=CalculationRead, status_code=status.HTTP_201_CREATED)
def add_calculation(calc_in: CalculationCreate, db: Session = Depends(get_db)):
    try:
        result_value = perform_calculation(
            a=calc_in.a,
            b=calc_in.b,
            operation_type=calc_in.type,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    calc = Calculation(
        a=calc_in.a,
        b=calc_in.b,
        type=calc_in.type,
        result=result_value,
    )
    db.add(calc)
    db.commit()
    db.refresh(calc)
    return calc



@router.put("/{calc_id}", response_model=CalculationRead)
def edit_calculation(calc_id: int, calc_in: CalculationCreate, db: Session = Depends(get_db)):
    calc = db.query(Calculation).get(calc_id)
    if not calc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found",
        )

    try:
        result_value = perform_calculation(
            a=calc_in.a,
            b=calc_in.b,
            operation_type=calc_in.type,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    calc.a = calc_in.a
    calc.b = calc_in.b
    calc.type = calc_in.type
    calc.result = result_value

    db.commit()
    db.refresh(calc)
    return calc



@router.delete("/{calc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation(calc_id: int, db: Session = Depends(get_db)):
    calc = db.query(Calculation).get(calc_id)
    if not calc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found",
        )

    db.delete(calc)
    db.commit()
    return
