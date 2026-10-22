"""Creates a staff account.

Usage (from the backend folder):
    python -m app.scripts.create_staff librarian1
The password is asked for in the terminal, so it never stays in your shell history.
"""
import getpass
import sys

from app.database import Base, SessionLocal, engine
from app.models.book import Book  # noqa: F401  (importing registers the tables)
from app.models.borrow import BorrowRecord  # noqa: F401
from app.models.member import Member  # noqa: F401
from app.models.user import User  # noqa: F401
from app.services import user_service
from app.services.errors import BusinessRuleError, DuplicateError


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python -m app.scripts.create_staff <username>")
        sys.exit(1)

    password = getpass.getpass("Password: ")
    if password != getpass.getpass("Repeat password: "):
        print("The passwords do not match.")
        sys.exit(1)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user = user_service.create_user(db, sys.argv[1], password)
        print(f"Created staff account: {user.username}")
    except (DuplicateError, BusinessRuleError) as error:
        print(error)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()