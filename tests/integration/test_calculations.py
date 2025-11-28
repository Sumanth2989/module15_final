from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_calculation_bread_flow():
    # Create
    create_payload = {"a": 10, "b": 5, "type": "add"}
    r = client.post("/calculations/", json=create_payload)
    assert r.status_code == 201
    calc = r.json()
    calc_id = calc["id"]

    # Read
    r2 = client.get(f"/calculations/{calc_id}")
    assert r2.status_code == 200

    # Browse
    r3 = client.get("/calculations/")
    assert r3.status_code == 200
    assert any(c["id"] == calc_id for c in r3.json())

    # Update
    update_payload = {"a": 20, "b": 2, "type": "multiply"}
    r4 = client.put(f"/calculations/{calc_id}", json=update_payload)
    assert r4.status_code == 200

    # Delete
    r5 = client.delete(f"/calculations/{calc_id}")
    assert r5.status_code == 204

    # Confirm Gone
    r6 = client.get(f"/calculations/{calc_id}")
    assert r6.status_code == 404

def test_invalid_operation_type():
    bad_payload = {"a": 10, "b": 5, "type": "weird"}
    r = client.post("/calculations/", json=bad_payload)
    assert r.status_code in (400, 422)
