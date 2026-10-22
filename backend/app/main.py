from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.database import Base, engine
from app.models.book import Book  # noqa: F401  (importing registers the table)
from app.models.borrow import BorrowRecord  # noqa: F401
from app.models.member import Member  # noqa: F401
from app.models.user import User  # noqa: F401
from app.routers import auth, books, borrows, members

# Create any tables that don't exist yet.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Library Management System")

# Keeps the signed-in user in a signed, HttpOnly cookie that lasts 8 hours.
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    max_age=60 * 60 * 8,
    same_site="lax",
    https_only=settings.COOKIE_SECURE,
)

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(members.router)
app.include_router(borrows.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


# This must stay LAST. Mounted at "/", it answers every URL that no API
# route above has matched, and serves the files from the frontend folder.
app.mount("/", StaticFiles(directory=settings.FRONTEND_DIR, html=True), name="frontend")