#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime


class BaseModel:
    """ Implements common methods used by the models for syncing data into database.
    currently following models use this: Companies, Contacts, Departments, Events,
    Invoices, Projects, Users."""

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

    def count_sql(self):
        return f'SELECT COUNT(*) FROM {self.table}'

    def max_last_modified_sql(self):
        return f'SELECT max(updated_at) FROM {self.table}'

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

    def count_tl_type(self, tl_type: str) -> int:
        return self.count_where('tl_type = %s', (tl_type,))

    # customize these below methods in the classes where we want different or additional columns.

    @classmethod
    def create_table_sql(cls, table_name):
        return f'''CREATE TABLE IF NOT EXISTS {table_name}(
            id serial PRIMARY KEY,
            tl_uuid uuid NOT NULL,
            tl_content jsonb NOT NULL,
            tl_type VARCHAR,
            created_at timestamp with time zone NOT NULL DEFAULT now(),
            updated_at timestamp with time zone NOT NULL DEFAULT now(),
            CONSTRAINT {table_name.replace(".","_")}_constraint_key UNIQUE (tl_uuid)
        );
        '''

    def upsert_entities_sql(self):
        return f'''INSERT INTO {self.table} (
                                  tl_uuid,
                                  tl_type,
                                  tl_content)
        VALUES (%s, %s, %s) ON CONFLICT (tl_uuid) DO
        UPDATE
        SET tl_content = EXCLUDED.tl_content,
            tl_type = EXCLUDED.tl_type,
            updated_at = now();
        '''

    def _prepare_vars_upsert(self, teamleader_result, tl_type: str) -> tuple:
        """Transforms teamleader entry to pass to the psycopg2 execute function.

        Transform it to a tuple containing the parameters to be able to upsert.
        """
        return (
            str(teamleader_result['id']),
            tl_type,
            json.dumps(teamleader_result)
        )

    def upsert_results(self, teamleader_results: list):
        """Upsert the teamleader entries into PostgreSQL.

       Transforms and flattens the teamleader entries to one list,
       in order to execute in one transaction.

        Arguments:
            teamleader_results -- list of Tuple[list[teamleader_entry], str].
        """
        vars_list = []
        for result_tuple in teamleader_results:
            tl_type = result_tuple[1]
            # Parse and flatten the SQL values from the ldap_results as a
            # passable list
            vars_list.extend(
                [
                    self._prepare_vars_upsert(tl_result, tl_type)
                    for tl_result
                    in result_tuple[0]
                ]
            )
        self.postgresql_wrapper.executemany(
            self.upsert_entities_sql(), vars_list)
