from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, UserRead
from app.services import user_service

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=UserRead)
def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = user_service.authenticate(db, data.username, data.password)
    if user is None:
        # The same message for "no such user" and "wrong password", so nobody can
        # use this endpoint to find out which usernames exist.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password"
        )
    request.session.clear()
    request.session["user_id"] = user.id
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request):
    request.session.clear()


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)):
    return user