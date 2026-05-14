from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.users.repository import UsersRepository
from src.auth.users.service import UsersService
from src.common.database import get_db


async def get_users_repository(session: Annotated[AsyncSession, Depends(get_db)]) -> UsersRepository:
    """
    Get an Auth repository.

    Parameters
    ----------
    session : AsyncSession
        The database session to use for the repository.

    Returns
    -------
    UsersRepository
        An Auth repository instance.
    """
    return UsersRepository(session)


async def get_users_service(repository: Annotated[UsersRepository, Depends(get_users_repository)]) -> UsersService:
    """
    Get an Auth service.

    Parameters
    ----------
    repository : UsersRepository
        The Auth repository to use for the service.

    Returns
    -------
    UsersService
        An Auth service instance.
    """
    return UsersService(repository)
