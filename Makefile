PYTHON := uv run

.PHONY: sync lint format typecheck test eval ui

sync:
	uv sync --all-extras

lint:
	$(PYTHON) ruff check .

format:
	$(PYTHON) ruff format .

typecheck:
	$(PYTHON) ty check

test:
	$(PYTHON) pytest

eval:
	$(PYTHON) maestro eval

ui:
	cd ui && npm install && npm run dev

