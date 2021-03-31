#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import uuid
from datetime import datetime
from app.comm.psql_wrapper import PostgresqlWrapper


class AvoClient:
    """Acts as a client to query and modify information from and to DEEWEE"""

    def __init__(self, params: dict):
        self.db_connect = params.copy()
        self.table = self.db_connect.pop('table_name', 'ldap_organizations')
        self.postgresql_wrapper = PostgresqlWrapper(self.db_connect)
        self.postgresql_wrapper.execute(
            AvoClient.create_table_sql(self.table)
        )

    def table_name(self):
        return self.table

    def status(self):
        return {
            'avo_database_host': self.db_connect.get('host', 'avo_db_host'),
            'avo_database': self.db_connect.get('database', 'avo_db'),
            'avo_database_table': self.table_name(),
            'avo_synced_entries': self.count(),
            'avo_last_modified': self.max_last_modified_timestamp()
        }

    @classmethod
    def create_table_sql(cls, table_name):
        return f'''CREATE TABLE IF NOT EXISTS {table_name}(
            id serial PRIMARY KEY,
            organization_id VARCHAR NOT NULL,
            ldap_entryuuid uuid NOT NULL,
            ldap_description text,
            ldap_content jsonb NOT NULL,
            type VARCHAR,
            ldap_modifytimestamp timestamp with time zone NOT NULL,
            created_at timestamp with time zone NOT NULL DEFAULT now(),
            updated_at timestamp with time zone NOT NULL DEFAULT now(),
            CONSTRAINT {table_name.replace(".","_")}_constraint_key UNIQUE (ldap_entryuuid)
        );
        '''

    def upsert_entities_sql(self):
        return f'''INSERT INTO {self.table} (
                                  ldap_entryuuid,
                                  organization_id,
                                  ldap_description,
                                  type,
                                  ldap_content,
                                  ldap_modifytimestamp)
        VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (ldap_entryuuid) DO
        UPDATE
        SET organization_id = EXCLUDED.organization_id,
            ldap_description = EXCLUDED.ldap_description,
            type = EXCLUDED.type,
            ldap_content = EXCLUDED.ldap_content,
            ldap_modifytimestamp = EXCLUDED.ldap_modifytimestamp;
        '''

    def count_sql(self):
        return f'SELECT COUNT(*) FROM {self.table}'

    def max_last_modified_sql(self):
        return f'SELECT max(ldap_modifytimestamp) FROM {self.table}'

    def _prepare_vars_upsert(self, ldap_result, type: str) -> tuple:
        """Transforms an LDAP entry to pass to the psycopg2 execute function.

        Transform it to a tuple containing the parameters to be able to upsert.
        """
        return (
            str(ldap_result.entryUUID),
            str(ldap_result.entryOID),
            str(ldap_result.entryDescription),
            type,
            ldap_result.entry_to_json(),
            ldap_result.modifyTimestamp.value
        )

    def upsert_ldap_results_many(self, ldap_results: list):
        """Upsert the LDAP entries into PostgreSQL.

       Transforms and flattens the LDAP entries to one list,
       in order to execute in one transaction.

        Arguments:
            ldap_results -- list of Tuple[list[LDAP_Entry], str].
                            The tuple contains a list of LDAP entries and a type (str)
        """
        vars_list = []
        for ldap_result_tuple in ldap_results:
            type = ldap_result_tuple[1]
            # Parse and flatten the SQL values from the ldap_results as a
            # passable list
            vars_list.extend(
                [
                    self._prepare_vars_upsert(ldap_result, type)
                    for ldap_result
                    in ldap_result_tuple[0]
                ]
            )
        self.postgresql_wrapper.executemany(
            self.upsert_entities_sql(), vars_list)

    def max_last_modified_timestamp(self) -> datetime:
        """Returns the highest ldap_modifytimestamp"""
        return self.postgresql_wrapper.execute(
            self.max_last_modified_sql()
        )[0][0]

    def insert_entity(
            self,
            date_time: datetime = datetime.now(),
            type='person'):
        vars = (str(uuid.uuid4()), 'org_id', 'description',
                type, '{"key": "value"}', date_time)
        self.postgresql_wrapper.execute(self.upsert_entities_sql(), vars)

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

    def truncate_table(self):
        self.postgresql_wrapper.execute(
            f'TRUNCATE TABLE {self.table};'
        )
