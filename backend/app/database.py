"""Database connection setup (SQLAlchemy)."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# SQLite needs this flag because FastAPI may use a connection across threads.
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """All database models will inherit from this class."""


def get_db():
    """Gives each request its own database session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()