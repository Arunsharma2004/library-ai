from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.borrow import BorrowRecord
from app.models.member import Member
from app.services.errors import NotFoundError


def get_member_with_loans(db: Session, member_id: int) -> tuple[Member, list[BorrowRecord]]:
    """One member and their own loans, newest first."""
    member = db.get(Member, member_id)
    if member is None:
        raise NotFoundError("This membership no longer exists")

    loans = db.scalars(
        select(BorrowRecord)
        .where(BorrowRecord.member_id == member_id)
        .order_by(BorrowRecord.id.desc())
    )
    return member, list(loans)