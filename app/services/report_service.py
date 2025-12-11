from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.calculation import Calculation


def generate_report(db: Session, user_id: int, limit: int = 5) -> Dict[str, Any]:
    """Generate a report for a user's calculations.

    Returns a dict with:
      - total_count: int
      - average_result: float | None
      - average_a: float | None
      - average_b: float | None
      - op_counts: dict mapping operation -> count
      - recent: list of recent calculations (dicts)
    """
    # Total count
    total = db.query(func.count(Calculation.id)).filter(Calculation.user_id == user_id).scalar() or 0

    # Average result
    avg_result = db.query(func.avg(Calculation.result)).filter(Calculation.user_id == user_id).scalar()
    average_result = float(avg_result) if avg_result is not None else None

    # Average operands
    avg_a = db.query(func.avg(Calculation.a)).filter(Calculation.user_id == user_id).scalar()
    average_a = float(avg_a) if avg_a is not None else None

    avg_b = db.query(func.avg(Calculation.b)).filter(Calculation.user_id == user_id).scalar()
    average_b = float(avg_b) if avg_b is not None else None

    # Counts per operation
    rows = (
        db.query(Calculation.type, func.count(Calculation.id))
        .filter(Calculation.user_id == user_id)
        .group_by(Calculation.type)
        .all()
    )
    op_counts = {r[0]: r[1] for r in rows}

    # Recent calculations
    recent_rows = (
        db.query(Calculation)
        .filter(Calculation.user_id == user_id)
        .order_by(Calculation.created_at.desc())
        .limit(limit)
        .all()
    )

    recent = [
        {
            "id": c.id,
            "a": c.a,
            "b": c.b,
            "operation": c.operation,
            "result": c.result,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in recent_rows
    ]

    return {
        "total_count": int(total),
        "average_result": average_result,
        "average_a": average_a,
        "average_b": average_b,
        "op_counts": op_counts,
        "recent": recent,
    }
