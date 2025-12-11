# app/routers/calculations.py
from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.models.calculation import Calculation  # SQLAlchemy model
from app.models.user import User
from app.schemas.calculation import CalculationOut, CalculationType  # Pydantic schema for response
from app.dependencies import get_current_user
from app.services.report_service import generate_report
from app.schemas.report import ReportOut

router = APIRouter(
    prefix="/calculations",
    tags=["calculations"],
)

templates = Jinja2Templates(directory="app/templates")

# -----------------------------
# 1. List all calculations for the current user
# -----------------------------
@router.get("", response_model=List[CalculationOut])
def list_calculations(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return either HTML page (for browser) or JSON list (for API clients)."""
    tmpl = Jinja2Templates(directory="app/templates")

    calculations = (
        db.query(Calculation)
        .filter(Calculation.user_id == current_user.user_id)
        .order_by(Calculation.created_at.desc())
        .all()
    )

    accept = request.headers.get("accept", "")
    # If browser requested HTML, render template
    if "text/html" in accept:
        return tmpl.TemplateResponse(
            "calculations/list.html",
            {
                "request": request,
                "calculations": calculations,
                "current_user": current_user,
            },
        )

    # Otherwise return JSON-serializable data for API clients
    return [CalculationOut.from_orm(c).dict() for c in calculations]


@router.get("/add")
def add_calculation_form(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """Render the Add Calculation HTML form for browser flows."""
    tmpl = Jinja2Templates(directory="app/templates")
    return tmpl.TemplateResponse(
        "calculations/add.html",
        {"request": request, "current_user": current_user},
    )


@router.get("/search")
def search_calculations_get(
    request: Request,
    search_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Render the search page or show results when ?search_id=... is provided."""
    tmpl = Jinja2Templates(directory="app/templates")
    calculations: list[Calculation] = []
    if search_id:
        calculations = (
            db.query(Calculation)
            .filter(
                Calculation.id == search_id,
                Calculation.user_id == current_user.user_id,
            )
            .order_by(Calculation.created_at.desc())
            .all()
        )
    return tmpl.TemplateResponse(
        "calculations/list.html",
        {"request": request, "calculations": calculations, "current_user": current_user},
    )


@router.post("/search")
async def search_calculations_post(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Accept the form submission from the search box and render results."""
    form = await request.form()
    raw_search_id = form.get("search_id")
    raw_query = form.get("query")

    search_id = None
    if raw_search_id:
        try:
            search_id = int(raw_search_id)
        except Exception:
            search_id = None
    elif raw_query:
        try:
            search_id = int(raw_query)
        except Exception:
            search_id = None

    tmpl = Jinja2Templates(directory="app/templates")
    calculations: list[Calculation] = []
    if search_id is not None:
        calculations = (
            db.query(Calculation)
            .filter(
                Calculation.id == search_id,
                Calculation.user_id == current_user.user_id,
            )
            .order_by(Calculation.created_at.desc())
            .all()
        )
    elif raw_query:
        q = raw_query.strip()
        calculations_query = db.query(Calculation).filter(
            Calculation.user_id == current_user.user_id
        )
        numeric_val = None
        try:
            numeric_val = float(q)
        except Exception:
            numeric_val = None

        if numeric_val is not None:
            calculations = (
                calculations_query.filter(Calculation.result == numeric_val)
                .order_by(Calculation.created_at.desc())
                .all()
            )
        else:
            calculations = (
                calculations_query.filter(Calculation.type.ilike(f"%{q}%"))
                .order_by(Calculation.created_at.desc())
                .all()
            )

    return tmpl.TemplateResponse(
        "calculations/list.html",
        {"request": request, "calculations": calculations, "current_user": current_user},
    )


# -----------------------------
# /calculations/report
# -----------------------------
@router.get("/report")
def report_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return HTML report for browsers or JSON for API clients.

    - E2E Playwright (browser) hits this with Accept including "text/html".
    - Integration test hits this and calls response.json() to get ReportOut.
    """
    user_id = getattr(current_user, "id", getattr(current_user, "user_id", None))
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    data = generate_report(db, user_id=user_id)
    accept = request.headers.get("accept", "")

    if "text/html" in accept:
        return templates.TemplateResponse(
            "calculations/report.html",
            {"request": request, "report": data, "current_user": current_user},
        )

    # For API clients return JSON schema-compatible structure
    return ReportOut(**data)


# -----------------------------
# 2. View a single calculation
# -----------------------------
@router.get("/{calc_id}", response_model=CalculationOut)
def view_calculation(
    request: Request,
    calc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    calc = (
        db.query(Calculation)
        .filter(
            Calculation.id == calc_id,
            Calculation.user_id == current_user.user_id,
        )
        .first()
    )
    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")

    tmpl = Jinja2Templates(directory="app/templates")
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return tmpl.TemplateResponse(
            "calculations/view.html",
            {"request": request, "calc": calc, "current_user": current_user},
        )

    return CalculationOut.from_orm(calc)


@router.get("/{calc_id}/edit")
def edit_calculation_form(
    request: Request,
    calc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Render the Edit Calculation HTML form for browser flows."""
    calc = (
        db.query(Calculation)
        .filter(
            Calculation.id == calc_id,
            Calculation.user_id == current_user.user_id,
        )
        .first()
    )
    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")

    tmpl = Jinja2Templates(directory="app/templates")
    return tmpl.TemplateResponse(
        "calculations/edit.html",
        {"request": request, "calc": calc, "current_user": current_user},
    )


# -----------------------------
# 3. Add a new calculation
# -----------------------------
@router.post("/add")
def add_calculation(
    operand1: float = Form(...),
    operand2: float = Form(...),
    operation: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Normalize operation to the enum
    try:
        op = CalculationType(operation)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid operation")

    # Perform calculation
    if op == CalculationType.ADD:
        result = operand1 + operand2
    elif op == CalculationType.SUB:
        result = operand1 - operand2
    elif op == CalculationType.MUL:
        result = operand1 * operand2
    elif op in (CalculationType.DIV, CalculationType.DIVISION):
        if operand2 == 0:
            raise HTTPException(status_code=400, detail="Division by zero")
        result = operand1 / operand2
    elif op == CalculationType.POW:
        result = operand1 ** operand2
    elif op == CalculationType.MOD:
        if operand2 == 0:
            raise HTTPException(status_code=400, detail="Modulo by zero")
        result = operand1 % operand2
    else:
        raise HTTPException(status_code=400, detail="Invalid operation")

    # Save to DB
    calc = Calculation(
        user_id=current_user.user_id,
        a=operand1,
        b=operand2,
        type=op.value,
        result=result,
    )
    db.add(calc)
    db.commit()
    db.refresh(calc)

    return RedirectResponse(url="/calculations", status_code=303)


# -----------------------------
# 4. Edit a calculation
# -----------------------------
@router.post("/{calc_id}/edit")
def edit_calculation(
    calc_id: int,
    operand1: float = Form(...),
    operand2: float = Form(...),
    operation: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    calc = (
        db.query(Calculation)
        .filter(
            Calculation.id == calc_id,
            Calculation.user_id == current_user.user_id,
        )
        .first()
    )
    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")
    # Normalize operation to enum
    try:
        op = CalculationType(operation)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid operation")

    # Recalculate result
    if op == CalculationType.ADD:
        result = operand1 + operand2
    elif op == CalculationType.SUB:
        result = operand1 - operand2
    elif op == CalculationType.MUL:
        result = operand1 * operand2
    elif op in (CalculationType.DIV, CalculationType.DIVISION):
        if operand2 == 0:
            raise HTTPException(status_code=400, detail="Division by zero")
        result = operand1 / operand2
    elif op == CalculationType.POW:
        result = operand1 ** operand2
    elif op == CalculationType.MOD:
        if operand2 == 0:
            raise HTTPException(status_code=400, detail="Modulo by zero")
        result = operand1 % operand2
    else:
        raise HTTPException(status-code=400, detail="Invalid operation")

    # Update DB
    calc.a = operand1
    calc.b = operand2
    calc.type = op.value
    calc.result = result
    db.commit()
    db.refresh(calc)

    return RedirectResponse(url=f"/calculations/{calc_id}", status_code=303)


# -----------------------------
# 5. Delete a calculation
# -----------------------------
@router.post("/{calc_id}/delete")
def delete_calculation(
    calc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    calc = (
        db.query(Calculation)
        .filter(
            Calculation.id == calc_id,
            Calculation.user_id == current_user.user_id,
        )
        .first()
    )
    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")

    db.delete(calc)
    db.commit()

    return RedirectResponse(url="/calculations", status_code=303)
