from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BookBase(BaseModel):
    """Fields shared by creating and reading a book."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=255)
    author: str = Field(min_length=1, max_length=255)
    isbn: str | None = Field(default=None, min_length=1, max_length=20)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    published_year: int | None = Field(default=None, ge=1000, le=2100)
    description: str | None = None
    total_copies: int = Field(default=1, ge=1)


class BookCreate(BookBase):
    """What the client sends to add a book."""


class BookUpdate(BaseModel):
    """What the client sends to edit a book. Every field is optional."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=255)
    author: str | None = Field(default=None, min_length=1, max_length=255)
    isbn: str | None = Field(default=None, min_length=1, max_length=20)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    published_year: int | None = Field(default=None, ge=1000, le=2100)
    description: str | None = None
    total_copies: int | None = Field(default=None, ge=1)


class BookRead(BookBase):
    """What the API sends back. Includes fields the database fills in."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    available_copies: int
    created_at: datetime
    updated_at: datetime