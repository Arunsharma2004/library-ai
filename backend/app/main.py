from fastapi import FastAPI

from app.database import Base, engine
from app.models.book import Book  # noqa: F401  (importing registers the table)

# Create any tables that don't exist yet.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Library Management System")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}