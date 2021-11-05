#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app.comm.psql_wrapper import PostgresqlWrapper
from app.models.sync_model import SyncModel


class CustomFields(SyncModel):
    """Acts as a client to query and modify information from and to database"""

    def __init__(self, db_params: dict, table_names: dict):
        self.table = table_names.get('custom_fields_table', 'tl_custom_fields')
        self.name = 'custom_fields'
        self.postgresql_wrapper = PostgresqlWrapper(db_params)
        self.postgresql_wrapper.execute(
            CustomFields.create_table_sql(self.table)
        )
