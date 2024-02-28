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

.PHONY: metrics-motormongo
metrics-motormongo:
	poetry run uvicorn metrics.motormongo.main:app --port 8000 &
	UVICORN_PID=$$!; \
	sleep 15; \
	poetry run locust -f metrics/locustfile.py --host http://127.0.0.1:8000 --headless -u 10 -r 1 -t 30s; \
	sleep 20; \
	kill $$UVICORN_PID; \
	open http://localhost:8089

.PHONY: metrics-mongoengine
metrics-mongoengine:
	poetry run uvicorn metrics.mongoengine.main:app --port 8000 &
	UVICORN_PID=$$!; \
	sleep 15; \
	poetry run locust -f metrics/locustfile.py --host http://127.0.0.1:8000 --headless -u 10 -r 1 -t 30s; \
	sleep 20; \
	kill $$UVICORN_PID; \
	open http://localhost:8089

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
	poetry run uvicorn demo.main:app --reload --log-config=./demo/logging.yaml