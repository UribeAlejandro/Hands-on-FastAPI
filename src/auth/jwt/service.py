from src.auth.jwt.repository import AuthRepository
from src.auth.schemas import Token


class AuthService:
    """Service layer for authentication-related operations."""

    def __init__(self, repository: AuthRepository):
        self.repository = repository

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
