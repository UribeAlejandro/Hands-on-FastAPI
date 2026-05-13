# Hands On FastAPI

## Keywords

- FastAPI
- Python
- Docker
- Test Containers
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- AsyncIO
- Dependency Injection
- RESTful API
- CRUD Operations
- Swagger UI
- UV
- Pytest
- CI/CD
- GitHub Actions


This repository contains a hands-on tutorial for building a TODO application using FastAPI. It covers the basics of FastAPI, including how to create endpoints, handle requests and responses, dependency injection, and more.

### Getting Started

To get started, install:

- [uv](https://docs.astral.sh/uv/).
- [Docker](https://www.docker.com/).
- [Docker Compose](https://docs.docker.com/compose/).

### Environment Setup

Create a `.env` file in the root of the project with the following command:

```bash
cp .env.template .env
```

> Modify the `.env` file with your own values if necessary.

### Running the Application

To run the application, use the following command:

```bash
make run
```

This will start the FastAPI application using a SQLite database. You can access the API documentation at `http://localhost:8000/docs`.

### Running Tests

To run the tests, use the following command:

```bash
make test
```

This will run the tests using pytest, and it will use a test-containers PostgreSQL database for testing. Refer to [.env.template](.env.template) file for test-containers variables according to your docker configuration and emulator.


## Docker image

To build the Docker image for `Production` environment, use the following command:

```bash
make build-docker
```
