import uuid

import pytest

from src.auth.models import UserCreate, UserRead, UserUpdate
from tests.conftest import create_user


@pytest.mark.anyio
async def test_get_non_existent_user_by_id(test_app) -> None:
    """Test retrieving a non-existent user by their ID."""
    _uuid = uuid.uuid4()
    response = await test_app.get(f"/auth/{str(_uuid)}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"


@pytest.mark.anyio
async def test_update_non_existent_user_by_id(test_app) -> None:
    """Test updating a non-existent user by their ID."""
    _uuid = uuid.uuid4()
    updated_user = UserUpdate(username="updated_test_user")
    response = await test_app.put(f"/auth/{str(_uuid)}", json=updated_user.model_dump())
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"


@pytest.mark.anyio
async def test_delete_non_existent_user_by_id(test_app) -> None:
    """Test deleting a non-existent user by their ID."""
    _uuid = uuid.uuid4()
    response = await test_app.delete(f"/auth/{str(_uuid)}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"


@pytest.mark.anyio
async def test_create_user(test_app) -> None:
    """Test the creation of a new user."""
    user = await create_user(test_app)
    user_id = str(user.id)

    response = await test_app.get(f"/auth/{user_id}")
    assert response.status_code == 200
    data = response.json()

    assert UserRead.model_validate(data)
    assert data["username"] == user.username
    assert data["email"] == user.email
    assert data["role"] == user.role
    assert data["id"] == user_id


@pytest.mark.anyio
async def test_create_user_with_existing_username(test_app) -> None:
    """Test creating a user with an existing username."""
    user = await create_user(test_app)
    user_data = UserCreate(
        username=user.username,
        email=user.email,
        password="password12345678910",
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
    )
    response = await test_app.post("/auth", json=user_data.model_dump())
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Username already exists"


@pytest.mark.anyio
async def test_create_user_with_existing_email(test_app) -> None:
    """Test creating a user with an existing email."""
    user = await create_user(test_app)
    user_data = UserCreate(
        username="new_test_user",
        email=user.email,
        password="password12345678910",
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
    )
    response = await test_app.post("/auth", json=user_data.model_dump())
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Email already exists"


@pytest.mark.anyio
async def test_update_user(test_app) -> None:
    """Test updating an existing user."""
    user = await create_user(test_app)
    user_id = str(user.id)

    updated_user = UserUpdate(username="updated_test_user")
    response = await test_app.put(f"/auth/{user_id}", json=updated_user.model_dump())
    assert response.status_code == 200
    data = response.json()

    assert UserRead.model_validate(data)
    assert data["username"] == updated_user.username
    assert data["email"] == user.email
    assert data["role"] == user.role
    assert data["id"] == user_id


@pytest.mark.anyio
async def test_delete_user(test_app) -> None:
    """Test deleting an existing user."""
    user = await create_user(test_app)
    user_id = str(user.id)

    response = await test_app.delete(f"/auth/{user_id}")
    assert response.status_code == 204

    result = await test_app.get(f"/auth/{user_id}")
    assert result.status_code == 404
    data = result.json()
    assert data["detail"] == "User not found"
