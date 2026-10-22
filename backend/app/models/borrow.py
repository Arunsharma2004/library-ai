from datetime import date

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.book import Book
from app.models.member import Member


class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), index=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), index=True)
    issued_on: Mapped[date]
    due_on: Mapped[date]
    returned_on: Mapped[date | None]  # empty until the book comes back
    issued_by: Mapped[str | None] = mapped_column(String(100))  # filled in by the login phase

    # These let us write record.book.title and record.member.name.
    book: Mapped[Book] = relationship()
    member: Mapped[Member] = relationship()

    # Extra read-only values the API shows, calculated on the fly.
    @property
    def book_title(self) -> str:
        return self.book.title

    @property
    def member_name(self) -> str:
        return self.member.name

    @property
    def is_overdue(self) -> bool:
        return self.returned_on is None and self.due_on < date.today()