.PHONY: install
install:
	poetry install

.PHONY: install-pre-commit
install-pre-commit:
	poetry run pre-commit uninstall; poetry run pre-commit install

.PHONY: lint
lint:
	poetry run flake8

.PHONY: lint-fix
lint-fix:
	poetry run black motormongo

.PHONY: sort
sort:
	 poetry run isort motormongo/

.PHONY: demo
demo:
	poetry run uvicorn demo.main:app --reload