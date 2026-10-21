from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate
from app.services.errors import BusinessRuleError, DuplicateError, NotFoundError


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

REQUIRED_FIELDS = {"title", "author", "total_copies"}


def update_book(db: Session, book_id: int, data: BookUpdate) -> Book:
    book = get_book(db, book_id)

    # exclude_unset=True keeps only the fields the client actually sent.
    changes = data.model_dump(exclude_unset=True)
    # Required fields cannot be set to null, so ignore those.
    changes = {k: v for k, v in changes.items() if not (v is None and k in REQUIRED_FIELDS)}

    new_isbn = changes.get("isbn")
    if new_isbn and new_isbn != book.isbn:
        if db.scalar(select(Book).where(Book.isbn == new_isbn)):
            raise DuplicateError(f"A book with ISBN {new_isbn} already exists")

    if "total_copies" in changes:
        borrowed = book.total_copies - book.available_copies
        if changes["total_copies"] < borrowed:
            raise BusinessRuleError(
                f"Total copies cannot be below {borrowed}, "
                f"because {borrowed} copies are currently borrowed"
            )
        # Keep the number of borrowed copies the same.
        book.available_copies = changes["total_copies"] - borrowed

    for field, value in changes.items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book_id: int) -> None:
    book = get_book(db, book_id)
    db.delete(book)
    db.commit()