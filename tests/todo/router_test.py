import uuid

import pytest

from src.todo.models import ToDoCreate, ToDoUpdate
from src.todo.schemas import PaginatedTodos
from tests.conftest import create_todo, create_user


@pytest.mark.anyio
async def test_empty_table(test_app) -> None:
    """Test listing todo items when the database is empty."""
    response = await test_app.get("/todo/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.anyio
async def test_get_non_existent_todo_by_id(test_app) -> None:
    """Test retrieving a non-existent todo item by its ID."""
    _uuid = uuid.uuid4()
    response = await test_app.get(f"/todo/{_uuid}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "ToDo item not found"


@pytest.mark.anyio
async def test_delete_non_existent_todo_by_id(test_app) -> None:
    """Test deleting a non-existent todo item by its ID."""
    _uuid = uuid.uuid4()
    response = await test_app.delete(f"/todo/{_uuid}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "ToDo item not found"


@pytest.mark.anyio
async def test_update_non_existent_todo_by_id(test_app) -> None:
    """Test updating a non-existent todo item by its ID."""
    _uuid = uuid.uuid4()
    updated_todo = ToDoUpdate(title="Updated Test Todo", description="This is an updated test todo item.", priority=2)
    response = await test_app.put(f"/todo/{_uuid}", json=updated_todo.model_dump())
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "ToDo item not found"


@pytest.mark.anyio
async def test_create_todo_non_existent_user(test_app) -> None:
    """Test the creation of a new todo item."""
    todo = ToDoCreate(title="Test Todo", description="This is a test todo item.", priority=1, user_id=uuid.uuid4())
    response = await test_app.post("/todo/", json=todo.model_dump())
    assert response.status_code == 422
    data = response.json()
    assert data["detail"] == "User not found"


@pytest.mark.anyio
async def test_create_todo(test_app) -> None:
    """Test the creation of a new todo item."""
    user = await create_user(test_app)
    todo = await create_todo(test_app, user.id)
    todo_id = str(todo.id)

    result = await test_app.get(f"/todo/{todo_id}")
    assert result.status_code == 200
    data = result.json()
    assert data["title"] == todo.title
    assert data["description"] == todo.description
    assert data["priority"] == todo.priority
    assert data["completed"] == todo.completed
    assert data["id"] == todo_id


@pytest.mark.anyio
async def test_list_todos(test_app) -> None:
    """Test listing todo items."""
    response = await test_app.get("/todo/")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert PaginatedTodos.model_validate(data)
    assert isinstance(data["items"], list)
    assert all("id" in item for item in data["items"])
    assert all("title" in item for item in data["items"])
    assert all("description" in item for item in data["items"])
    assert all("priority" in item for item in data["items"])
    assert all("completed" in item for item in data["items"])


@pytest.mark.anyio
async def test_get_todo_by_id(test_app) -> None:
    """Test retrieving a todo item by its ID."""
    user = await create_user(test_app)
    todo = await create_todo(test_app, user.id)
    todo_id = str(todo.id)

    response = await test_app.get(f"/todo/{todo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == todo.title
    assert data["description"] == todo.description
    assert data["priority"] == todo.priority
    assert data["completed"] == todo.completed


@pytest.mark.anyio
async def test_delete_todo_by_id(test_app) -> None:
    """Test deleting a todo item by its ID."""
    user = await create_user(test_app)
    todo = await create_todo(test_app, user.id)
    todo_id = str(todo.id)

    response = await test_app.delete(f"/todo/{todo_id}")
    assert response.status_code == 204

    result = await test_app.get(f"/todo/{todo_id}")
    assert result.status_code == 404
    data = result.json()
    assert data["detail"] == "ToDo item not found"


@pytest.mark.anyio
async def test_update_todo_by_id(test_app) -> None:
    """Test updating a todo item by its ID."""
    user = await create_user(test_app)
    todo = await create_todo(test_app, user.id)
    todo_id = str(todo.id)

    updated_todo = ToDoUpdate(title="Updated Test Todo", description="This is an updated test todo item.")
    response = await test_app.put(f"/todo/{todo_id}", json=updated_todo.model_dump())
    assert response.status_code == 204

    result = await test_app.get(f"/todo/{todo_id}")
    assert result.status_code == 200
    data = result.json()
    assert data["id"] == todo_id
    assert data["title"] == updated_todo.title
    assert data["description"] == updated_todo.description
    assert data["priority"] == todo.priority
    assert data["completed"] == todo.completed
