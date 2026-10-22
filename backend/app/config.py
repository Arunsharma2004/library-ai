"""Application settings, read from environment variables."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent  # the backend/ folder
PROJECT_DIR = BASE_DIR.parent                      # the library-ai/ folder

load_dotenv(BASE_DIR / ".env")  # loads backend/.env if it exists


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'library.db'}")
    FRONTEND_DIR: Path = Path(os.getenv("FRONTEND_DIR", PROJECT_DIR / "frontend"))

    # Signs the login cookie. The default is fine on your laptop, but you MUST set
    # a long random SECRET_KEY in .env before deploying (we'll do that at the end).
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-only-secret-change-me")
    # Set COOKIE_SECURE=true when the site runs on https.
    COOKIE_SECURE: bool = os.getenv("COOKIE_SECURE", "false").lower() == "true"


settings = Settings()