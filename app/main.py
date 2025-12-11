# app/main.py
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from sqlalchemy.orm import Session

from app.db import engine, SessionLocal
from app.models.base_class import Base
from app.routers.users import router as users_api_router
from app.routers.auth import router as auth_router
from app.routers.calculations import router as calculations_router
from app.routers.reports import router as reports_router
from app.models.user import User
from app.auth import hash_password, authenticate_user, create_access_token

# -----------------------------
# Create the database tables automatically
# -----------------------------
Base.metadata.create_all(bind=engine)

# -----------------------------
# Initialize FastAPI app
# -----------------------------
app = FastAPI()

# -----------------------------
# Mount Static Files
# -----------------------------
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# -----------------------------
# Setup Templates
# -----------------------------
templates = Jinja2Templates(directory="app/templates")

# -----------------------------
# Include Routers
# -----------------------------
app.include_router(auth_router)
app.include_router(users_api_router)
app.include_router(calculations_router)
app.include_router(reports_router)


@app.on_event("startup")
def seed_default_user():
    """
    Create or update the default test user for E2E tests.

    IMPORTANT: Always reset the password hash to match the current hashing
    algorithm, so login with password123 always works.
    """
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "testuser@example.com").first()
        if not user:
            user = User(
                email="testuser@example.com",
                hashed_password=hash_password("password123"),
            )
            db.add(user)
        else:
            # Force-update the password hash so it always matches current hasher
            user.hashed_password = hash_password("password123")
        db.commit()
    finally:
        db.close()


# -----------------------------
# Auth UI routes for E2E tests
# -----------------------------
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """
    Render the login page for browser flows.
    """
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """
    Handle login form submit and redirect to /calculations on success.

    Also sets an `access_token` cookie so browser requests to /calculations
    and /calculations/report are authenticated.
    """
    db: Session = SessionLocal()
    try:
        user = authenticate_user(db, username=username, password=password)
    finally:
        db.close()

    if not user:
        # Stay on login with error if credentials invalid
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid email or password"},
            status_code=400,
        )

    # Create JWT and store it in a cookie
    token = create_access_token({"sub": user.email})
    response = RedirectResponse(url="/calculations", status_code=303)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        samesite="lax",
    )
    return response


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    """
    Render the register page.
    """
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def register_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    """
    Handle register form submit and redirect to /login on success.
    """
    db: Session = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return templates.TemplateResponse(
                "register.html",
                {"request": request, "error": "Email already registered"},
                status_code=400,
            )

        user = User(
            email=email,
            hashed_password=hash_password(password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    finally:
        db.close()

    return RedirectResponse(url="/login", status_code=303)


# (Optional root-level /report – not used by tests but harmless)
@app.get("/report", response_class=HTMLResponse)
def report_page_root(request: Request):
    dummy_report = {
        "total_count": 0,
        "average_result": None,
        "average_a": None,
        "average_b": None,
        "op_counts": {},
        "recent": [],
    }
    return templates.TemplateResponse(
        "calculations/report.html",
        {"request": request, "report": dummy_report},
    )


# -----------------------------
# Root Route
# -----------------------------
@app.get("/")
def read_root(request: Request):
    """
    Home page
    """
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "message": "Module 14: BREAD Functionality Ready"},
    )
