from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status

from src.auth.models import UserCreate, UserRead, UserUpdate
from src.auth.users.dependency import get_users_service
from src.auth.users.service import UsersService
from src.common.dependency import get_current_user
from src.common.exceptions import (
    UserEmailAlreadyExistsException,
    UserUsernameAlreadyExistsException,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(
    service: Annotated[UsersService, Depends(get_users_service)],
    user: UserCreate = Body(..., description="The user to create"),
) -> UserRead:
    """
    Create a new user.

    Parameters
    ----------
    user : UserCreate
        The user to create.

    Returns
    -------
    UserRead
        The created user.
    """
    try:
        _user = await service.create_user(user)
    except UserUsernameAlreadyExistsException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    except UserEmailAlreadyExistsException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    return _user


@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserRead)
async def get_current_authenticated_user(
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> UserRead:
    """
    Get the current authenticated user.

    Returns
    -------
    UserRead
        The current authenticated user.
    """
    return current_user


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_by_id(
    # user: Annotated[UserRead, Depends(get_current_user)],
    service: Annotated[UsersService, Depends(get_users_service)],
    user_id: UUID = Path(..., description="The ID of the user to retrieve"),
) -> UserRead:
    """
    Get a user by their ID.

    Parameters
    ----------
    user_id : str
        The ID of the user to retrieve.

    Returns
    -------
    UserRead
        The user with the specified ID.
    """
    _user = await service.get_user_by_id(user_id)
    if not _user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return _user


@router.put("/{user_id}", status_code=status.HTTP_200_OK)
async def update_user_by_id(
    # user: Annotated[UserRead, Depends(get_current_user)],
    service: Annotated[UsersService, Depends(get_users_service)],
    user_id: UUID = Path(..., description="The ID of the user to update"),
    user_update: UserUpdate = Body(..., description="The updated user data"),
) -> UserRead:
    """
    Update a user by their ID.

    Parameters
    ----------
    user_id : str
        The ID of the user to update.
    user_update : UserCreate
        The updated user data.

    Returns
    -------
    UserRead
        The updated user.
    """
    _user = await service.update_user(user_id, user_update)
    if not _user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return _user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_id(
    # user: Annotated[UserRead, Depends(get_current_user)],
    service: Annotated[UsersService, Depends(get_users_service)],
    user_id: UUID = Path(..., description="The ID of the user to delete"),
) -> None:
    """
    Delete a user by their ID.

    Parameters
    ----------
    user_id : str
        The ID of the user to delete.
    """
    deleted = await service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
