# ldap2db
Component that one-way syncs data from LDAP to a PostgreSQL DB. This allows for reporting further downstream.

The app is designed to sync changed (new/updated) LDAP entries to the PostgreSQL DB based on the `modifyTimestamp` attribute from LDAP. The identifying key between the two systems is the LDAP attribute `EntryUUID`.

Do note that the service is not able to handle deletes. A full load from LDAP can be achieved if the target database table is empty. So in case of known deleted LDAP entries that should reflect in the database, this mechanism can be used to "sync" up.


## Prerequisites

* Python >= 3.7 (when working locally)
* The package `python3-venv` (when working locally)
* The package `PostgreSQL` (when running integration tests locally)
* LDAP Server with appropriate structure
* PostgreSQL DB with appropriate schema
* Docker (optional)
* Access to the [meemoo PyPi](http://do-prd-mvn-01.do.viaa.be:8081/)

## Used libraries

* `viaa-chassis`
* `ldap3` - communicates with the LDAP server
* `psycopg2` - communicates with the PostgreSQL server
* `fastapi` - exposes json api to start deewee and avo sync jobs
* `uvicorn` - ASGI server implementation, using uvloop used for running fastapi server


## Fast-API
We added fast-api and some routes to the application afterwards.
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
  avosync     start AVO ldap synchronize job directly from command line
  deeweesync  start DEEWEE ldap synchronize job directly from command line
  server      start uvicorn development server fast-api for synchronizing with ldap
```

For example run the server in dev mode:
```
$ make server
```
Then visit http://localhost:8080 


For docker and running in production you do:
```
$ python main.py
```

The cli version is also still available with a -h to show commandline usage:
```
$ python -m app.app -h
usage: app.py [-h] {avo-status,avo-sync-job,deewee-status,deewee-sync-job} ...

positional arguments:
  {avo-status,avo-sync-job,deewee-status,deewee-sync-job}
    avo-status
    avo-sync-job
    deewee-status
    deewee-sync-job

optional arguments:
  -h, --help            show this help message and exit

```

Calling without params shows usage. you can either supply avo-sync-job or deewee-sync-job.
And for each you can also pass the -f or --full-sync flag to force a full sync and without the flag
you get a regular delta/daily sync.

```
$ python -m app.app avo-sync-job -h
usage: app.py avo-sync-job [-h] [-f]

optional arguments:
  -h, --help       show this help message and exit
  -f, --full-sync  False
```

Help for deewee-sync-job is verry similar:
```
$ python -m app.app deewee-sync-job -h
usage: app.py deewee-sync-job [-h] [-f]

optional arguments:
  -h, --help       show this help message and exit
  -f, --full-sync  False

```

Running avo delta job:
```
$ python -m app.app avo-sync-job

{"message": "Start AVO sync of difference since - 2021-01-19T15:08:11+01:00", "logger": "__main__", "level": "info", "timestamp": "2021-03-24T17:32:49.456424Z", "source": "/Users/wschrep/FreelanceWork/VIAA/ldap2db/app/app.py:avo_sync_job:123"}
{"message": "Target database table = shared.ldap_organizations", "logger": "__main__", "level": "info", "timestamp": "2021-03-24T17:32:49.516881Z", "source": "/Users/wschrep/FreelanceWork/VIAA/ldap2db/app/app.py:avo_sync_job:126"}
search_orgs_and_units: modified_at=2021-01-19 15:08:11+01:00

inserting 0 org_with_units into db now...

found orgs with changed units or_ids = {}
{"message": "AVO sync finished", "logger": "__main__", "level": "info", "timestamp": "2021-03-24T17:32:50.955174Z", "source": "/Users/wschrep/FreelanceWork/VIAA/ldap2db/app/app.py:avo_sync_job:128"}

```

Running deewee delta/daily job:
```
$ python -m app.app deewee-sync-job

{"message": "Start DEEWEE sync of difference since - 2021-03-24T15:52:41+01:00", "logger": "__main__", "level": "info", "timestamp": "2021-03-24T17:33:51.601296Z", "source": "/Users/wschrep/FreelanceWork/VIAA/ldap2db/app/app.py:deewee_sync_job:138"}
{"message": "Target database table = shared.ldap_entities", "logger": "__main__", "level": "info", "timestamp": "2021-03-24T17:33:51.663520Z", "source": "/Users/wschrep/FreelanceWork/VIAA/ldap2db/app/app.py:deewee_sync_job:142"}
inserting 0 organizations into db now...
inserting 19 people into db now...
{"message": "DEEWEE sync finished", "logger": "__main__", "level": "info", "timestamp": "2021-03-24T17:33:54.009217Z", "source": "/Users/wschrep/FreelanceWork/VIAA/ldap2db/app/app.py:deewee_sync_job:145"}

```

And as seen above, adding -f or --full-sync as argument will force a full sync by first truncating the table.


Status calls can also be done from commandline, here's an example:
```
$ python -m app.app deewee-status
{'deewee_database_host': '127.0.0.1', 'deewee_database': 'avo_test', 'deewee_database_table': 'shared.ldap_entities', 'deewee_synced_entries': 68692, 'deewee_last_modified': datetime.datetime(2021, 3, 24, 18, 36, 9, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=60, name=None))}
```

### Testing

* `make test` - runs automated tests
* `make coverage` - produces coverage reports
* `testing.postgresql` - creates temporary PostgreSQL databases and cleans up afterwards

## Usage

First clone this repository with `git clone` and change into the new directory.

If you have no access to an LDAP and/or PostgreSQL server they can easily be set up internally by using Docker containers, explained in section [external servers via containers](#external-servers-via-containers).

### Locally

Running the app locally is recommended when developing/debugging and running tests.

First create the virtual environment:

```shell
$ make install
```

Copy the `config.yml.example` file:

```shell
cp ./config.yml.example ./config.yml
```

Be sure to fill in the correct configuration parameters in `config.yml` in order to communicate with the LDAP server and PostgreSQL database.

Run the webserver with fast-api calls to start jobs:
```shell
$ make server
```


#### Testing

Run the tests:

```shell
$ make test

