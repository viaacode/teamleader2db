#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import uuid
from unittest.mock import patch
# from dataclasses import dataclass, field
# from datetime import datetime
from viaa.configuration import ConfigParser
from app.models.contacts import Contacts
from app.comm.psql_wrapper import PostgresqlWrapper

TABLE_NAME = 'tl_contacts'
COUNT_ENTITIES_SQL = f'SELECT COUNT(*) FROM {TABLE_NAME}'


class TestPostgresqlWrapper:

    @pytest.fixture
    def postgresql_wrapper(self):
        """Returns a PostgresqlWrapper initiliazed by the parameters in config.yml"""
        return PostgresqlWrapper(ConfigParser().app_cfg['postgresql_teamleader'])

    @pytest.fixture
    @patch('psycopg2.connect')
    def upsert_entities_sql(self, mock_connect):
        config = ConfigParser()
        db_conf = config.app_cfg['postgresql_teamleader']
        table_names = config.app_cfg['table_names']
        self.contacts = Contacts(db_conf, table_names)
        return self.contacts.upsert_entities_sql()

    @patch('psycopg2.connect')
    def test_execute(self, mock_connect, postgresql_wrapper):
        connect = mock_connect.return_value.__enter__.return_value
        connect.cursor.return_value.__enter__.return_value.fetchall.return_value = 5
        result = postgresql_wrapper.execute(COUNT_ENTITIES_SQL)
        assert result == 5

    @patch('psycopg2.connect')
    def test_execute_insert(self, mock_connect, postgresql_wrapper, upsert_entities_sql):
        key = str(uuid.uuid4())
        mock_connect.cursor.return_value.description = None
        postgresql_wrapper.execute(upsert_entities_sql, [key])
        connect = mock_connect.return_value.__enter__.return_value
        cursor = connect.cursor.return_value.__enter__.return_value
        assert cursor.execute.call_count == 1
        assert cursor.execute.call_args[0][0] == upsert_entities_sql
        assert cursor.execute.call_args[0][1] == [key]

    @patch('psycopg2.connect')
    def test_executemany(self, mock_connect, postgresql_wrapper, upsert_entities_sql):
        values = [(str(uuid.uuid4()),), (str(uuid.uuid4()),)]
        postgresql_wrapper.executemany(upsert_entities_sql, values)
        connect = mock_connect.return_value.__enter__.return_value
        cursor = connect.cursor.return_value.__enter__.return_value
        assert cursor.executemany.call_count == 1
        assert cursor.executemany.call_args[0][0] == upsert_entities_sql
        assert cursor.executemany.call_args[0][1] == values
