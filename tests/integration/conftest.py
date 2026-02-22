"""Integration test fixtures: mock database with in-memory SQLite for API tests."""

import pytest
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.main import app
from app.crud.database import get_session


@pytest.fixture
def test_db_session():
    """Create an in-memory SQLite database for integration tests."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def test_client(test_db_session: Session):
    """Override FastAPI app's get_session dependency with test DB session."""
    def override_get_session():
        yield test_db_session
    
    app.dependency_overrides[get_session] = override_get_session
    
    # Import TestClient after dependency override
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    yield client
    
    # Clean up
    app.dependency_overrides.clear()
