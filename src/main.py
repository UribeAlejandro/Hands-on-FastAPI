from fastapi import FastAPI

from src.common.config import settings
from src.common.lifespan import lifespan
from src.common.logger import setup_logger
from src.router.root import router as root_router

setup_logger()

app = FastAPI(
    title=settings.project_name,
    lifespan=lifespan,
    description=settings.description,
    version=settings.version,
    debug=settings.debug,
)
app.include_router(root_router)
