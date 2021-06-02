#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#   app/comm/psql_wrapper.py
#
#   PostgresqlWrapper that wraps postgres connection
#   and also allows for our unit and integration tests to more
#   easily mock it.
#
import psycopg2
from functools import wraps


class PostgresqlWrapper:
    """Allows for executing SQL statements to a postgresql database"""

    def __init__(self, params: dict):
        self.params_postgresql = params

    def _connect_curs_postgresql(function):
        """Wrapper function that connects and authenticates to the PostgreSQL DB.

        The passed function will receive the open cursor.
        """
        @wraps(function)
        def wrapper_connect(self, *args, **kwargs):
            with psycopg2.connect(**self.params_postgresql) as conn:
                with conn.cursor() as curs:
                    val = function(self, cursor=curs, *args, **kwargs)
            return val
        return wrapper_connect

    @_connect_curs_postgresql
    def execute(self, query: str, vars=None, cursor=None):
        """Connects to the postgresql DB and executes the statement.

        Returns all results of the statement if applicable.
        """
        cursor.execute(query, vars)
        if cursor.description is not None:
            return cursor.fetchall()

    @_connect_curs_postgresql
    def executemany(self, query: str, vars_list: list, cursor=None):
        """Connects to the postgresql DB and executes the many statement"""
        cursor.executemany(query, vars_list)
