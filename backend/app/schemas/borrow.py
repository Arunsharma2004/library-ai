from datetime import date

from pydantic import BaseModel, ConfigDict


class IssueRequest(BaseModel):
    book_id: int
    member_id: int


class BorrowRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    book_id: int
    member_id: int
    book_title: str
    member_name: str
    issued_on: date
    due_on: date
    returned_on: date | None
    issued_by: str | None
    is_overdue: bool