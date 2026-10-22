from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.member import Member
from app.schemas.join import JoinRequest


def request_to_join(db: Session, data: JoinRequest) -> int | None:
    """Creates a PENDING (inactive) member. Staff activate them later.

    Returns the new member's id. If the email already exists it does nothing and
    returns None, so the caller can't use this form to take over an existing member.
    """
    email = data.email.lower()
    if db.scalar(select(Member).where(Member.email == email)):
        return None

    member = Member(name=data.name, email=email, phone=data.phone or None, is_active=False)
    db.add(member)
    try:
        db.commit()
    except IntegrityError:  # two identical requests arrived at the same moment
        db.rollback()
        return None
    return member.id