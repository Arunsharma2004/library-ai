from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.book import BookRead


class ChatMessage(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=1000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=20)

    @field_validator("messages")
    @classmethod
    def last_message_must_be_from_the_reader(cls, messages):
        if messages[-1].role != "user":
            raise ValueError("The last message must be from the reader")
        return messages


class ChatResponse(BaseModel):
    reply: str
    books: list[BookRead]