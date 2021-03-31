#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import uuid
from datetime import datetime
from app.comm.psql_wrapper import PostgresqlWrapper
from app.comm.base_model import BaseModel


class Companies(BaseModel):
    """Acts as a client to query and modify information from and to DEEWEE"""

    def __init__(self, db_params: dict, table_names: dict):
        self.table = table_names.get('companies_table', 'tl_companies')
        self.postgresql_wrapper = PostgresqlWrapper(db_params)
        self.postgresql_wrapper.execute(
            Companies.create_table_sql(self.table)
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


