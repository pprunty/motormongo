.PHONY: install
install:
	poetry install

.PHONY: install-pre-commit
install-pre-commit:
	poetry run pre-commit uninstall; poetry run pre-commit install

.PHONY: lint
lint:
	poetry run flake8 motormongo

.PHONY: lint-fix
lint-fix:
	poetry run black motormongo

.PHONY: check-sort
check-sort:
	 poetry run isort motormongo/ --check-only

.PHONY: sort
sort:
	 poetry run isort motormongo/

.PHONY: test
test:
	poetry run pytest

.PHONY: test-cov
test-cov:
	poetry run pytest --cov=motormongo

.PHONY: pre-commit-install
pre-commit-install:
	poetry run pre-commit install

.PHONY: pre-commit
pre-commit:
	poetry run pre-commit run --all-files

.PHONY: test-cov-report
test-cov-report:
	poetry run pytest --cov=motormongo --cov-report=xml:coverage.xml

.PHONY: demo
demo:
	export DEBUG_MODE=true
	poetry run uvicorn demo.main:app --reload