# app/routers/users.py
from fastapi import APIRouter, Depends, Form, Response, status, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter(
    prefix="",
    tags=["users"],
)

# Setup templates
templates = Jinja2Templates(directory="app/templates")


# -----------------------------
# Register Route (HTML Form)
# -----------------------------
@router.get("/register")
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
def register(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    # Check if email already exists
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Email already registered"}
        )

    # Create new user
    user = User(
        email=email,
        password=hash_password(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Set cookie for session
    response.set_cookie(key="user_id", value=str(user.user_id))

    # Redirect to login page after successful registration (E2E expects this)
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


# -----------------------------
# Login Route (HTML Form)
# -----------------------------
@router.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login(
    request: Request,
    response: Response,
    email: str = Form(None),
    username: str = Form(None),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Accept either 'email' or 'username' form field name
    login_email = email or username
    user = db.query(User).filter(User.email == login_email).first()
    stored_password = getattr(user, 'password', None) if user else None
    if not user or not verify_password(password, stored_password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid email or password"}
        )

    # Create an access token and set it as a cookie so `get_current_user` can find it
    token = create_access_token({"sub": getattr(user, 'id', getattr(user, 'user_id', None))})
    redirect = RedirectResponse(url="/calculations", status_code=status.HTTP_303_SEE_OTHER)
    # Set the HTTP-only cookie used by browser flows
    redirect.set_cookie(key="access_token", value=token, httponly=True)
    return redirect


# -----------------------------
# Logout Route
# -----------------------------
@router.get("/logout")
def logout(response: Response):
    response.delete_cookie("user_id")
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
