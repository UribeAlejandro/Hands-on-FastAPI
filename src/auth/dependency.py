from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repository import AuthRepository
from src.auth.service import AuthService
from src.common.database import get_db


async def get_auth_repository(session: AsyncSession = Depends(get_db)) -> AuthRepository:
    """
    Get an Auth repository.

    Parameters
    ----------
    session : AsyncSession
        The database session to use for the repository.

    Returns
    -------
    AuthRepository
        An Auth repository instance.
    """
    return AuthRepository(session)


async def get_auth_service(repository: AuthRepository = Depends(get_auth_repository)) -> AuthService:
    """
    Get an Auth service.

    Parameters
    ----------
    repository : AuthRepository
        The Auth repository to use for the service.

    Returns
    -------
    AuthService
        An Auth service instance.
    """
    return AuthService(repository)
