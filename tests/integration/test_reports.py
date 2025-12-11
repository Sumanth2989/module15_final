from fastapi.testclient import TestClient
from app.main import app
from app.models.calculation import Calculation
from app.auth import hash_password
from app.models.user import User
from app.db import SessionLocal


def test_report_route_json():
    """Test report route exists and returns JSON when Accept: application/json."""
    client = TestClient(app)
    db = SessionLocal()
    
    try:
        # seed a user with hashed password
        u = User(email="reporter2@example.com", password=hash_password("password123"))
        db.add(u)
        db.commit()
        db.refresh(u)

        db.add(Calculation(user_id=u.user_id, a=2, b=2, type="add", result=4))
        db.commit()

        # Hit the report endpoint with Bearer token (use JWT)
        from app.auth import create_access_token
        token = create_access_token({"sub": u.id})
        headers = {"Authorization": f"Bearer {token}", "accept": "application/json"}
        resp = client.get("/calculations/report", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_count" in data
        assert "recent" in data
    finally:
        db.close()
