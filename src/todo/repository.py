from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Sequence, col, func, or_, select

from src.auth.models import User
from src.common.exceptions import UserNotFoundException
from src.todo.models import ToDo, ToDoCreate, ToDoUpdate


class ToDoRepository:
    """Repository for managing ToDo items in the database."""

    def __init__(self, session: AsyncSession):
        self.session = session

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
        user_id = todo.user_id
        _todo = ToDo(**todo.model_dump())
        # Check user_id exists
        result = await self.session.get(User, user_id)
        if not result:
            raise UserNotFoundException(f"User with id {user_id} does not exist.")

        self.session.add(_todo)
        await self.session.commit()
        await self.session.refresh(_todo)
        return _todo

    async def list_todos(self, search: str, limit: int, offset: int) -> Sequence[ToDo]:
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
        Sequence[ToDo]
            A list of ToDo items matching the search criteria and pagination settings.
        """
        query = select(ToDo)
        if search:
            query = query.where(or_(col(ToDo.title).ilike(f"%{search}%"), col(ToDo.description).ilike(f"%{search}%")))
        result = await self.session.execute(query.offset(offset).limit(limit))
        return result.scalars().all()

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
        result = await self.session.get(ToDo, todo_id)
        return result

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
        todo = await self.get_by_id(todo_id)
        if not todo:
            return False
        await self.session.delete(todo)
        await self.session.commit()
        return True

    async def update_todo(self, todo_id: UUID, todo: ToDoUpdate) -> ToDo | None:
        """
        Update a ToDo item by its ID.

        Parameters
        ----------
        todo_id : UUID
            The ID of the ToDo item to update.
        todo : ToDoUpdate
            The updated ToDo item data.

        Returns
        -------
        ToDo | None
            The updated ToDo item, or None if not found.
        """
        existing_todo = await self.get_by_id(todo_id)
        if not existing_todo:
            return None

        for key, value in todo.model_dump(exclude_none=True).items():
            setattr(existing_todo, key, value)

        self.session.add(existing_todo)
        await self.session.commit()
        await self.session.refresh(existing_todo)
        return existing_todo

    async def count_todos(self, search: str) -> int:
        """
        Count the total number of ToDo items matching the search criteria.

        Parameters
        ----------
        search : str
            A search term to filter ToDo items by title.

        Returns
        -------
        int
            The total number of ToDo items matching the search criteria.
        """
        query = select(func.count(col(ToDo.id)))
        if search:
            query = query.where(or_(col(ToDo.title).ilike(f"%{search}%"), col(ToDo.description).ilike(f"%{search}%")))
        result = await self.session.execute(query)
        return result.scalar_one()
