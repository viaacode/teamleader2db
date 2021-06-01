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



## Testing

Use the makefile to execute the integration and unit tests:
```
$ make test
===================================== test session starts =====================================
platform darwin -- Python 3.8.5, pytest-5.3.5, py-1.10.0, pluggy-0.13.1
rootdir: /Users/wschrep/FreelanceWork/VIAA/teamleader2db
plugins: recording-0.11.0, cov-2.8.1, mock-3.5.1
collected 68 items

tests/api/test_api.py .....                                                             [  7%]
tests/integration/test_sync.py .......                                                  [ 17%]
tests/unit/test_app.py ....                                                             [ 23%]
tests/unit/comm/test_companies.py ......                                                [ 32%]
tests/unit/comm/test_departments.py ......                                              [ 41%]
tests/unit/comm/test_events.py ......                                                   [ 50%]
tests/unit/comm/test_invoices.py ......                                                 [ 58%]
tests/unit/comm/test_projects.py ......                                                 [ 67%]
tests/unit/comm/test_sqlwrapper.py ...                                                  [ 72%]
tests/unit/comm/test_teamleader_auth.py ......                                          [ 80%]
tests/unit/comm/test_teamleader_client.py .......                                       [ 91%]
tests/unit/comm/test_users.py ......                                                    [100%]

===================================== 68 passed in 1.78s ======================================
```

## Testing code coverage report

The makefile has a nice target called 'coverage' use this to make a testing coverage report.

```
$ make coverage
=================================== test session starts ====================================
platform darwin -- Python 3.8.5, pytest-5.3.5, py-1.10.0, pluggy-0.13.1
rootdir: /Users/wschrep/FreelanceWork/VIAA/teamleader2db
plugins: recording-0.11.0, cov-2.8.1, mock-3.5.1
collected 68 items                                                                         

tests/api/test_api.py .....                                                          [  7%]
tests/integration/test_sync.py .......                                               [ 17%]
tests/unit/test_app.py ....                                                          [ 23%]
tests/unit/comm/test_companies.py ......                                             [ 32%]
tests/unit/comm/test_departments.py ......                                           [ 41%]
tests/unit/comm/test_events.py ......                                                [ 50%]
tests/unit/comm/test_invoices.py ......                                              [ 58%]
tests/unit/comm/test_projects.py ......                                              [ 67%]
tests/unit/comm/test_sqlwrapper.py ...                                               [ 72%]
tests/unit/comm/test_teamleader_auth.py ......                                       [ 80%]
tests/unit/comm/test_teamleader_client.py .......                                    [ 91%]
tests/unit/comm/test_users.py ......                                                 [100%]

---------- coverage: platform darwin, python 3.8.5-final-0 -----------
Name                            Stmts   Miss  Cover
---------------------------------------------------
app/__init__.py                     0      0   100%
app/api/__init__.py                 0      0   100%
app/api/api.py                      5      0   100%
app/api/routers/__init__.py         0      0   100%
app/api/routers/health.py           5      0   100%
app/api/routers/sync.py            32      3    91%
app/app.py                         98      8    92%
app/comm/__init__.py                0      0   100%
app/comm/psql_wrapper.py           21      0   100%
app/comm/teamleader_client.py     123     11    91%
app/models/__init__.py              0      0   100%
app/models/companies.py             8      0   100%
app/models/contacts.py              8      0   100%
app/models/departments.py           8      0   100%
app/models/events.py                8      0   100%
app/models/invoices.py              8      0   100%
app/models/projects.py              8      0   100%
app/models/sync_model.py           37      5    86%
app/models/teamleader_auth.py      29      0   100%
app/models/users.py                 8      0   100%
app/server.py                      12      0   100%
---------------------------------------------------
TOTAL                             418     27    94%
Coverage HTML written to dir htmlcov


==================================== 68 passed in 2.91s ===================================
```





## Auth tokens, expiry and renewal

Teamleader has an original take on oauth2 and its token management system.
Basically you first set up a code to be used here in the KnowledgeGraph integration:
KnowledgeGraph integration https://marketplace.teamleader.eu/be/nl/beheer

