import os
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel

from src.common.config import Environment, settings
from src.common.database import get_db
from src.main import app

pytest_plugins = ["anyio"]

if settings.environment == Environment.local:
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./database/test.db"


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Specifies the AnyIO backend to use for asynchronous tests."""
    return "asyncio"


@pytest.fixture(scope="session")
def test_engine() -> AsyncEngine:
    """Creates an asynchronous engine for testing, using an in-memory SQLite database."""
    engine = create_async_engine(
        os.environ["DATABASE_URL"],
        poolclass=NullPool,
        echo=settings.echo_sql,
    )
    return engine


@pytest.fixture(scope="session")
async def setup_database(test_engine):
    """Sets up the database for testing."""
    if settings.environment == Environment.local:
        async with test_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    yield

    if settings.environment == Environment.local:
        async with test_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)

    await test_engine.dispose()


@pytest.fixture
async def test_db_session(test_engine, setup_database) -> AsyncGenerator[AsyncSession]:
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
