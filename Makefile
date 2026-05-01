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

.PHONY: test
test:			## Run the tests
	@echo "Running tests"
	uv run pytest tests

.PHONY: test-docker
test-docker:		## Run the tests in a Docker container
	@echo "Building Docker image"
	docker compose build
	@echo "Running tests in Docker container"
	docker compose run --rm template uv run pytest tests
