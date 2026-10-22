"""Application settings.

All configuration comes from environment variables (optionally loaded from a
local `.env` file). Secrets such as API keys are NEVER written in source code.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent  # the `backend/` folder
PROJECT_DIR = BASE_DIR.parent                      # the `library-ai/` folder

load_dotenv(BASE_DIR / ".env")

DEFAULT_SECRET_KEY = "dev-only-secret-change-me"


def _flag(name: str, default: bool) -> bool:
    """Reads a true/false setting such as COOKIE_SECURE=true."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def _database_url() -> str:
    url = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'library.db'}")
    # Hosting services often give "postgres://..." or "postgresql://...". Turn them into the
    # form SQLAlchemy needs, naming the PostgreSQL driver (psycopg).
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


def check_production_settings(app_env: str, secret_key: str, cookie_secure: bool) -> None:
    """In production, refuse to start with settings that would be unsafe."""
    if app_env != "production":
        return
    if secret_key == DEFAULT_SECRET_KEY or len(secret_key) < 32:
        raise RuntimeError(
            "SECRET_KEY must be a random string of at least 32 characters in production."
        )
    if not cookie_secure:
        raise RuntimeError("COOKIE_SECURE must be true in production (the site must use HTTPS).")


class Settings:
    # "development" (default) or "production".
    APP_ENV: str = os.getenv("APP_ENV", "development").strip().lower()

    # SQLite for local development. For PostgreSQL, set e.g.
    # DATABASE_URL=postgresql://user:password@localhost:5432/library
    DATABASE_URL: str = _database_url()

    # Folder containing the HTML/CSS/JS files served to the browser.
    FRONTEND_DIR: Path = Path(os.getenv("FRONTEND_DIR", PROJECT_DIR / "frontend"))

    # Signs the login cookie. Must be long, random and secret in production.
    SECRET_KEY: str = os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY)

    # Cookies are sent over HTTPS only. On by default in production.
    COOKIE_SECURE: bool = _flag("COOKIE_SECURE", os.getenv("APP_ENV", "").strip().lower() == "production")

    # AI provider (Google Gemini).
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    # Optional: creates the FIRST staff account at startup if no staff exist yet.
    ADMIN_USERNAME: str | None = os.getenv("ADMIN_USERNAME")
    ADMIN_PASSWORD: str | None = os.getenv("ADMIN_PASSWORD")


settings = Settings()
check_production_settings(settings.APP_ENV, settings.SECRET_KEY, settings.COOKIE_SECURE)