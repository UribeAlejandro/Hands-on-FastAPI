from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture(scope="module")
def test_app() -> Generator[TestClient]:
    """Provides a TestClient for testing the FastAPI application."""
    client = TestClient(app)
    yield client
