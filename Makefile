NAME := ldap2db
FOLDERS := ./app/ ./tests/

.DEFAULT_GOAL := help


.PHONY: help
help:
	@echo "Available make commands:"
	@echo ""
	@echo "  install     install packages and prepare environment"
	@echo "  clean       remove all temporary files"
	@echo "  lint        run the code linters"
	@echo "  format      reformat code"
	@echo "  test        run all the tests"
	@echo "  dockertest  run all the tests in docker image like jenkins"
	@echo "  coverage    run tests and generate coverage report"
	@echo "  sync        start Teamleader sync directly"
	@echo "  server      start uvicorn development server fast-api for synchronizing with ldap"
	@echo ""


.PHONY: install
install:
	mkdir -p python_env; \
	python3 -m venv python_env; \
	. python_env/bin/activate; \
	python3 -m pip install --upgrade pip; \
	python3 -m pip install -r requirements.txt; \
	python3 -m pip install -r requirements-test.txt


.PHONY: clean
clean:
	find . -type d -name "__pycache__" | xargs rm -rf {}; \
	rm -rf .coverage htmlcov


.PHONY: lint
lint:
	@. python_env/bin/activate; \
	flake8 --max-line-length=120 --exclude=.git,python_env,__pycache__


.PHONY: format
format:
	@. python_env/bin/activate; \
	autopep8 --in-place -r app; \
	autopep8 --in-place -r tests;

.PHONY: test
test:
	@. python_env/bin/activate; \
	cp config.yml.tst config.yml && \
	python -m pytest


.PHONY: dockertest
dockertest:
	docker build . -t ldap2db; \
	docker container run --name ldap2db --env-file .env.example --entrypoint python "ldap2db" "-m" "pytest"


.PHONY: coverage
coverage:
	@. python_env/bin/activate; \
	python -m pytest --cov-config=.coveragerc --cov . .  --cov-report html --cov-report term


.PHONY: sync 
sync:
	. python_env/bin/activate; \
	python -m app.app teamleader-sync

.PHONY: code_callback_example
code_callback_example:
	curl "http://localhost:8080/sync/oauth?code=CODE_HERE&state=qas_secret_state"


.PHONY: server
server:
	. python_env/bin/activate; \
	uvicorn app.server:app --reload --port 8080 --no-access-log --reload-dir app


