from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.member import MemberCreate, MemberRead, MemberUpdate
from app.services import member_service
from app.services.errors import BusinessRuleError, DuplicateError, NotFoundError

router = APIRouter(prefix="/api/members", tags=["Members"])


@router.get("", response_model=list[MemberRead])
def list_members(
    search: str | None = None,
    active_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return member_service.list_members(db, search, active_only, skip, limit)


@router.get("/{member_id}", response_model=MemberRead)
def get_member(member_id: int, db: Session = Depends(get_db)):
    try:
        return member_service.get_member(db, member_id)
    except NotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


@router.post("", response_model=MemberRead, status_code=status.HTTP_201_CREATED)
def create_member(data: MemberCreate, db: Session = Depends(get_db)):
    try:
        return member_service.create_member(db, data)
    except DuplicateError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))


@router.patch("/{member_id}", response_model=MemberRead)
def update_member(member_id: int, data: MemberUpdate, db: Session = Depends(get_db)):
    try:
        return member_service.update_member(db, member_id, data)
    except NotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    except DuplicateError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int, db: Session = Depends(get_db)):
    try:
        member_service.delete_member(db, member_id)
    except NotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    except BusinessRuleError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))