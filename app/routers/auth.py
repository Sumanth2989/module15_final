from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Form
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.db import get_db
# We import the User model to save new users
from app.models.user import User
# We import tools to hash passwords and create tokens
from app.auth import authenticate_user, create_access_token, get_password_hash

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# --- LOGIN ROUTES ---
@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login(
    request: Request,
    response: Response, 
    username: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    response = RedirectResponse(url="/calculations", status_code=303)
    # Set the cookie so the browser remembers you
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

# --- LOGOUT ROUTE ---
@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response

# --- REGISTER ROUTES (NEW!) ---
@router.get("/register")
def register_page(request: Request):
    # Show the empty register form
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register(
    request: Request,
    email: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    # 1. Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Email already registered"})
    
    # 2. Hash the password (security!)
    hashed_pwd = get_password_hash(password)
    
    # 3. Create and Save the new User
    new_user = User(email=email, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 4. Send them to the login page to sign in
    return RedirectResponse(url="/login", status_code=303)