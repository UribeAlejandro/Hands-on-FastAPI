from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status

from src.common.exceptions import UserNotFoundException
from src.todo.dependency import get_to_do_service
from src.todo.models import ToDo, ToDoCreate, ToDoUpdate
from src.todo.schemas import PaginatedTodos
from src.todo.service import ToDoService

router = APIRouter(prefix="/todo", tags=["To Do"])


@router.post("/", response_model=ToDo, status_code=status.HTTP_201_CREATED)
async def create_todo(
    service: Annotated[ToDoService, Depends(get_to_do_service)],
    todo: ToDoCreate = Body(..., description="The ToDo item) to create"),
) -> ToDo:
    """
    Create a new ToDo item.

    Parameters
    ----------
    todo : ToDoCreate
        The ToDo item to create.

    Returns
    -------
    ToDo
        The created ToDo item.
    """
    try:
        _todo = await service.create_todo(todo)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="User not found")
    return _todo


@router.get("/", response_model=PaginatedTodos, status_code=status.HTTP_200_OK)
async def list_todos(
    service: Annotated[ToDoService, Depends(get_to_do_service)],
    search: str = Query("", description="Search term to filter ToDo items by title"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> PaginatedTodos:
    """
    List ToDo items with optional search, pagination, and filtering.

    Parameters
    ----------
    search : str, optional
        A search term to filter ToDo items by title (default is an empty string).
    limit : int, optional
        The maximum number of ToDo items to return (default is 10).
    offset : int, optional
        The number of ToDo items to skip before starting to collect the result set (default is 0).

    Returns
    -------
    PaginatedTodos
        A paginated list of ToDo items matching the search criteria and pagination settings.
    """
    return await service.list_todos(search, limit, offset)


@router.get("/{todo_id}", response_model=ToDo | None, status_code=status.HTTP_200_OK)
async def get_todo_by_id(
    service: Annotated[ToDoService, Depends(get_to_do_service)],
    todo_id: UUID = Path(..., description="The ID of the ToDo item to retrieve"),
) -> ToDo | None:
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
    _todo = await service.get_by_id(todo_id)
    if _todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ToDo item not found")
    return _todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_by_id(
    service: Annotated[ToDoService, Depends(get_to_do_service)],
    todo_id: UUID = Path(..., description="The ID of the ToDo item to delete"),
) -> None:
    """
    Delete a ToDo item by its ID.

    Parameters
    ----------
    todo_id : UUID
        The ID of the ToDo item to delete.
    """
    deleted = await service.delete_todo(todo_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ToDo item not found")


@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo_by_id(
    service: Annotated[ToDoService, Depends(get_to_do_service)],
    todo_id: UUID = Path(..., description="The ID of the ToDo item to update"),
    todo: ToDoUpdate = Body(..., description="The updated ToDo item data"),
) -> None:
    """
    Update a ToDo item by its ID.

    Parameters
    ----------
    todo_id : UUID
        The ID of the ToDo item to update.
    todo: ToDoCreate
        The updated ToDo item data.
    service : ToDoService, optional
        The ToDo service instance, by default Depends(get_to_do_service)
    """
    _todo = await service.update_todo(todo_id, todo)
    if _todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ToDo item not found")
