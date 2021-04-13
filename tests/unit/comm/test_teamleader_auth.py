import pytest
import uuid
import json
from unittest.mock import patch
from dataclasses import dataclass, field, asdict
from datetime import datetime
from viaa.configuration import ConfigParser
from app.models.teamleader_auth import TeamleaderAuth


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


class TestTeamleaderAuth:

    @pytest.fixture
    @patch('app.models.teamleader_auth.PostgresqlWrapper')
    def teamleader_auth(self, postgresql_wrapper_mock):
        config = ConfigParser()
        db_conf = config.app_cfg['postgresql_teamleader']
        table_names = config.app_cfg['table_names']
        self.teamleader_auth = TeamleaderAuth(db_conf, table_names)
        return self.teamleader_auth

    def test_read(self, teamleader_auth):
        code, token, frefresh = teamleader_auth.read()
        qry_executed = teamleader_auth.postgresql_wrapper.execute.call_args[0][0]
        assert 'SELECT * FROM' in qry_executed
        assert 'LIMIT 1' in qry_executed

    def test_reset(self, teamleader_auth):
        teamleader_auth.reset()
        assert 'TRUNCATE TABLE' in teamleader_auth.postgresql_wrapper.execute.call_args[
            0][0]

    def test_save_initial(self, teamleader_auth):
        # setup count to return 0, meaning no tokens saved before
        psql_wrapper_mock = teamleader_auth.postgresql_wrapper
        psql_wrapper_mock.execute.return_value = [[0]]

        teamleader_auth.save('code1', 'token1', 'rt_1')
        qry_executed = teamleader_auth.postgresql_wrapper.execute.call_args[0][0]
        assert qry_executed == teamleader_auth.insert_tokens_sql()

    def test_save_updated(self, teamleader_auth):
        # setup count to return 1, causes an update instead of insert
        psql_wrapper_mock = teamleader_auth.postgresql_wrapper
        psql_wrapper_mock.execute.return_value = [[1]]

        teamleader_auth.save('code1', 'token1', 'rt_1')
        qry_executed = teamleader_auth.postgresql_wrapper.execute.call_args[0][0]
        assert qry_executed == teamleader_auth.update_tokens_sql()

    def test_count(self, teamleader_auth):
        psql_wrapper_mock = teamleader_auth.postgresql_wrapper
        psql_wrapper_mock.execute.return_value = [[1]]
        value = teamleader_auth.count()
        assert value == 1

    def test_table_name(self, teamleader_auth):
        assert teamleader_auth.table == 'tl_auth'
