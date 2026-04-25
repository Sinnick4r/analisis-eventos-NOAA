.PHONY: instalar formato lint test check

instalar:
	uv sync

formato:
	uv run ruff format .

lint:
	uv run ruff check .

test:
	uv run pytest

check: lint test
