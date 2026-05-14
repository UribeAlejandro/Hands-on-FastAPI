from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.jwt.dependency import get_auth_service
from src.auth.jwt.service import AuthService
from src.auth.schemas import Token
from src.common.exceptions import (
    InvalidCredentialsException,
    UserNotFoundException,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/jwt/login", status_code=status.HTTP_200_OK, response_model=Token)
async def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    """
    Authenticate a user and return a JWT token.

    Returns
    -------
    str
        A JWT token if authentication is successful.
    """
    try:
        _token = await service.authenticate_user(form_data.username, form_data.password)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    except InvalidCredentialsException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    else:
        return _token
