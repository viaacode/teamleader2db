.ONESHELL:
SHELL = /bin/sh

.PHONY: all test

test:
	export $(shell cat .env.example | xargs)
	cp ./config.yml.example ./config.yml
	apk add --no-cache postgresql-dev gcc musl-dev postgresql
	pip install -r requirements.txt --extra-index-url http://do-prd-mvn-01.do.viaa.be:8081/repository/pypi-all/simple --trusted-host do-prd-mvn-01.do.viaa.be
	pip install -r requirements-test.txt
	python -m pytest -vvv "--cov=./app" "--junit-xml=./tests/test_results.xml"