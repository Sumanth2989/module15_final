from app.services.report_service import generate_report
from app.models.calculation import Calculation


def test_generate_report_empty(db_session):
    # No calculations exist yet
    user_id = 1
    r = generate_report(db_session, user_id=user_id)
    assert r["total_count"] == 0
    assert r["average_result"] is None
    assert r["op_counts"] == {}
    assert r["recent"] == []


def test_generate_report_with_data(db_session):
    # Create some calculations
    user_id = 2
    calcs = [
        Calculation(user_id=user_id, a=1, b=2, type="add", result=3),
        Calculation(user_id=user_id, a=10, b=5, type="sub", result=5),
        Calculation(user_id=user_id, a=2, b=3, type="mul", result=6),
    ]
    for c in calcs:
        db_session.add(c)
    db_session.commit()

    r = generate_report(db_session, user_id=user_id)
    assert r["total_count"] == 3
    assert round(r["average_result"], 5) == round((3 + 5 + 6) / 3, 5)
    # op_counts keys should contain the types
    assert r["op_counts"]["add"] == 1
    assert len(r["recent"]) == 3
