.PHONY: instalar formato formato-check lint test check

instalar:
	uv sync

formato:
	uv run ruff format .

formato-check:
	uv run ruff format --check .

lint:
	uv run ruff check .

test:
	uv run pytest

check: formato-check lint test
