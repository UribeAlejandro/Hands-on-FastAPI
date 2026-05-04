from enum import StrEnum

from pydantic import Field
from pydantic_settings import BaseSettings


class Environment(StrEnum):
    """Application runtime environments."""

    local = "local"
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


settings = AppSettings()  # ty: ignore[missing-argument]
