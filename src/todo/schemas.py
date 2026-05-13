from pydantic import BaseModel

from src.todo.models import ToDo


class PaginatedTodos(BaseModel):
    """Model for paginated ToDo items."""

    total: int
    items: list[ToDo]
