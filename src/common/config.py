from enum import StrEnum

from pydantic import Field
from pydantic_settings import BaseSettings


class Environment(StrEnum):
    """Application runtime environments."""

    local = "local"
    ci = "ci"
    dev = "dev"
    live = "live"


class AppSettings(BaseSettings):
    """Configuration settings for the application."""

    environment: Environment = Field(..., alias="ENVIRONMENT")
    debug: bool
    project_name: str
    version: str
    description: str

    # Database settings
    echo_sql: bool
    database_url: str

    # JWT settings
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_expires_delta_hours: int = 24


settings = AppSettings()
