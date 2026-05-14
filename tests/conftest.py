import os
from collections.abc import AsyncGenerator, Generator
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel
from testcontainers.postgres import PostgresContainer

from src.auth.models import UserCreate, UserRead
from src.common.config import settings
from src.common.database import get_db
from src.main import app
from src.todo.models import ToDo, ToDoCreate
from tests.constants import TODO, USER

pytest_plugins = ["anyio"]


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Specifies the AnyIO backend to use for asynchronous tests."""
    return "asyncio"


@pytest.fixture(scope="session")
def database_container() -> Generator[PostgresContainer]:
    """Sets up a PostgreSQL database for testing using Testcontainers."""
    with PostgresContainer("postgres:18-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
async def test_engine(database_container: PostgresContainer) -> AsyncGenerator[AsyncEngine]:
    """Creates an asynchronous engine for testing, using an in-memory SQLite database."""
    url = database_container.get_connection_url().replace("postgresql+psycopg2", "postgresql+asyncpg")
    os.environ["TEST_DATABASE_URL"] = url
    engine = create_async_engine(
        url,
        poolclass=NullPool,
        echo=settings.echo_sql,
    )
    yield engine


@pytest.fixture(scope="session")
async def setup_database(test_engine: AsyncEngine):
    """Sets up the database for testing."""
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
async def test_db_session(test_engine: AsyncEngine, setup_database) -> AsyncGenerator[AsyncSession]:
    """Provides a database session for testing, using a SQLite database."""
    conn = await test_engine.connect()
    trans = await conn.begin()

    test_async_session = async_sessionmaker(
        bind=conn,
        class_=AsyncSession,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    async with test_async_session() as session:
        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()
            await conn.close()


@pytest.fixture
async def test_app(test_db_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    """Provides a TestClient for testing the FastAPI application."""

    async def override_get_db() -> AsyncGenerator[AsyncSession]:
        """Overrides the get_db dependency to use the test database session."""
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


async def create_user(test_app: AsyncClient) -> UserRead:
    """
    Creates a new user for testing.

    Parameters
    ----------
    test_app : AsyncClient
        The test client to use for making requests to the application.

    Returns
    -------
    UserRead
        The created user.
    """
    _user = UserCreate(
        username=USER["username"],
        email=USER["email"],
        password=USER["password"],
        first_name=USER["first_name"],
        last_name=USER["last_name"],
        role=USER["role"],
    )
    response = await test_app.post("/users/register", json=_user.model_dump())
    assert response.status_code == 201, f"Failed to create user: {response.text}"
    return UserRead.model_validate(response.json())


async def create_todo(test_app: AsyncClient, user_id: UUID) -> ToDo:
    """
    Creates a new todo item for testing.

    Parameters
    ----------
    test_app : AsyncClient
        The test client to use for making requests to the application.
    user_id : UUID
        The ID of the user to associate with the todo item.

    Returns
    -------
    ToDo
        The created todo item.
    """
    _todo = ToDoCreate(
        title=TODO["title"],
        description=TODO["description"],
        priority=TODO["priority"],
        user_id=user_id,
    )
    response = await test_app.post("/todo/", json=_todo.model_dump())
    assert response.status_code == 201, f"Failed to create todo: {response.text}"
    return ToDo.model_validate(response.json())


async def login_user(test_app: AsyncClient, username: str, password: str) -> str:
    """
    Logs in a user and returns the access token.

    Parameters
    ----------
    test_app : AsyncClient
        The test client to use for making requests to the application.
    username : str
        The username of the user to log in.
    password : str
        The password of the user to log in.

    Returns
    -------
    str
        The access token for the logged-in user.
    """
    response = await test_app.post(
        "/auth/jwt/login",
        data={"username": username, "password": password},
    )
    data = response.json()
    assert response.status_code == 200, f"Failed to login: {response.text}"
    assert data["token_type"] == "bearer", f"Unexpected token type: {data.get('token_type')}"
    return data["access_token"]


def auth_header(token: str) -> dict[str, str]:
    """
    Creates an authorization header for the given token.

    Parameters
    ----------
    token : str
        The JWT token to include in the authorization header.

    Returns
    -------
    dict[str, str]
        A dictionary containing the authorization header with the provided token.
    """
    return {"Authorization": f"Bearer {token}"}
