from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Returns the signed-in staff user, or answers 401 if nobody is signed in."""
    user_id = request.session.get("user_id")
    user = db.get(User, user_id) if user_id else None
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please sign in")
    return user