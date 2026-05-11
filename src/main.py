from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from src.common.config import settings
from src.common.database import async_engine
from src.common.logger import setup_logger
from src.common.router import router as root_router
from src.todo.router import router as todo_router

setup_logger()

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator:
    """Lifespan context manager for FastAPI application."""
    logger.info("Starting up...")
    logger.info(
        "Database Connection",
        dialect=async_engine.dialect.name,
        driver=async_engine.driver,
        echo=async_engine.echo,
    )

    logger.info("Startup finished.")
    yield
    logger.info("Shutting down...")
    await async_engine.dispose()
    logger.info("Shutdown finished.")


app = FastAPI(
    title=settings.project_name,
    lifespan=lifespan,
    description=settings.description,
    version=settings.version,
    debug=settings.debug,
)
app.include_router(root_router)
app.include_router(todo_router)
