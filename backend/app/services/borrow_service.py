from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.borrow import BorrowRecord
from app.schemas.borrow import IssueRequest
from app.services import book_service, member_service
from app.services.errors import BusinessRuleError, NotFoundError

LOAN_DAYS = 14


def issue_book(db: Session, data: IssueRequest, issued_by: str | None = None) -> BorrowRecord:
    book = book_service.get_book(db, data.book_id)
    member = member_service.get_member(db, data.member_id)

    if not member.is_active:
        raise BusinessRuleError(f"{member.name} is not an active member")
    if book.available_copies < 1:
        raise BusinessRuleError(f'No copies of "{book.title}" are available')

    already_has_it = db.scalar(
        select(BorrowRecord).where(
            BorrowRecord.book_id == book.id,
            BorrowRecord.member_id == member.id,
            BorrowRecord.returned_on.is_(None),
        )
    )
    if already_has_it:
        raise BusinessRuleError(f'{member.name} already has "{book.title}"')

    today = date.today()
    record = BorrowRecord(
        book_id=book.id,
        member_id=member.id,
        issued_on=today,
        due_on=today + timedelta(days=LOAN_DAYS),
        issued_by=issued_by,
    )
    book.available_copies -= 1  # saved in the same commit as the record
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def return_book(db: Session, record_id: int) -> BorrowRecord:
    record = db.get(BorrowRecord, record_id)
    if record is None:
        raise NotFoundError(f"Borrow record {record_id} not found")
    if record.returned_on is not None:
        raise BusinessRuleError("This book has already been returned")

    record.returned_on = date.today()
    record.book.available_copies += 1
    db.commit()
    db.refresh(record)
    return record


def list_borrows(
    db: Session,
    status: str | None = None,  # "active", "overdue" or "returned"
    member_id: int | None = None,
    book_id: int | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[BorrowRecord]:
    query = select(BorrowRecord).options(
        joinedload(BorrowRecord.book), joinedload(BorrowRecord.member)
    )

    if status == "active":
        query = query.where(BorrowRecord.returned_on.is_(None))
    elif status == "overdue":
        query = query.where(
            BorrowRecord.returned_on.is_(None), BorrowRecord.due_on < date.today()
        )
    elif status == "returned":
        query = query.where(BorrowRecord.returned_on.is_not(None))

    if member_id:
        query = query.where(BorrowRecord.member_id == member_id)
    if book_id:
        query = query.where(BorrowRecord.book_id == book_id)

    query = query.order_by(BorrowRecord.id.desc()).offset(skip).limit(limit)
    return list(db.scalars(query))