from typing import Any

import pytest
from pydantic import ValidationError

from src.common.config import AppSettings, Environment

ENV_NAMES = [
    "ENVIRONMENT",
    "DEBUG",
    "PROJECT_NAME",
    "VERSION",
    "DESCRIPTION",
    "ECHO_SQL",
    "DATABASE_URL",
    "JWT_SECRET_KEY",
    "JWT_ALGORITHM",
    "JWT_EXPIRES_DELTA_HOURS",
]

VALUES: dict[str, Any] = {
    "ENVIRONMENT": "local",
    "debug": False,
    "project_name": "demo",
    "version": "0.0.1",
    "description": "demo app",
    "echo_sql": False,
    "database_url": "postgresql+asyncpg://user:pw@localhost/db",
    "jwt_secret_key": "dummy-secret",
    "jwt_algorithm": "HS256",
}


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove settings-related env vars so each test controls its own inputs."""
    for name in ENV_NAMES:
        monkeypatch.delenv(name, raising=False)


def build(**overrides: Any) -> AppSettings:
    """Construct AppSettings from explicit values, without reading any dotenv file."""
    values = {**VALUES, **overrides}
    return AppSettings(**values)


class TestEnvironment:
    """Tests for the Environment enum."""

    def test_values(self) -> None:
        """Test the enum members and values."""
        assert {e.name: e.value for e in Environment} == {
            "local": "local",
            "ci": "ci",
            "dev": "dev",
            "live": "live",
        }

    @pytest.mark.parametrize("value", ["local", "ci", "dev", "live"])
    def test_from_value(self, value: str) -> None:
        """Test lookup by value."""
        assert Environment(value) == value

    def test_invalid(self) -> None:
        """Test that an unknown environment raises ValueError."""
        with pytest.raises(ValueError):
            Environment("prod")


class TestAppSettings:
    """Tests for AppSettings."""

    def test_explicit_values(self) -> None:
        """Test construction from explicit values."""
        settings = build()

        assert settings.environment is Environment.local
        assert settings.project_name == "demo"
        assert settings.database_url.startswith("postgresql+asyncpg://")
        assert settings.jwt_algorithm == "HS256"

    def test_jwt_expires_default(self) -> None:
        """Test that jwt_expires_delta_hours defaults to 24."""
        assert build().jwt_expires_delta_hours == 24

    def test_jwt_expires_override(self) -> None:
        """Test overriding jwt_expires_delta_hours."""
        assert build(jwt_expires_delta_hours=2).jwt_expires_delta_hours == 2

    @pytest.mark.parametrize("env", ["local", "ci", "dev", "live"])
    def test_environment_values(self, env: str) -> None:
        """Test that each environment value is accepted."""
        assert build(ENVIRONMENT=env).environment == Environment(env)

    def test_invalid_environment(self) -> None:
        """Test that an unknown environment fails."""
        with pytest.raises(ValidationError):
            build(ENVIRONMENT="prod")

    @pytest.mark.parametrize(
        "missing",
        [
            "ENVIRONMENT",
            "debug",
            "project_name",
            "version",
            "description",
            "echo_sql",
            "database_url",
            "jwt_secret_key",
            "jwt_algorithm",
        ],
    )
    def test_required_fields(self, missing: str) -> None:
        """Test that each required field raises when absent."""
        values = {k: v for k, v in VALUES.items() if k != missing}

        with pytest.raises(ValidationError) as exc_info:
            AppSettings(**values)

        assert len(exc_info.value.errors()) == 1
        assert exc_info.value.errors()[0]["type"] == "missing"

    def test_no_values_reports_all_required(self) -> None:
        """Test that an empty environment reports every required field."""
        with pytest.raises(ValidationError) as exc_info:
            AppSettings()

        assert len(exc_info.value.errors()) == 9

    def test_reads_environment_variables(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that settings load from environment variables, case-insensitively."""
        env = {
            "ENVIRONMENT": "ci",
            "DEBUG": "true",
            "PROJECT_NAME": "from-env",
            "VERSION": "1.2.3",
            "DESCRIPTION": "d",
            "ECHO_SQL": "1",
            "DATABASE_URL": "postgresql+asyncpg://u:p@h/db",
            "JWT_SECRET_KEY": "dummy",
            "JWT_ALGORITHM": "HS512",
            "JWT_EXPIRES_DELTA_HOURS": "6",
        }
        for key, value in env.items():
            monkeypatch.setenv(key, value)

        settings = AppSettings()

        assert settings.environment is Environment.ci
        assert settings.debug is True
        assert settings.echo_sql is True
        assert settings.project_name == "from-env"
        assert settings.jwt_expires_delta_hours == 6

    @pytest.mark.parametrize(("raw", "expected"), [("true", True), ("false", False), ("1", True), ("0", False)])
    def test_bool_coercion(self, raw: str, expected: bool) -> None:
        """Test coercion of boolean strings."""
        assert build(debug=raw).debug is expected

    def test_invalid_bool(self) -> None:
        """Test that a non-boolean debug value fails."""
        with pytest.raises(ValidationError):
            build(debug="maybe")

    def test_invalid_hours(self) -> None:
        """Test that a non-integer jwt_expires_delta_hours fails."""
        with pytest.raises(ValidationError):
            build(jwt_expires_delta_hours="soon")

    def test_environment_accepted_by_field_name(self) -> None:
        """Document that environment can be passed by field name as well as by its ENVIRONMENT alias."""
        values = {k: v for k, v in VALUES.items() if k != "ENVIRONMENT"}

        assert AppSettings(environment="dev", **values).environment is Environment.dev
