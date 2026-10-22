from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict


class MyLoan(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    book_title: str
    issued_on: date
    due_on: date
    returned_on: date | None
    is_overdue: bool


class AccountRead(BaseModel):
    name: str
    email: str
    status: Literal["pending", "member"]  # pending = staff have not approved yet
    loans: list[MyLoan]