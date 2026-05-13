# Install uv
FROM ghcr.io/astral-sh/uv:python3.14-bookworm AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

# Change the working directory to the `app` directory
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-install-project --no-dev

# Copy the project into the intermediate image
COPY src /app/src
#COPY tests /app/tests
# COPY migrations /app/migrations
# COPY alembic.ini /app/alembic.ini

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked

FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

# Copy the environment, but not the source code
COPY --from=builder --chown=app:app /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Run the application
#Get env var for PORT
CMD ["fastapi", "run", "--workers", "2", "--host", "0.0.0.0", "--port", "8080", "src/main.py"]
