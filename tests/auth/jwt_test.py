import pytest

from tests.conftest import create_user
from tests.constants import USER


@pytest.mark.anyio
async def test_login_non_existent_user(test_app) -> None:
    """Test logging in with a non-existent user."""
    response = await test_app.post("/auth/jwt/login", data={"username": "non_existent_user", "password": "password"})

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid username or password"


@pytest.mark.anyio
async def test_login_user_with_wrong_password(test_app) -> None:
    """Test logging in with a wrong password."""
    user = await create_user(test_app)
    response = await test_app.post("/auth/jwt/login", data={"username": user.username, "password": "wrong_password"})

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid username or password"


@pytest.mark.anyio
async def test_login_user(test_app) -> None:
    """Test logging in with a valid user."""
    user = await create_user(test_app)
    response = await test_app.post("/auth/jwt/login", data={"username": user.username, "password": USER["password"]})

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
