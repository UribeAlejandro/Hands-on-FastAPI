from datetime import datetime
from uuid import UUID, uuid4

from pydantic import field_serializer
from sqlmodel import TIMESTAMP, Column, Field, SQLModel, text


class ToDoBase(SQLModel):
    """Base model for ToDo items."""

    title: str
    description: str | None = Field(default=None)
    priority: int
    completed: bool = Field(default=False)


class ToDoUserForeignKeyBase(SQLModel):
    """Base model for ToDo items with a foreign key to the User model."""

    user_id: UUID = Field(foreign_key="users.id", index=True, ondelete="CASCADE")

    @field_serializer("user_id")
    def serialize_user_id(self, value: UUID) -> str:
        """Serialize the user_id field as a string."""
        return str(value)


class ToDo(ToDoBase, ToDoUserForeignKeyBase, table=True):
    """Model representing a ToDo item in the database."""

    __tablename__ = "todos"  # pyrefly: ignore[bad-override]

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


class ToDoCreate(ToDoBase, ToDoUserForeignKeyBase):
    """Model for creating a new ToDo item."""

    pass


class ToDoUpdate(ToDoBase):
    """Model for updating an existing ToDo item."""

    title: str | None = None  # pyrefly: ignore[bad-override-mutable-attribute]
    description: str | None = None  # pyrefly: ignore[bad-override-mutable-attribute]
    priority: int | None = None  # pyrefly: ignore[bad-override-mutable-attribute]
    completed: bool | None = None  # pyrefly: ignore[bad-override-mutable-attribute]
