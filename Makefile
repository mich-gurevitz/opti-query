lint:
	pre-commit run ruff-format --all-files

install:
	pip install -e .

install-dev:
	pip install .[dev]
