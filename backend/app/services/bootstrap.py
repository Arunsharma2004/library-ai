from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.security import hash_password


def create_first_staff(db: Session, username: str | None, password: str | None) -> bool:
    """Creates the first staff account, only when there are no staff yet.

    Returns True if it created one. It never changes an existing account.
    """
    if not username or not password:
        return False
    if db.scalar(select(User.id).limit(1)) is not None:
        return False  # staff already exist: leave them alone
    if len(password) < 8:
        raise RuntimeError("ADMIN_PASSWORD must be at least 8 characters.")

    db.add(User(username=username.strip().lower(), password_hash=hash_password(password)))
    db.commit()
    return True