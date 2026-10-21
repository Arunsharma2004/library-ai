from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    author: Mapped[str] = mapped_column(String(255), index=True)
    isbn: Mapped[str | None] = mapped_column(String(20), unique=True)
    category: Mapped[str | None] = mapped_column(String(100), index=True)
    published_year: Mapped[int | None]
    description: Mapped[str | None] = mapped_column(Text)

    # Availability: Phase 2 (issue/return) will change available_copies.
    total_copies: Mapped[int] = mapped_column(default=1)
    available_copies: Mapped[int] = mapped_column(default=1)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )