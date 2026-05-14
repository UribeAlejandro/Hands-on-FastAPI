from pydantic import BaseModel, Field


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = Field(default="bearer")
