from uuid import UUID

from src.todo.models import ToDo, ToDoCreate
from src.todo.repository import ToDoRepository


class ToDoService:
    """Service layer for managing ToDo items, providing business logic and interaction with the repository."""

    def __init__(self, repository: ToDoRepository):
        self.repository = repository

    async def create_todo(self, todo: ToDoCreate) -> ToDo:
        """
        Create a new ToDo item in the database.

        Parameters
        ----------
        todo : ToDoCreate
            The ToDo item to create.

        Returns
        -------
        ToDo
            The created ToDo item.
        """
        return await self.repository.create_todo(todo)

    async def list_todos(self, search: str, limit: int, offset: int) -> list[ToDo]:
        """
        List ToDo items with optional search, pagination, and filtering.

        Parameters
        ----------
        search : str
            A search term to filter ToDo items by title.
        limit : int
            The maximum number of ToDo items to return.
        offset : int
            The number of ToDo items to skip before starting to collect the result set.

        Returns
        -------
        list[ToDo]
            A list of ToDo items matching the search criteria and pagination settings.
        """
        return await self.repository.list_todos(search, limit, offset)

    async def get_by_id(self, todo_id: UUID) -> ToDo | None:
        """
        Get a ToDo item by its ID.

        Parameters
        ----------
        todo_id : UUID
            The ID of the ToDo item to retrieve.

        Returns
        -------
        ToDo | None
            The ToDo item with the specified ID, or None if not found.
        """
        return await self.repository.get_by_id(todo_id)

    async def delete_todo(self, todo_id: UUID) -> bool:
        """
        Delete a ToDo item by its ID.

        Parameters
        ----------
        todo_id : UUID
            The ID of the ToDo item to delete.

        Returns
        -------
        bool
            True if the ToDo item was deleted, False if not found.
        """
        return await self.repository.delete_todo(todo_id)

    async def update_todo(self, todo_id: UUID, todo: ToDoCreate) -> ToDo | None:
        """
        Update a ToDo item by its ID.

        Parameters
        ----------
        todo_id : UUID
            The ID of the ToDo item to update.
        todo : ToDoCreate
            The updated ToDo item data.

        Returns
        -------
        ToDo | None
            The updated ToDo item, or None if not found.
        """
        return await self.repository.update_todo(todo_id, todo)
