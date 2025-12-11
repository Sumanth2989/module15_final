import sys
from pathlib import Path

import pytest

# Ensure project root is on sys.path so "import app" works in tests
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


@pytest.fixture
def db_session():
    """
    Simple database session fixture for integration tests.
    Uses the same engine and SessionLocal as the app.
    """
    from app.db import Base, engine, SessionLocal

    # Ensure a clean schema for tests: drop any existing tables then recreate
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
