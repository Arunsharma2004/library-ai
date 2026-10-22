from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.errors import BusinessRuleError, DuplicateError
from app.services.security import hash_password, verify_password

MIN_PASSWORD_LENGTH = 8


def create_user(db: Session, username: str, password: str) -> User:
    username = username.strip().lower()
    if not username:
        raise BusinessRuleError("Username cannot be empty")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise BusinessRuleError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters")
    if db.scalar(select(User).where(User.username == username)):
        raise DuplicateError(f"User {username} already exists")

    user = User(username=username, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, username: str, password: str) -> User | None:
    """Returns the user if the password is right, otherwise None."""
    user = db.scalar(select(User).where(User.username == username.strip().lower()))
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user