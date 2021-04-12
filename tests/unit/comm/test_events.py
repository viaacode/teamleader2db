import pytest
import uuid
import json
from unittest.mock import patch
from dataclasses import dataclass, field, asdict
from datetime import datetime
from viaa.configuration import ConfigParser
from app.models.events import Events


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


class TestEvents:

    @pytest.fixture
    @patch('app.models.events.PostgresqlWrapper')
    def events(self, postgresql_wrapper_mock):
        config = ConfigParser()
        db_conf = config.app_cfg['postgresql_teamleader']
        table_names = config.app_cfg['table_names']
        self.events = Events(db_conf, table_names)
        return self.events

    def test_prepare_vars_upsert(self, events):
        tlres = TeamleaderEntryMock()
        tlres.attributes['name'] = 'meeoo'
        value = events._prepare_vars_upsert(asdict(tlres), 'events')
        assert value == (
            tlres.id,
            'events',
            tlres.entry_to_json(),
        )

    def test_upsert_ldap_results_many(self, events):
        psql_wrapper_mock = events.postgresql_wrapper

        # Create 2 mock events
        result_1 = TeamleaderEntryMock()
        result_1.attributes['name'] = 'department1'
        result_2 = TeamleaderEntryMock()
        result_2.attributes['name'] = 'department2'
        # Prepare to pass
        results = [([asdict(result_1), asdict(result_2)], 'events')]
        events.upsert_results(results)

        # The transformed mock teamleader result as tuple
        val1 = events._prepare_vars_upsert(asdict(result_1), 'events')
        val2 = events._prepare_vars_upsert(asdict(result_2), 'events')

        assert psql_wrapper_mock.executemany.call_count == 1
        assert psql_wrapper_mock.executemany.call_args[0][0] == events.upsert_entities_sql(
        )
        assert psql_wrapper_mock.executemany.call_args[0][1] == [val1, val2]

    def test_max_last_modified_timestamp(self, events):
        psql_wrapper_mock = events.postgresql_wrapper
        dt = datetime.now()
        psql_wrapper_mock.execute.return_value = [[dt]]
        value = events.max_last_modified_timestamp()
        assert psql_wrapper_mock.execute.call_args[0][0] == events.max_last_modified_sql(
        )
        assert value == dt

    def test_count(self, events):
        psql_wrapper_mock = events.postgresql_wrapper
        psql_wrapper_mock.execute.return_value = [[5]]
        value = events.count()
        assert psql_wrapper_mock.execute.call_args[0][0] == events.count_sql(
        )
        assert value == 5

    def test_table_name(self, events):
        assert events.table_name() == 'tl_events'

    def test_status(self, events):
        status = events.status()

        assert status['database_table'] == 'tl_events'
        assert 'synced_entries' in status
        assert 'last_modified' in status
