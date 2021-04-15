#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app.comm.psql_wrapper import PostgresqlWrapper
from app.models.sync_model import SyncModel


class Companies(SyncModel):
    """Acts as a client to query and modify information from and to database"""

    def __init__(self, db_params: dict, table_names: dict):
        self.table = table_names.get('companies_table', 'tl_companies')
        self.name = 'companies'
        self.postgresql_wrapper = PostgresqlWrapper(db_params)
        self.postgresql_wrapper.execute(
            Companies.create_table_sql(self.table)
        )