More specifically for the qas environment you need to use the client_id and secret here:
https://marketplace.teamleader.eu/be/nl/ontwikkel/integraties/b88413


Whenever you save here it invalidates the refresh_token and any backend using it must update it's
refresh token using an auth callback method. Basically you supply a code + secret and a callback will be made to a public https url with the actual token you need later on.


In this administration page it is crutial to have a https public url that you can monitor as this is used to have a callback that gives you a code to be able to fetch a refresh token.
Right now for qas&prd we've set up this path:
https://teamleader.sitweb.eu/oauth

Ideally this application has a public route and then a path on this api can be used.
It's already implemented here:
```
http://localhost:8080/sync/oauth is the route and an example follows below.
```
Basically you pass a code and some defined state (shared secret) on this route. Teamleader calls
this route and passes a code you can use later on.
We save this code in shared.tl_authorization table on our database and from there on if a 401 or 403 response is found the refresh token calls are made automatically and the auth_token and refresh_token are updated in the database.


To initially bootstrap your 'code' or whenever the refresh_token is invalid and code is expired you will see this in the logs:

```
Error 400: {"errors":[{"code":8,"title":"The refresh token is invalid.","status":400,"meta":{"type":"invalid_request","hint":"Token has been revoked"}}]} in handle_token_response

Login into teamleader and paste code callback link in browser: https://app.teamleader.eu/oauth2/authorize?client_id=75bd9426f541ea9be95142476c458023&response_type=code&redirect_uri=https://teamleader.sitweb.eu/oauth&state=qas_secret_state
```

This means you need to login into teamleader.eu with an admin account and then paste the following link in your browser. Then the teamleader server will make a call to the redirect_uri specified which must match the one specified on the integration page and here you will see the code that is passed.



## Authorization code callback example:
So let's say you pasted the above callback link in browser and got back a code. You can then use this on your local server either by inserting it into the config.yml or by making the following request:

```
curl http://localhost:8080/sync/oauth\?code\=def502004de7b8367bdc6acb4427289394a02afa62c23304f14a37df3abd15593c4dfc625c65bf3acb2c20fc00e968ea240fa69f0747808cb0598bd7b9d5fe6ed579027017d8494e8afc9a6fc10460663605ba6ecedd308801c8130ca8e8deca7c6aaf762cdc663f4414244fbde58d9cd047dba7e71d9e3a0dd6d1b95c626a1cb27d71e6c687056f75dfe1593b518450301a327cfb51f5ed3646e98a51b47b4d3785e1a9108d2df00573d67e91e4406ace80c5e608bba1bdd84e7c34f74ecf017fbf5628ffd45760d3aaad52c32f5d2e44fbd977f0b1796c08d2efe72e07a1d3012f4a00af624eaf37212cd56edaa6600428ecaa106259a29c275a53922cf0e3fc03faf122073b2ed3ff870636f3e5baeae37b7c7738fa2d8a3e0a03951bf8c9b22984b5335ae77cc122540ea1956a922ec38adf9c33deb383ccac6b560b4e53ccb83b90e22422134ded9cc327c20a7daffad6cff1e1590d78314caeadf3c9fbbf45a54417568d0a38a88732d7438799c207fa4d35de28fae8051f0776a628ed5da22d6ae84df828ed5622a5847bce921e29\&state\=somesecrethere
```

response will be:
```
code accepted
```
Or rejected if something was wrong. After this the code, token, refresh_token are stored in db. And also after this the code will be invalid again (only useable once).


This now updated the code, token and refresh_token in database. And from now on everything keeps working again. If a token expires the refresh_token is automatically used (and here is where teamleader is different from classic oauth2, the refresh_token is only useable once).

# Detailed teamleader authorization flow
With the refresh token you fetch an actual auth token to be used in further calls. And whenever you do this
the refresh_token itself is updated to a new one that you will need to store in the db for later use (in case pod restarts or for a later sync call when the auth_token is expired).

It's this last part that messes up if for instance you decide you have 2 pods or multiple instances running this flow of execution.
Once the first client refreshes its auth token the refresh token is invalidated for all the others. And in this case you can either copy a valid auth_token or do the above described callback to get a new code to request an entirely new and valid refresh_token.



