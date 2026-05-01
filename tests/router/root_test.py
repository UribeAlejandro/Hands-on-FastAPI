def test_root(test_app) -> None:
    """Test the root endpoint of the FastAPI application."""
    response = test_app.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_health(test_app) -> None:
    """Test the health endpoint of the FastAPI application."""
    response = test_app.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
