import pytest
import uuid
import json
from unittest.mock import patch
from dataclasses import dataclass, field, asdict
from datetime import datetime
from viaa.configuration import ConfigParser
from app.models.users import Users


@dataclass
class ModifyTimestampMock:
    """Mock class of the returned modifyTimestamp by LDAP server"""

    value: str = str(datetime.now())


@dataclass
class TeamleaderEntryMock:
    '''Mock teamleader entry'''

    id: str = str(uuid.uuid4())
    modifyTimestamp: ModifyTimestampMock = ModifyTimestampMock()
    attributes: dict = field(default_factory=dict)

    def entry_to_json(self) -> str:
        return json.dumps(asdict(self))


class TestUsers:

    @pytest.fixture
    @patch('app.models.users.PostgresqlWrapper')
    def users(self, postgresql_wrapper_mock):
        config = ConfigParser()
        db_conf = config.app_cfg['postgresql_teamleader']
        table_names = config.app_cfg['table_names']
        self.users = Users(db_conf, table_names)
        return self.users

    def test_prepare_vars_upsert(self, users):
        tlres = TeamleaderEntryMock()
        tlres.attributes['name'] = 'meemoo user'
        value = users._prepare_vars_upsert(asdict(tlres), 'users')
        assert value == (
            tlres.id,
            'users',
            tlres.entry_to_json(),
        )

    def test_upsert_results_many(self, users):
        psql_wrapper_mock = users.postgresql_wrapper

        # Create 2 mock users
        result_1 = TeamleaderEntryMock()
        result_1.attributes['name'] = 'user1'
        result_2 = TeamleaderEntryMock()
        result_2.attributes['name'] = 'user2'
        # Prepare to pass
        results = [([asdict(result_1), asdict(result_2)], 'users')]
        users.upsert_results(results)

        # The transformed mock teamleader result as tuple
        val1 = users._prepare_vars_upsert(asdict(result_1), 'users')
        val2 = users._prepare_vars_upsert(asdict(result_2), 'users')

        assert psql_wrapper_mock.executemany.call_count == 1
        assert psql_wrapper_mock.executemany.call_args[0][0] == users.upsert_entities_sql(
        )
        assert psql_wrapper_mock.executemany.call_args[0][1] == [val1, val2]

    def test_max_last_modified_timestamp(self, users):
        psql_wrapper_mock = users.postgresql_wrapper
        dt = datetime.now()
        psql_wrapper_mock.execute.return_value = [[dt]]
        value = users.max_last_modified_timestamp()
        assert psql_wrapper_mock.execute.call_args[0][0] == users.max_last_modified_sql(
        )
        assert value == dt

    def test_count(self, users):
        psql_wrapper_mock = users.postgresql_wrapper
        psql_wrapper_mock.execute.return_value = [[5]]
        value = users.count()
        assert psql_wrapper_mock.execute.call_args[0][0] == users.count_sql(
        )
        assert value == 5

    def test_table_name(self, users):
        assert users.table_name() == 'tl_users'

    def test_status(self, users):
        status = users.status()

        assert status['database_table'] == 'tl_users'
        assert 'synced_entries' in status
        assert 'last_modified' in status
