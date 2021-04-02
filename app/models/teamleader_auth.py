#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app.comm.psql_wrapper import PostgresqlWrapper


class TeamleaderAuth():
    """Acts as a client to query and modify information from and to database"""

    def __init__(self, db_params: dict, table_names: dict):
        self.table = table_names.get('oauth_table', 'shared.tl_auth')
        self.postgresql_wrapper = PostgresqlWrapper(db_params)
        self.postgresql_wrapper.execute(
            TeamleaderAuth.create_table_sql(self.table)
        )

    def save(self, code='', auth_token='', refresh_token=''):
        print(
            f"saving updated code, auth_token, refresh_token to table {self.table}", flush=True)
        if self.count() == 0:
            self.postgresql_wrapper.execute(
                self.insert_tokens_sql(),
                (code, auth_token, refresh_token)
            )
        else:
            self.postgresql_wrapper.execute(
                self.update_tokens_sql(),
                (code, auth_token, refresh_token)
            )

    def read(self):
        print(
            f"loading code, auth_token, refresh_token from database table {self.table}", flush=True)
        row = self.postgresql_wrapper.execute(
            f'SELECT * FROM {self.table} LIMIT 1;')[0]
        code = row[1]
        token = row[2]
        refresh_token = row[3]
        return code, token, refresh_token

    @classmethod
    def create_table_sql(cls, table_name):
        return f'''CREATE TABLE IF NOT EXISTS {table_name}(
            id serial PRIMARY KEY,
            code VARCHAR,
            auth_token VARCHAR,
            refresh_token VARCHAR,
            created_at timestamp with time zone NOT NULL DEFAULT now(),
            updated_at timestamp with time zone NOT NULL DEFAULT now()
        );
        '''

    def reset(self):
        self.postgresql_wrapper.execute(
            f'TRUNCATE TABLE {self.table};'
        )

    def count(self) -> int:
        count_sql = f'SELECT COUNT(*) FROM {self.table}'
        return self.postgresql_wrapper.execute(count_sql)[0][0]

    def insert_tokens_sql(self):
        return f'''
            INSERT INTO {self.table} (code, auth_token, refresh_token)
            VALUES (%s, %s, %s)
        '''

    def update_tokens_sql(self):
        return f'''
            UPDATE {self.table} SET
            code = %s, auth_token = %s, refresh_token = %s, updated_at = now();
        '''
