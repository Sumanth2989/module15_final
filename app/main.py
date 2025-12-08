from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db import Base, engine
from app.routers.users import router as users_router
from app.routers.auth import router as auth_router
from app.routers.calculations import router as calculations_router

# Create the database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 1. Mount Static Files
# We changed directory="static" to "app/static" so it finds the folder inside 'app'
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 2. Include Routers
# I removed the duplicates so everything is included exactly once
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(calculations_router)

@app.get("/")
def read_root():
    return {"message": "Module 14: BREAD Functionality Ready"}