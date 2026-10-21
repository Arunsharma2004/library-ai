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



settings = Settings()