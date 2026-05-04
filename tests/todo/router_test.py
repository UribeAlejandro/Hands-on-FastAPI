import pytest

from src.todo.models import ToDoCreate


@pytest.mark.anyio
async def test_create_todo(test_app) -> None:
    """Test the creation of a new todo item."""
    todo = ToDoCreate(title="Test Todo", description="This is a test todo item.", priority=1)

    response = await test_app.post("/todo/", json=todo.model_dump())
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["description"] == "This is a test todo item."
    assert data["priority"] == 1
    assert data["completed"] is False
    assert "id" in data


@pytest.mark.anyio
async def test_list_todos(test_app) -> None:
    """Test listing todo items."""
    response = await test_app.get("/todo/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_get_todo_by_id(test_app) -> None:
    """Test retrieving a todo item by its ID."""
    # First, create a new todo item to ensure there is at least one item in the database
    todo = ToDoCreate(title="Test Todo for Get", description="This is a test todo item for get.", priority=1)
    create_response = await test_app.post("/todo/", json=todo.model_dump())
    assert create_response.status_code == 201
    created_todo = create_response.json()
    todo_id = created_todo["id"]

    # Now, retrieve the created todo item by its ID
    response = await test_app.get(f"/todo/{todo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == "Test Todo for Get"
    assert data["description"] == "This is a test todo item for get."
    assert data["priority"] == 1
    assert data["completed"] is False


@pytest.mark.anyio
async def test_delete_todo_by_id(test_app) -> None:
    """Test deleting a todo item by its ID."""
    # First, create a new todo item to ensure there is at least one item in the database
    todo = ToDoCreate(title="Test Todo for Delete", description="This is a test todo item for delete.", priority=1)
    create_response = await test_app.post("/todo/", json=todo.model_dump())
    assert create_response.status_code == 201
    created_todo = create_response.json()
    todo_id = created_todo["id"]

    # Now, delete the created todo item by its ID
    response = await test_app.delete(f"/todo/{todo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["deleted"] is True


@pytest.mark.anyio
async def test_update_todo_by_id(test_app) -> None:
    """Test updating a todo item by its ID."""
    # First, create a new todo item to ensure there is at least one item in the database
    todo = ToDoCreate(title="Test Todo for Update", description="This is a test todo item for update.", priority=1)
    create_response = await test_app.post("/todo/", json=todo.model_dump())
    assert create_response.status_code == 201
    created_todo = create_response.json()
    todo_id = created_todo["id"]

    # Now, update the created todo item by its ID
    updated_todo = ToDoCreate(title="Updated Test Todo", description="This is an updated test todo item.", priority=2)
    response = await test_app.put(f"/todo/{todo_id}", json=updated_todo.model_dump())
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == "Updated Test Todo"
    assert data["description"] == "This is an updated test todo item."
    assert data["priority"] == 2
    assert data["completed"] is False
