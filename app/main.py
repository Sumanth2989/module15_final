# app/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.db import engine, SessionLocal
from app.models.base_class import Base
from app.routers.users import router as users_api_router
from app.routers.auth import router as auth_router
from app.routers.calculations import router as calculations_router
from app.routers.reports import router as reports_router
from app.models.user import User
from app.auth import hash_password
from sqlalchemy.orm import Session

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
    """Create a default test user used by E2E tests if it doesn't exist."""
    db: Session = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "testuser@example.com").first()
        if not existing:
            user = User(
                email="testuser@example.com",
                hashed_password=hash_password("password123"),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
    finally:
        db.close()


# -----------------------------
# UI routes for auth pages
# -----------------------------
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """
    Render the login page used by Playwright E2E tests.
    Expects an input with name="username" and name="password".
    """
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    """
    Render the register page used by Playwright E2E tests.
    Expects an input with name="email" and name="password".
    """
    return templates.TemplateResponse("register.html", {"request": request})


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
