from pydantic import BaseModel, ConfigDict, Field


class DescribeRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=255)
    author: str = Field(min_length=1, max_length=255)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    published_year: int | None = Field(default=None, ge=1000, le=2100)


class DescribeResponse(BaseModel):
    description: str