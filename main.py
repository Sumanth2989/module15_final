from fastapi import FastAPI
from app.routers import users, calculations
app = FastAPI()

app.include_router(users.router)
app.include_router(calculations.router)


@app.get("/")
def read_root():
    return {"message": "Module 12 API is running"}
