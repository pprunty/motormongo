.PHONY: install
install:
	poetry install

.PHONY: install-pre-commit
install-pre-commit:
	poetry run pre-commit uninstall; poetry run pre-commit install

#.PHONY: lint
#lint:
#	poetry run pre-commit run --all-files
#
#.PHONY: lint
#lint:
#	cd motormongo && poetry run pre-commit run --all-files

.PHONY: run
run:
	poetry run uvicorn motormongo.main:app --reload  --log-config=motormongo/logging.yaml

.PHONY: demo
demo:
	poetry run uvicorn demo.main:app --reload