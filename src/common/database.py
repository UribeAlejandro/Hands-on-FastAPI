from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.common.config import settings

async_engine = create_async_engine(
    settings.database_url,
    echo=settings.echo_sql,
    future=True,
)

async_session = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession]:
    """Get a database session."""
    async with async_session() as session:
        yield session
