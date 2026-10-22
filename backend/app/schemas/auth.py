from typing import Literal

from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class SessionRead(BaseModel):
    """Who is using the app right now. Used by the menu."""

    role: Literal["staff", "visitor"]
    username: str | None = None