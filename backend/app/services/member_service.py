from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.member import Member
from app.schemas.member import MemberCreate, MemberUpdate
from app.models.borrow import BorrowRecord
from app.services.errors import BusinessRuleError, DuplicateError, NotFoundError

REQUIRED_FIELDS = {"name", "email", "is_active"}


def get_member(db: Session, member_id: int) -> Member:
    member = db.get(Member, member_id)
    if member is None:
        raise NotFoundError(f"Member {member_id} not found")
    return member


def _email_taken(db: Session, email: str) -> bool:
    return db.scalar(select(Member).where(Member.email == email)) is not None


def create_member(db: Session, data: MemberCreate) -> Member:
    email = data.email.lower()  # store emails in lowercase so duplicates can't hide
    if _email_taken(db, email):
        raise DuplicateError(f"A member with email {email} already exists")

    member = Member(name=data.name, email=email, phone=data.phone)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def list_members(
    db: Session,
    search: str | None = None,
    active_only: bool = False,
    skip: int = 0,
    limit: int = 50,
) -> list[Member]:
    query = select(Member)
    if search:
        pattern = f"%{search}%"
        query = query.where(or_(Member.name.ilike(pattern), Member.email.ilike(pattern)))
    if active_only:
        query = query.where(Member.is_active.is_(True))

    query = query.order_by(Member.name).offset(skip).limit(limit)
    return list(db.scalars(query))


def update_member(db: Session, member_id: int, data: MemberUpdate) -> Member:
    member = get_member(db, member_id)

    changes = data.model_dump(exclude_unset=True)
    changes = {k: v for k, v in changes.items() if not (v is None and k in REQUIRED_FIELDS)}

    if "email" in changes:
        changes["email"] = changes["email"].lower()
        if changes["email"] != member.email and _email_taken(db, changes["email"]):
            raise DuplicateError(f"A member with email {changes['email']} already exists")

    for field, value in changes.items():
        setattr(member, field, value)

    db.commit()
    db.refresh(member)
    return member

def delete_member(db: Session, member_id: int) -> None:
    member = get_member(db, member_id)
    has_history = db.scalar(
        select(BorrowRecord.id).where(BorrowRecord.member_id == member_id).limit(1)
    )
    if has_history is not None:
        raise BusinessRuleError(
            "This member has borrowing records, so they cannot be deleted. "
            "Deactivate them instead."
        )
    db.delete(member)
    db.commit()