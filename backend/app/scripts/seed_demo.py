"""Adds 20 demo books so the app has something to show.

Usage (from the backend folder):
    python -m app.scripts.seed_demo
Books that already exist (same title and author) are skipped.
"""
from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models.book import Book
from app.models.borrow import BorrowRecord  # noqa: F401  (importing registers the tables)
from app.models.member import Member  # noqa: F401
from app.models.user import User  # noqa: F401

# (title, author, category, year, copies)
BOOKS = [
    ("Dune", "Frank Herbert", "Science Fiction", 1965, 2),
    ("The Martian", "Andy Weir", "Science Fiction", 2011, 2),
    ("The Hobbit", "J.R.R. Tolkien", "Fantasy", 1937, 3),
    ("A Game of Thrones", "George R.R. Martin", "Fantasy", 1996, 2),
    ("Gone Girl", "Gillian Flynn", "Mystery", 2012, 2),
    ("The Girl with the Dragon Tattoo", "Stieg Larsson", "Mystery", 2005, 1),
    ("Sapiens", "Yuval Noah Harari", "History", 2011, 3),
    ("Guns, Germs, and Steel", "Jared Diamond", "History", 1997, 1),
    ("Atomic Habits", "James Clear", "Self-help", 2018, 3),
    ("The 7 Habits of Highly Effective People", "Stephen R. Covey", "Self-help", 1989, 2),
    ("Zero to One", "Peter Thiel", "Business", 2014, 2),
    ("The Lean Startup", "Eric Ries", "Business", 2011, 2),
    ("A Brief History of Time", "Stephen Hawking", "Science", 1988, 2),
    ("Cosmos", "Carl Sagan", "Science", 1980, 2),
    ("The Selfish Gene", "Richard Dawkins", "Science", 1976, 1),
    ("Pride and Prejudice", "Jane Austen", "Classics", 1813, 2),
    ("1984", "George Orwell", "Classics", 1949, 3),
    ("To Kill a Mockingbird", "Harper Lee", "Classics", 1960, 2),
    ("The Alchemist", "Paulo Coelho", "Fiction", 1988, 2),
    ("Educated", "Tara Westover", "Memoir", 2018, 2),
]


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        added = 0
        for title, author, category, year, copies in BOOKS:
            exists = db.scalar(select(Book).where(Book.title == title, Book.author == author))
            if exists:
                continue
            db.add(
                Book(
                    title=title,
                    author=author,
                    category=category,
                    published_year=year,
                    total_copies=copies,
                    available_copies=copies,
                )
            )
            added += 1
        db.commit()
        print(f"Added {added} books ({len(BOOKS) - added} already existed).")
    finally:
        db.close()


if __name__ == "__main__":
    main()