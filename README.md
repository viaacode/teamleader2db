# Teamleader2Db

Component that syns data from teamleader api into a PostgresQL DB.

## Prerequisites

* Python >= 3.7 (when working locally)
* The package `python3-venv` (when working locally)
* The package `PostgreSQL` (when running integration tests locally)
* PostgreSQL DB with appropriate schema
* Docker (optional)
* Access to the [meemoo PyPi](http://do-prd-mvn-01.do.viaa.be:8081/)

## Used libraries

* `viaa-chassis`
* `psycopg2` - communicates with the PostgreSQL server
* `fastapi` - exposes json api to start deewee and avo sync jobs
* `uvicorn` - ASGI server implementation, using uvloop used for running fastapi server
* `requests` - Teamleader api calls implemented using requests


## Fast-API
We added fast-api to make sync calls and to implement the code callback api call needed
for authorization with teamleader api.

This now exposes an api at http://localhost:8080 with some routes to start sync jobs.
The api is self documented using swagger and you will see the available calls with parameters
when you visit the / route.


There's now a makefile which provides various helper commands:
```
$ make
Available make commands:

  install     install packages and prepare environment
  clean       remove all temporary files
  lint        run the code linters
  format      reformat code
  test        run all the tests
  dockertest  run all the tests in docker image like jenkins
  coverage    run tests and generate coverage report
  sync        start Teamleader sync directly
  server      start uvicorn development server fast-api for synchronizing with ldap
```

For example run the server in dev mode:
```
$ make server
```
Then visit http://localhost:8080 


