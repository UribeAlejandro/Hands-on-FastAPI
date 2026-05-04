from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from src.todo.dependency import get_to_do_service
from src.todo.models import ToDo, ToDoCreate
from src.todo.service import ToDoService

router = APIRouter(prefix="/todo", tags=["To Do"])


@router.post("/", response_model=ToDo, status_code=201)
async def create_todo(todo: ToDoCreate, service: ToDoService = Depends(get_to_do_service)) -> ToDo:
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
    return await service.create_todo(todo)


@router.get("/", response_model=list[ToDo])
async def list_todos(
    search: str = Query("", description="Search term to filter ToDo items by title"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: ToDoService = Depends(get_to_do_service),
) -> list[ToDo]:
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
    list[ToDo]
        A list of ToDo items matching the search criteria and pagination settings.
    """
    return await service.list_todos(search, limit, offset)


@router.get("/{todo_id}", response_model=ToDo | None, status_code=200)
async def get_todo_by_id(
    todo_id: UUID,
    service: ToDoService = Depends(get_to_do_service),
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
    return await service.get_by_id(todo_id)


@router.delete("/{todo_id}", status_code=200)
async def delete_todo_by_id(
    todo_id: UUID,
    service: ToDoService = Depends(get_to_do_service),
) -> JSONResponse:
    """
    Delete a ToDo item by its ID.

    Parameters
    ----------
    todo_id : UUID
        The ID of the ToDo item to delete.

    Returns
    -------
    JSONResponse
        A JSON response indicating whether the ToDo item was deleted.
    """
    deleted = await service.delete_todo(todo_id)
    return JSONResponse(content={"deleted": deleted})


@router.put("/{todo_id}", response_model=ToDo | None, status_code=201)
async def update_todo_by_id(
    todo_id: UUID,
    todo: ToDoCreate,
    service: ToDoService = Depends(get_to_do_service),
) -> ToDo | None:
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

    Returns
    -------
    ToDo | None
        The updated ToDo item, or None if not found.
    """
    return await service.update_todo(todo_id, todo)
