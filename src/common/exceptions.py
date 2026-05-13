class UserEmailAlreadyExistsException(Exception):
    """Exception raised when a user with the same email already exists in the database."""

    def __init__(self, email: str):
        self.email = email
        super().__init__(f"An user with email '{email}' already exists.")


class UserUsernameAlreadyExistsException(Exception):
    """Exception raised when a user with the same username already exists in the database."""

    def __init__(self, username: str):
        self.username = username
        super().__init__(f"An user with username '{username}' already exists.")


class UserNotFoundException(Exception):
    """Exception raised when a user is not found in the database."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        super().__init__(f"User with id '{user_id}' not found.")
