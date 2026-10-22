from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_staff_or_visitor
from app.schemas.account import AccountRead
from app.services import account_service
from app.services.errors import NotFoundError

router = APIRouter(
    prefix="/api/my",
    tags=["My account"],
    dependencies=[Depends(require_staff_or_visitor)],
)


@router.get("/account", response_model=AccountRead)
def my_account(request: Request, db: Session = Depends(get_db)):
    """The member linked to this browser (set when they joined). Nobody else's data."""
    member_id = request.session.get("member_id")
    if member_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No membership is linked to this browser",
        )
    try:
        member, loans = account_service.get_member_with_loans(db, member_id)
    except NotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))

    return {
        "name": member.name,
        "email": member.email,
        "status": "member" if member.is_active else "pending",
        "loans": loans,
    }