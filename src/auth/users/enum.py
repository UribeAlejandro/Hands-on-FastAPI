from enum import StrEnum


class UserRole(StrEnum):
    """Enum representing user roles in the system."""

    ADMIN = "admin"
    USER = "user"
