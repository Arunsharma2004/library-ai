from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.book import BookRead


class RecommendationRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    mood: str = Field(min_length=1, max_length=100)
    interests: str = Field(min_length=1, max_length=200)
    length: Literal["short", "long", "any"] = "any"


class RecommendationItem(BaseModel):
    book: BookRead
    reason: str


class RecommendationResponse(BaseModel):
    recommendations: list[RecommendationItem]