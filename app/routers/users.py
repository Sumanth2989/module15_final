# app/routers/users.py
from fastapi import APIRouter, Depends, Form, Response, status, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

# -----------------------------
# Register Route (HTML Form)
# -----------------------------
@router.get("/register")
def register_form(request: Request):
    # Return rendered template for browsers, or a marker dict for API clients
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return templates.TemplateResponse("register.html", {"request": request})
    return {"template": "register.html"}


@router.post("/register")
async def register(request: Request, response: Response, db: Session = Depends(get_db)):
    # Support both JSON (API tests) and form data (if posted here)
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = await request.json()
        email = payload.get("email")
        password = payload.get("password")
    else:
        form = await request.form()
        email = form.get("email")
        password = form.get("password")

    # Validate
    if not email or not password:
        return JSONResponse({"detail": "Missing email or password"}, status_code=422)

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        # For API requests return 400, for form return template
        if "application/json" in content_type:
            return JSONResponse({"detail": "Email already registered"}, status_code=400)
        return {"template": "register.html", "error": "Email already registered"}

    user = User(email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)

    if "application/json" in content_type:
        return JSONResponse({"id": getattr(user, 'id', None), "email": user.email}, status_code=201)

    # For browser flows redirect to login (do not auto-login here)
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


# -----------------------------
# Login Route (HTML Form)
# -----------------------------
@router.get("/login")
def login_form(request: Request):
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return templates.TemplateResponse("login.html", {"request": request})
    return {"template": "login.html"}


@router.post("/login")
async def login(request: Request, response: Response, db: Session = Depends(get_db)):
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = await request.json()
        email = payload.get("email")
        password = payload.get("password")
    else:
        form = await request.form()
        # Some templates use 'username' as the email field name
        email = form.get("email") or form.get("username")
        password = form.get("password")

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, getattr(user, 'password', getattr(user, 'hashed_password', None))):
        if "application/json" in content_type:
            return JSONResponse({"detail": "Invalid email or password"}, status_code=401)
        return {"template": "login.html", "error": "Invalid email or password"}

    if "application/json" in content_type:
        return JSONResponse({"id": getattr(user, 'id', None), "email": user.email}, status_code=200)

    # For browser flows: create access token, set as HTTP-only cookie, and redirect to /calculations
    token = create_access_token({"sub": getattr(user, 'id', getattr(user, 'user_id', None))})
    redirect = RedirectResponse(url="/calculations", status_code=status.HTTP_303_SEE_OTHER)
    redirect.set_cookie(key="access_token", value=token, httponly=True)
    return redirect


# -----------------------------
# Logout Route
# -----------------------------
@router.get("/logout")
def logout(response: Response):
    response.delete_cookie("user_id")
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
