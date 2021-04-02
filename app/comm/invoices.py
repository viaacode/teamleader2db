#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import uuid
from datetime import datetime
from app.comm.psql_wrapper import PostgresqlWrapper
from app.comm.base_model import BaseModel


class Invoices(BaseModel):
    """Acts as a client to query and modify information from and to DEEWEE"""

    def __init__(self, db_params: dict, table_names: dict):
        self.table = table_names.get('invoices_table', 'tl_invoices')
        self.postgresql_wrapper = PostgresqlWrapper(db_params)
        self.postgresql_wrapper.execute(
            Invoices.create_table_sql(self.table)
        )

    def insert_entity(self, date_time: datetime = datetime.now(), tl_type='invoice', content='{"key": "value"}'):
        vars = (str(uuid.uuid4()), tl_type, content)
        self.postgresql_wrapper.execute(self.upsert_entities_sql(), vars)