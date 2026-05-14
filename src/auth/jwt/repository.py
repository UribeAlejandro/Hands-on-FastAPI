from datetime import UTC, datetime, timedelta

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.auth.models import User, UserRead
from src.auth.schemas import Token
from src.common.config import settings
from src.common.exceptions import (
    InvalidCredentialsException,
    UserNotFoundException,
)


class AuthRepository:
    """Repository for managing authentication-related operations in the database."""

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
