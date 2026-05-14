from datetime import datetime
from uuid import UUID, uuid4

from pydantic import ConfigDict, EmailStr
from sqlmodel import TIMESTAMP, Column, Field, SQLModel, text

from src.auth.users.enum import UserRole


class UserBase(SQLModel):
    """Base model for User."""

    model_config = ConfigDict(use_enum_values=True)

    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr = Field(..., max_length=120)
    username: str = Field(..., min_length=3, max_length=50)
    is_active: bool = Field(default=True)
    role: UserRole = Field(default=UserRole.USER)


class UserCreate(UserBase):
    """Model for creating a new User, including password field."""

    password: str = Field(min_length=12, max_length=72)


class UserCreatePrivate(UserBase):
    """Model for creating a new User, including password field."""

    password_hash: str


class UserUpdate(UserBase):
    """Model for updating an existing User, all fields optional."""

    first_name: str | None = Field(default=None, min_length=1, max_length=50)  # pyrefly: ignore[bad-override-mutable-attribute]
    last_name: str | None = Field(default=None, min_length=1, max_length=50)  # pyrefly: ignore[bad-override-mutable-attribute]
    email: EmailStr | None = Field(default=None, max_length=120)  # pyrefly: ignore[bad-override-mutable-attribute]
    username: str | None = Field(default=None, min_length=3, max_length=50)  # pyrefly: ignore[bad-override-mutable-attribute]
    is_active: bool | None = Field(default=None)  # pyrefly: ignore[bad-override-mutable-attribute]
    role: UserRole | None = Field(default=None)  # pyrefly: ignore[bad-override-mutable-attribute]


class User(UserCreatePrivate, table=True):
    """Model representing a User in the database."""

    __tablename__ = "users"  # pyrefly: ignore[bad-override]

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        )
    )
    updated_at: datetime | None = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=text("CURRENT_TIMESTAMP"),
        )
    )


class UserRead(UserBase):
    """Model for reading User data, excluding sensitive fields."""

    id: UUID
