from fastapi import APIRouter

from src.auth.jwt.router import router as jwt_router
from src.auth.users.router import router as users_router

router = APIRouter(prefix="")

router.include_router(jwt_router)
router.include_router(users_router)
