.ONESHELL:
ENV_PREFIX=$(shell python -c "if __import__('pathlib').Path('.venv/bin/pip').exists(): print('.venv/bin/')")

.PHONY: help
help:			## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep


.PHONY: install
install:		## Install dependencies
	@echo "Installing Python"
	uv python install 3.14
	@echo "Installing dependencies"
	uv sync --all-groups
	@echo "Installing pre-commit hooks"
	uv run pre-commit install
	@echo "Updating pre-commit hooks"
	uv run pre-commit autoupdate

.PHONY: run
run:			## Run the application
	@echo "Running the application"
	uv run fastapi dev src/main.py

.PHONY: test
test:			## Run the tests
	@echo "Running tests"
	@if [ -f .env ]; then \
		set -a; . .env; set +a; \
	fi; \
	uv run pytest tests

.PHONY: build-docker
build-docker:		## Build the Docker image
	@echo "Building Docker image"
	docker compose build

.PHONY: run-migrations
run-migrations:		## Run database migrations
	@echo "Running database migrations"
	uv run alembic upgrade head
