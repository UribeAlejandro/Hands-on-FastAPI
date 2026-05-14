from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.auth.models import User, UserCreate, UserRead, UserUpdate
from src.auth.schemas import Token
from src.common.config import settings
from src.common.exceptions import (
    InvalidCredentialsException,
    UserEmailAlreadyExistsException,
    UserNotFoundException,
    UserUsernameAlreadyExistsException,
)


class UsersRepository:
    """Repository for managing users in the database."""

    def __init__(self, session: AsyncSession):
        self.session = session

    @property
    def bcrypt_context(self) -> CryptContext:
        """
        Get the bcrypt context for password hashing.

        Returns
        -------
        CryptContext
            The bcrypt context instance.
        """
        return CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    async def __generate_jwt_token(user: UserRead) -> str:
        """
        Generate a JWT token for a user.

        Parameters
        ----------
        user : UserRead
            The user for whom to generate the token.

        Returns
        -------
        str
            The generated JWT token.
        """
        expires_delta = timedelta(hours=settings.jwt_expires_delta_hours)
        username = user.username
        user_id = str(user.id)

        payload = {"sub": username, "id": user_id, "exp": datetime.now(UTC) + expires_delta}
        return jwt.encode(payload, key=settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

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
        email = user_create.email
        username = user_create.username
        # Check if the username already exists
        result = await self.session.execute(select(User).where(User.username == username))
        if result.scalars().first():
            raise UserUsernameAlreadyExistsException(username)
        # Check if the email already exists
        result = await self.session.execute(select(User).where(User.email == email))
        if result.scalars().first():
            raise UserEmailAlreadyExistsException(email)

        _user = User(**user_create.model_dump(), password_hash=self.bcrypt_context.hash(user_create.password))
        self.session.add(_user)
        await self.session.commit()
        await self.session.refresh(_user)
        return UserRead.model_validate(_user)

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
        result = await self.session.get(User, user_id)
        return UserRead.model_validate(result) if result else None

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
        existing_user = await self.session.get(User, user_id)
        if not existing_user:
            return None

        for key, value in user_update.model_dump(exclude_none=True).items():
            setattr(existing_user, key, value)

        self.session.add(existing_user)
        await self.session.commit()
        await self.session.refresh(existing_user)
        return UserRead.model_validate(existing_user)

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
        existing_user = await self.session.get(User, user_id)
        if not existing_user:
            return False

        await self.session.delete(existing_user)
        await self.session.commit()
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
        result = await self.session.execute(select(User).where(User.username == username))
        user = result.scalars().first()

        if not user:
            raise UserNotFoundException(username)

        if not self.bcrypt_context.verify(password, user.password_hash):
            raise InvalidCredentialsException()

        _token = Token(access_token=await self.__generate_jwt_token(UserRead.model_validate(user)))
        return _token
