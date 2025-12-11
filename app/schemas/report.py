from pydantic import BaseModel
from typing import Dict, Any, List, Optional


class RecentCalc(BaseModel):
    id: int
    a: float
    b: float
    operation: str
    result: float
    created_at: Optional[str]


class ReportOut(BaseModel):
    total_count: int
    average_result: Optional[float]
    average_a: Optional[float]
    average_b: Optional[float]
    op_counts: Dict[str, int]
    recent: List[RecentCalc]

    class Config:
        orm_mode = True
