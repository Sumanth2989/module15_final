from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db import Base, engine
from app.routers.users import router as users_router
from app.routers.calculations import router as calculations_router
from app.routers.auth import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

# serve static frontend files
app.mount("/static", StaticFiles(directory="static"), name="static")

# include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(calculations_router)


@app.get("/")
def read_root():
    return {"message": "Module 13. JWT auth with frontend and Playwright"}