===================================== test session starts =====================================
platform darwin -- Python 3.8.5, pytest-5.3.5, py-1.10.0, pluggy-0.13.1
rootdir: /Users/wschrep/FreelanceWork/VIAA/ldap2db
plugins: cov-2.8.1
collected 37 items

tests/integration/comm/test_avo.py .                                                    [  2%]
tests/integration/comm/test_deewee.py .....                                             [ 16%]
tests/integration/comm/test_ldap.py ..........                                          [ 43%]
tests/unit/test_app.py ......                                                           [ 59%]
tests/unit/comm/test_avo.py ....                                                        [ 70%]
tests/unit/comm/test_deewee.py .......                                                  [ 89%]
tests/unit/comm/test_ldap.py ....                                                       [100%]

===================================== 37 passed in 11.46s =====================================
```

The ldap2db integration tests make use of the PostgreSQL command `initdb` to create a temporary database. Thus, in order the run those integration tests you need to have `PostgreSQL` installed.

If desired, you can also run coverage reports:

```shell
$ make coverage

...
Name                          Stmts   Miss  Cover
-------------------------------------------------
app/__init__.py                   0      0   100%
app/api/__init__.py               0      0   100%
app/api/api.py                    5      0   100%
app/api/routers/__init__.py       0      0   100%
app/api/routers/health.py         5      0   100%
app/api/routers/sync.py          46      2    96%
app/app.py                       76      5    93%
app/comm/__init__.py              0      0   100%
app/comm/avo.py                  44      0   100%
app/comm/deewee.py               45      0   100%
app/comm/ldap.py                118      7    94%
app/comm/psql_wrapper.py         21      0   100%
app/server.py                    12      0   100%
main.py                           3      3     0%
-------------------------------------------------
TOTAL                           375     17    95%

Coverage HTML written to dir htmlcov
```

### External servers via containers

If you have no access to an LDAP and/or PostgreSQL server they can easily be set up internally by using Docker containers.

#### LDAP Container

A container which runs an LDAP server with an empty structure can be found [here](https://github.com/viaacode/docker-openldap-sc-idm "docker-openldap-sc-idm"). The custom `objectClasses` and `attributeTypes` can be found [here](https://github.com/viaacode/viaa-ldap-schema "viaa-ldap-schema"). The latter repository also contains a `sample.ldif` file with some `orgs` and `persons`.

#### PostgreSQL Container

A Dockerfile can be found in `./additional_containers/postgresql`. The schema is defined in the `init.sql` file of said folder.

Create an `env` file and fill in the parameters:

```shell
cp ./additional_containers/postgresql/env.example ./additional_containers/postgresql/env
```

Afterwards build and run the container:

```shell
docker build -f ./additional_containers/postgresql/Dockerfile -t deewee_postgresql .
docker run --name deewee_postgresql -p 5432:5432 --env-file=./additional_containers/postgresql/env -d deewee_postgresql
```

If desired, test the connection with the following statement in terminal:

```shell
psql -h localhost -U {postgresql_user} -d {postgresql_database}
```

### Container

If you just want to execute the app it might be easier to run the container instead of installing python and dependencies.

Copy the config file (`cp ./config.yml.example ./config.yml`) and fill in the correct parameters:

If the app connects to external servers just build the image:

```shell
docker build -t ldap2deewee .
```

If the build succeeded, you should be able to find the image via:

```shell
docker image ls
```

To run the app in the container, just execute:

```shell
docker run --name ldap2deewee -d ldap2deewee
```

If you want to run the tests in the container, you can run the container in interactive mode:

```shell
docker run -it --rm --entrypoint=/bin/sh ldap2deewee
```

You can then run the tests as described in section [testing](#testing-1).

However, if you make use of the other (LDAP and PostgreSQL) containers as described above, the app container needs to able to communicate with them. In order to do so you can connect them via a `Docker Network`. We can do this manually by creating a Docker Network and connecting them. Another more automatic option is via `Docker Compose`.

#### Docker Network

We'll need to create a network and connect the containers together:

```shell
docker network create ldap2deewee_network
docker network connect ldap2deewee_network deewee_postgresql
docker network connect ldap2deewee_network archief_ldap
```

Now we just need to build the ldap2deewee container and run in the Docker Network. Make sure that the host parameters in the `config.yml` file actually point to within the Docker Network.

```shell
docker build -t ldap2deewee .
docker run --name ldap2deewee --network=ldap2deewee_network -d ldap2deewee
```

Check the status via `docker container ls -a` and/or check the logs via `docker logs ldap2deewee`.

#### Docker Compose

Instead of manually creating a network and coupling the containers together, Docker Compose can be used as a more automatic alternative.

Do **note** that how the docker-compose file is set up, the process expects the PostgreSQL and LDAP images to have been build locally. However, as the Docker Compose process will also run the containers, make sure that they do not exist yet.

If you haven't already, be sure to create an `env` file for OpenLDAP and PostgreSQL containers as the Docker Compose process depends on such files. See the respective `env.example` files for the desired structure.

```shell
docker-compose up -d
```
Check the status via `docker container ls -a` and/or check the logs via `docker logs ldap2deewee`%

