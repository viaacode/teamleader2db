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
* `argh` - Command line parsing for CLI sync calls
* `requests` - Teamleader api calls with oauth2 are implemented using requests


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



## Authorization code callback example:
```
curl http://localhost:8080/sync/oauth\?code\=def502004de7b8367bdc6acb4427289394a02afa62c23304f14a37df3abd15593c4dfc625c65bf3acb2c20fc00e968ea240fa69f0747808cb0598bd7b9d5fe6ed579027017d8494e8afc9a6fc10460663605ba6ecedd308801c8130ca8e8deca7c6aaf762cdc663f4414244fbde58d9cd047dba7e71d9e3a0dd6d1b95c626a1cb27d71e6c687056f75dfe1593b518450301a327cfb51f5ed3646e98a51b47b4d3785e1a9108d2df00573d67e91e4406ace80c5e608bba1bdd84e7c34f74ecf017fbf5628ffd45760d3aaad52c32f5d2e44fbd977f0b1796c08d2efe72e07a1d3012f4a00af624eaf37212cd56edaa6600428ecaa106259a29c275a53922cf0e3fc03faf122073b2ed3ff870636f3e5baeae37b7c7738fa2d8a3e0a03951bf8c9b22984b5335ae77cc122540ea1956a922ec38adf9c33deb383ccac6b560b4e53ccb83b90e22422134ded9cc327c20a7daffad6cff1e1590d78314caeadf3c9fbbf45a54417568d0a38a88732d7438799c207fa4d35de28fae8051f0776a628ed5da22d6ae84df828ed5622a5847bce921e29\&state\=somesecrethere
```

response will be:
```
code accepted
```
Or rejected if something was wrong. After this the code, token, refresh_token are stored in db. And also after this the code will be invalid again (only useable once).

## TODOS

Write unit tests, integration tests, more documentation on cli usage etc.
Especially further explain the code callback which is needed whenever a refresh_token fails. The regular token expiry using valid refresh token works completely now however.
Reasons a refresh_token can become invalid are when we make changes in teamleader page for KnowledgeGraph integration https://marketplace.teamleader.eu/be/nl/beheer


