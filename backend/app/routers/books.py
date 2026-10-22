from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_staff_or_visitor
from app.schemas.book import BookCreate, BookRead, BookUpdate
from app.services import book_service
from app.services.errors import BusinessRuleError, DuplicateError, NotFoundError

router = APIRouter(prefix="/api/books", tags=["Books"])


# ---------- Reading: staff and visitors ----------
@router.get(
    "", response_model=list[BookRead], dependencies=[Depends(require_staff_or_visitor)]
)
def list_books(
    search: str | None = None,
    category: str | None = None,
    available_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return book_service.list_books(db, search, category, available_only, skip, limit)


@router.get(
    "/{book_id}", response_model=BookRead, dependencies=[Depends(require_staff_or_visitor)]
)
def get_book(book_id: int, db: Session = Depends(get_db)):
    try:
        return book_service.get_book(db, book_id)
    except NotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


# ---------- Changing: staff only ----------
@router.post(
    "",
    response_model=BookRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def create_book(data: BookCreate, db: Session = Depends(get_db)):
    try:
        return book_service.create_book(db, data)
    except DuplicateError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))


@router.patch(
    "/{book_id}", response_model=BookRead, dependencies=[Depends(get_current_user)]
)
def update_book(book_id: int, data: BookUpdate, db: Session = Depends(get_db)):
    try:
        return book_service.update_book(db, book_id, data)
    except NotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    except (DuplicateError, BusinessRuleError) as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    try:
        book_service.delete_book(db, book_id)
    except NotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    except BusinessRuleError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))