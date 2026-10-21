from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.book import Book
from app.schemas.book import BookCreate
from app.services.errors import DuplicateError, NotFoundError


def get_book(db: Session, book_id: int) -> Book:
    book = db.get(Book, book_id)
    if book is None:
        raise NotFoundError(f"Book {book_id} not found")
    return book


def create_book(db: Session, data: BookCreate) -> Book:
    if data.isbn and db.scalar(select(Book).where(Book.isbn == data.isbn)):
        raise DuplicateError(f"A book with ISBN {data.isbn} already exists")

    # A new book starts with every copy available.
    book = Book(**data.model_dump(), available_copies=data.total_copies)
    db.add(book)
    db.commit()
    db.refresh(book)  # reloads the id and timestamps the database generated
    return book


def list_books(
    db: Session,
    search: str | None = None,
    category: str | None = None,
    available_only: bool = False,
    skip: int = 0,
    limit: int = 50,
) -> list[Book]:
    query = select(Book)

    if search:
        pattern = f"%{search}%"
        query = query.where(
            or_(
                Book.title.ilike(pattern),
                Book.author.ilike(pattern),
                Book.isbn.ilike(pattern),
            )
        )
    if category:
        query = query.where(Book.category.ilike(category))
    if available_only:
        query = query.where(Book.available_copies > 0)

    query = query.order_by(Book.title).offset(skip).limit(limit)
    return list(db.scalars(query))