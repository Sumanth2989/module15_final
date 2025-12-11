from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from typing import Any
from sqlalchemy.orm import Session
from app.dependencies import get_current_user
from app.db import get_db
from app.services.report_service import generate_report
from app.schemas.report import ReportOut

router = APIRouter(prefix="/calculations", tags=["reports"])
templates = Jinja2Templates(directory="app/templates")


# Note: /report route is now in app/routers/calculations.py before /{calc_id}
# to ensure it takes route precedence


@router.get("/history")
def report_history(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user_id = getattr(current_user, "id", getattr(current_user, "user_id", None))
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    data = generate_report(db, user_id=user_id)
    return {"recent": data["recent"]}
