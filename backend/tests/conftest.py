import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.dependencies import get_current_user
from app.main import app
from app.models.user import User


@pytest.fixture()
def session_factory():
    """Makes database sessions on a brand-new, empty in-memory database."""
    engine = create_engine(
        "sqlite://",  # in-memory database
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # keep one connection so the memory DB survives
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture()
def raw_client(session_factory):
    """A client that is NOT signed in. Used to test the login rules themselves."""

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    # During tests, use our temporary database instead of the real one.
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def client(raw_client):
    """A client that is already signed in as a staff user. Most tests use this one."""
    app.dependency_overrides[get_current_user] = lambda: User(id=1, username="test-staff")
    return raw_client