from uuid import UUID

from src.auth.models import UserCreate, UserRead, UserUpdate
from src.auth.schemas import Token
from src.auth.users.repository import UsersRepository


class UsersService:
    """Service layer for user-related operations."""

    def __init__(self, repository: UsersRepository):
        self.repository = repository

    async def create_user(self, user_create: UserCreate) -> UserRead:
        """
        Create a new user in the database.

        Parameters
        ----------
        user_create : UserCreate
            The user data to create.

        Returns
        -------
        UserRead
            The created user.
        """
        return await self.repository.create_user(user_create)

    async def get_user_by_id(self, user_id: UUID) -> UserRead | None:
        """
        Get a user by their ID.

        Parameters
        ----------
        user_id : UUID
            The ID of the user to retrieve.

        Returns
        -------
        UserRead | None
            The user with the specified ID, or None if not found.
        """
        return await self.repository.get_user_by_id(user_id)

    async def update_user(self, user_id: UUID, user_update: UserUpdate) -> UserRead | None:
        """
        Update a user by their ID.

        Parameters
        ----------
        user_id : UUID
            The ID of the user to update.
        user_update : UserUpdate
            The updated user data.

        Returns
        -------
        UserRead | None
            The updated user, or None if not found.
        """
        existing_user = await self.repository.get_user_by_id(user_id)
        if not existing_user:
            return None
        return await self.repository.update_user(user_id, user_update)

    async def delete_user(self, user_id: UUID) -> bool:
        """
        Delete a user by their ID.

        Parameters
        ----------
        user_id : UUID
            The ID of the user to delete.

        Returns
        -------
        bool
            True if the user was deleted, False if not found.
        """
        existing_user = await self.repository.get_user_by_id(user_id)
        if not existing_user:
            return False
        await self.repository.delete_user(user_id)
        return True

    async def authenticate_user(self, username: str, password: str) -> Token:
        """
        Authenticate a user by their username and password.

        Parameters
        ----------
        username : str
            The username of the user to authenticate.
        password : str
            The password of the user to authenticate.

        Returns
        -------
        Token

        """
        return await self.repository.authenticate_user(username, password)
