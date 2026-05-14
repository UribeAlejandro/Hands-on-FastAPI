import uuid

import pytest

from src.auth.models import UserCreate, UserRead, UserUpdate
from tests.conftest import auth_header, create_user, login_user
from tests.constants import USER


@pytest.mark.anyio
async def test_get_non_existent_user_by_id(test_app) -> None:
    """Test retrieving a non-existent user by their ID."""
    _uuid = uuid.uuid4()
    response = await test_app.get(f"/users/{str(_uuid)}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"


@pytest.mark.anyio
async def test_update_non_existent_user_by_id(test_app) -> None:
    """Test updating a non-existent user by their ID."""
    _uuid = uuid.uuid4()
    updated_user = UserUpdate(username="updated_test_user")
    response = await test_app.put(f"/users/{str(_uuid)}", json=updated_user.model_dump())
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"


@pytest.mark.anyio
async def test_delete_non_existent_user_by_id(test_app) -> None:
    """Test deleting a non-existent user by their ID."""
    _uuid = uuid.uuid4()
    response = await test_app.delete(f"/users/{str(_uuid)}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"


@pytest.mark.anyio
async def test_create_user(test_app) -> None:
    """Test the creation of a new user."""
    user = await create_user(test_app)
    user_id = str(user.id)

    response = await test_app.get(f"/users/{user_id}")
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
    response = await test_app.post("/users/register", json=user_data.model_dump())
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
    response = await test_app.post("/users/register", json=user_data.model_dump())
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Email already exists"


@pytest.mark.anyio
async def test_update_user(test_app) -> None:
    """Test updating an existing user."""
    user = await create_user(test_app)
    user_id = str(user.id)

    updated_user = UserUpdate(username="updated_test_user")
    response = await test_app.put(f"/users/{user_id}", json=updated_user.model_dump())
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

    response = await test_app.delete(f"/users/{user_id}")
    assert response.status_code == 204

    result = await test_app.get(f"/users/{user_id}")
    assert result.status_code == 404
    data = result.json()
    assert data["detail"] == "User not found"


@pytest.mark.anyio
async def test_get_current_authenticated_user(test_app) -> None:
    """Test retrieving the current authenticated user."""
    user = await create_user(test_app)
    access_token = await login_user(test_app, user.username, USER["password"])

    auth_headers = auth_header(access_token)
    response = await test_app.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert UserRead.model_validate(data)
    assert data["username"] == user.username
    assert data["email"] == user.email
    assert data["role"] == user.role
    assert data["id"] == str(user.id)
