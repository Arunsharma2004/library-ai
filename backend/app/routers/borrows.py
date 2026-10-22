from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.borrow import BorrowRead, IssueRequest
from app.services import borrow_service
from app.services.errors import BusinessRuleError, NotFoundError

router = APIRouter(
    prefix="/api/borrows",
    tags=["Borrowing"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[BorrowRead])
def list_borrows(
    status_filter: Literal["active", "overdue", "returned"] | None = Query(None, alias="status"),
    member_id: int | None = None,
    book_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return borrow_service.list_borrows(db, status_filter, member_id, book_id, skip, limit)


@router.post("/issue", response_model=BorrowRead, status_code=status.HTTP_201_CREATED)
def issue_book(
    data: IssueRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return borrow_service.issue_book(db, data, issued_by=user.username)
    except NotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    except BusinessRuleError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))


@router.post("/{record_id}/return", response_model=BorrowRead)
def return_book(record_id: int, db: Session = Depends(get_db)):
    try:
        return borrow_service.return_book(db, record_id)
    except NotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    except BusinessRuleError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))