from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.models.calculation import Calculation
from app.deps import get_current_user 

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# 1. BROWSE (List all)
@router.get("/calculations")
def list_calculations(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    calculations = db.query(Calculation).filter(Calculation.user_id == user.id).all()
    return templates.TemplateResponse("calculations/list.html", {"request": request, "calculations": calculations})

# --- NEW: SEARCH ROUTE ---
@router.post("/calculations/search")
def search_calculation(search_id: int = Form(...)):
    # Redirect the user to the View page for the ID they typed
    return RedirectResponse(url=f"/calculations/{search_id}", status_code=303)

# --- ADD ROUTES (Specific routes come FIRST) ---

# 2. ADD (Show Form)
@router.get("/calculations/add")
def add_calculation_form(request: Request):
    return templates.TemplateResponse("calculations/add.html", {"request": request})

# 2. ADD (Process Logic)
@router.post("/calculations/add")
def add_calculation(
    request: Request,
    operand1: float = Form(...),
    operand2: float = Form(...),
    operation: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = 0.0
    if operation == "add":
        result = operand1 + operand2
    elif operation == "subtract":
        result = operand1 - operand2
    elif operation == "multiply":
        result = operand1 * operand2
    elif operation == "divide":
        if operand2 == 0:
            return templates.TemplateResponse("calculations/add.html", {"request": request, "error": "Cannot divide by zero"})
        result = operand1 / operand2

    new_calc = Calculation(
        operand1=operand1, 
        operand2=operand2, 
        operation=operation, 
        result=result, 
        user_id=user.id
    )
    db.add(new_calc)
    db.commit()
    
    return RedirectResponse(url="/calculations", status_code=303)

# --- GENERIC ROUTES (Routes with {id} come LAST) ---

# 3. READ (View One)
@router.get("/calculations/{id}")
def view_calculation(id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    calc = db.query(Calculation).filter(Calculation.id == id, Calculation.user_id == user.id).first()
    
    # If not found, go back to list (or you could show an error page)
    if not calc:
        return RedirectResponse(url="/calculations")
        
    return templates.TemplateResponse("calculations/view.html", {"request": request, "calc": calc})

# 4. EDIT (Show Form)
@router.get("/calculations/{id}/edit")
def edit_calculation_form(id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    calc = db.query(Calculation).filter(Calculation.id == id, Calculation.user_id == user.id).first()
    if not calc:
        return RedirectResponse(url="/calculations")
    return templates.TemplateResponse("calculations/edit.html", {"request": request, "calc": calc})

# 4. EDIT (Process Logic)
@router.post("/calculations/{id}/edit")
def update_calculation(
    id: int,
    operand1: float = Form(...),
    operand2: float = Form(...),
    operation: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    calc = db.query(Calculation).filter(Calculation.id == id, Calculation.user_id == user.id).first()
    
    if calc:
        result = 0.0
        if operation == "add": result = operand1 + operand2
        elif operation == "subtract": result = operand1 - operand2
        elif operation == "multiply": result = operand1 * operand2
        elif operation == "divide": 
             if operand2 == 0:
                 return RedirectResponse(url="/calculations", status_code=303)
             result = operand1 / operand2
        
        calc.operand1 = operand1
        calc.operand2 = operand2
        calc.operation = operation
        calc.result = result
        db.commit()
        
    return RedirectResponse(url="/calculations", status_code=303)

# 5. DELETE
@router.post("/calculations/{id}/delete")
def delete_calculation(id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    calc = db.query(Calculation).filter(Calculation.id == id, Calculation.user_id == user.id).first()
    if calc:
        db.delete(calc)
        db.commit()
    return RedirectResponse(url="/calculations", status_code=303)