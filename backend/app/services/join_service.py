from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.member import Member
from app.schemas.join import JoinRequest


def request_to_join(db: Session, data: JoinRequest) -> None:
    """Creates a PENDING (inactive) member. Staff activate them later.

    If the email already exists we do nothing, so the caller can't tell who is a member.
    """
    email = data.email.lower()
    if db.scalar(select(Member).where(Member.email == email)):
        return

    db.add(Member(name=data.name, email=email, phone=data.phone or None, is_active=False))
    try:
        db.commit()
    except IntegrityError:  # two identical requests arrived at the same moment
        db.rollback()