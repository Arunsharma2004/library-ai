from pydantic import BaseModel, ConfigDict, EmailStr, Field


class JoinRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=20)


class JoinResponse(BaseModel):
    message: str