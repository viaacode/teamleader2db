#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import uuid
from datetime import datetime
from app.comm.psql_wrapper import PostgresqlWrapper
from app.comm.base_model import BaseModel


class Contacts(BaseModel):
    """Acts as a client to query and modify information from and to DEEWEE"""

    def __init__(self, db_params: dict, table_names: dict):
        self.table = table_names.get('contacts_table', 'tl_companies')
        self.postgresql_wrapper = PostgresqlWrapper(db_params)
        self.postgresql_wrapper.execute(
            Contacts.create_table_sql(self.table)
        )

    @classmethod
    def create_table_sql(cls, table_name):
        return f'''CREATE TABLE IF NOT EXISTS {table_name}(
            id serial PRIMARY KEY,
            tl_entryuuid uuid NOT NULL,
            content jsonb NOT NULL,
            type VARCHAR,
            tl_modifytimestamp timestamp with time zone NOT NULL,
            created_at timestamp with time zone NOT NULL DEFAULT now(),
            updated_at timestamp with time zone NOT NULL DEFAULT now(),
            CONSTRAINT {table_name.replace(".","_")}_constraint_key UNIQUE (tl_entryuuid)
        );
        '''

    def upsert_entities_sql(self):
        return f'''INSERT INTO {self.table} (
                                  tl_entryuuid,
                                  type,
                                  content,
                                  tl_modifytimestamp)
        VALUES (%s, %s, %s, %s) ON CONFLICT (tl_entryuuid) DO
        UPDATE
        SET content = EXCLUDED.ldap_content,
            type = EXCLUDED.type,
            tl_modifytimestamp = EXCLUDED.tl_modifytimestamp;
        '''

    def count_sql(self):
        return f'SELECT COUNT(*) FROM {self.table}'

    def max_last_modified_sql(self):
        return f'SELECT max(tl_modifytimestamp) FROM {self.table}'

    def truncate_table(self):
        self.postgresql_wrapper.execute(
            f'TRUNCATE TABLE {self.table};'
        )

    def max_last_modified_timestamp(self) -> datetime:
        """Returns the highest ldap_modifytimestamp"""
        return self.postgresql_wrapper.execute(
            self.max_last_modified_sql()
        )[0][0]



#    def _prepare_vars_upsert(self, ldap_result, type: str) -> tuple:
#        """Transforms an LDAP entry to pass to the psycopg2 execute function.
#
#        Transform it to a tuple containing the parameters to be able to upsert.
#        """
#        return (
#            str(ldap_result.entryUUID),
#            str(ldap_result.entryOID),
#            str(ldap_result.entryDescription),
#            type,
#            ldap_result.entry_to_json(),
#            ldap_result.modifyTimestamp.value
#        )
#
#    def upsert_ldap_results_many(self, ldap_results: list):
#        """Upsert the LDAP entries into PostgreSQL.
#
#       Transforms and flattens the LDAP entries to one list,
#       in order to execute in one transaction.
#
#        Arguments:
#            ldap_results -- list of Tuple[list[LDAP_Entry], str].
#                            The tuple contains a list of LDAP entries and a type (str)
#        """
#        vars_list = []
#        for ldap_result_tuple in ldap_results:
#            type = ldap_result_tuple[1]
#            # Parse and flatten the SQL values from the ldap_results as a
#            # passable list
#            vars_list.extend(
#                [
#                    self._prepare_vars_upsert(ldap_result, type)
#                    for ldap_result
#                    in ldap_result_tuple[0]
#                ]
#            )
#        self.postgresql_wrapper.executemany(
#            self.upsert_entities_sql(), vars_list)
#
#
#    def insert_entity(
#            self,
#            date_time: datetime = datetime.now(),
#            type='person'):
#        vars = (str(uuid.uuid4()), 'org_id', 'description',
#                type, '{"key": "value"}', date_time)
#        self.postgresql_wrapper.execute(self.upsert_entities_sql(), vars)
#

