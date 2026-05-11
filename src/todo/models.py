from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class ToDoBase(SQLModel):
    """Base model for ToDo items."""

    title: str
    description: str | None = Field(default=None)
    priority: int
    completed: bool = Field(default=False)


class ToDo(ToDoBase, table=True):
    """Model representing a ToDo item in the database."""

    __tablename__ = "todos"  # pyrefly: ignore[bad-override]

    id: UUID = Field(default_factory=uuid4, primary_key=True)


class ToDoCreate(ToDoBase):
    """Model for creating a new ToDo item."""

    pass


class PaginatedTodos(BaseModel):
    """Model for paginated ToDo items."""

    total: int
    items: list[ToDo]
