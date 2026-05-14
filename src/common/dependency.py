from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from src.auth.models import UserRead
from src.auth.users.dependency import get_users_service
from src.auth.users.service import UsersService
from src.common.config import settings


async def get_bearer_token(token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="/auth/jwt/login"))]) -> str:
    """
    Get the bearer token from the request.

    Parameters
    ----------
    token : str
        The bearer token from the request.

    Returns
    -------
    str
        The bearer token.
    """
    return token


async def get_current_user(
    token: Annotated[str, Depends(get_bearer_token)], service: Annotated[UsersService, Depends(get_users_service)]
) -> UserRead | None:
    """
    Get the current user from the bearer token.

    Returns
    -------
    UserRead | None
        The current user.
    """
    try:
        payload = jwt.decode(token, key=settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        username = payload.get("sub")
        user_id = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    else:
        return await service.get_user_by_id(UUID(user_id))
