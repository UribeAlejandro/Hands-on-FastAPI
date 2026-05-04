from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database import get_db
from src.todo.repository import ToDoRepository
from src.todo.service import ToDoService


async def get_to_do_repository(session: AsyncSession = Depends(get_db)) -> ToDoRepository:
    """Get a ToDo repository."""
    return ToDoRepository(session)


async def get_to_do_service(repository: ToDoRepository = Depends(get_to_do_repository)) -> ToDoService:
    """Get a ToDo service."""
    return ToDoService(repository)
