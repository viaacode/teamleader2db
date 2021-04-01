#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import uuid
from datetime import datetime
from app.comm.psql_wrapper import PostgresqlWrapper


class BaseModel:

    def __init(self, db_params: dict, table_names: dict):
        pass

    def table_name(self):
        return self.table

    def status(self):
        return {
            'database_table': self.table_name(),
            'synced_entries': self.count(),
            'last_modified': self.max_last_modified_timestamp()
        }

    def truncate_table(self):
        self.postgresql_wrapper.execute(
            f'TRUNCATE TABLE {self.table};'
        )

    def max_last_modified_timestamp(self) -> datetime:
        """Returns the highest ldap_modifytimestamp"""
        return self.postgresql_wrapper.execute(
            self.max_last_modified_sql()
        )[0][0]

    def count(self) -> int:
        return self.postgresql_wrapper.execute(self.count_sql())[0][0]

    def count_where(self, where_clause: str, vars: tuple = None) -> int:
        """Constructs and executes a 'select count(*) where' statement.

        The where clause can contain zero or more paremeters.

        If there are no parameters e.g. clause = "column is null", vars should be None.
        If there are one or more parameters e.g. where_clause = "column = %s",
            vars should be a tuple containing the parameters.

        Arguments:
            where_clause -- represents the clause that comes after the where keyword
            vars -- see above

        Returns:
            int -- the amount of records
        """
        select_sql = f'{self.count_sql()} where {where_clause};'
        return self.postgresql_wrapper.execute(select_sql, vars)[0][0]

    def count_type(self, type: str) -> int:
        return self.count_where('type = %s', (type,))
