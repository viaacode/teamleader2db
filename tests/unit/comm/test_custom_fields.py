import pytest
import uuid
import json
from unittest.mock import patch
from dataclasses import dataclass, field, asdict
from datetime import datetime
from viaa.configuration import ConfigParser
from app.models.custom_fields import CustomFields


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


class TestCustomFields:

    @pytest.fixture
    @patch('app.models.custom_fields.PostgresqlWrapper')
    def custom_fields(self, postgresql_wrapper_mock):
        config = ConfigParser()
        db_conf = config.app_cfg['postgresql_teamleader']
        table_names = config.app_cfg['table_names']
        self.custom_fields = CustomFields(db_conf, table_names)
        return self.custom_fields

    def test_prepare_vars_upsert(self, custom_fields):
        tlres = TeamleaderEntryMock()
        tlres.attributes['name'] = 'meemoo project'
        value = custom_fields._prepare_vars_upsert(asdict(tlres), 'custom_fields')
        assert value == (
            tlres.id,
            'custom_fields',
            tlres.entry_to_json(),
        )

    def test_upsert_results_many(self, custom_fields):
        psql_wrapper_mock = custom_fields.postgresql_wrapper

        # Create 2 mock custom_fields
        result_1 = TeamleaderEntryMock()
        result_1.attributes['name'] = 'custom_field1'
        result_2 = TeamleaderEntryMock()
        result_2.attributes['name'] = 'custom_field2'

        # Prepare to pass
        results = [([asdict(result_1), asdict(result_2)], 'custom_fields')]
        custom_fields.upsert_results(results)

        # The transformed mock teamleader result as tuple
        val1 = custom_fields._prepare_vars_upsert(asdict(result_1), 'custom_fields')
        val2 = custom_fields._prepare_vars_upsert(asdict(result_2), 'custom_fields')

        assert psql_wrapper_mock.executemany.call_count == 1
        assert psql_wrapper_mock.executemany.call_args[0][0] == custom_fields.upsert_entities_sql(
        )
        assert psql_wrapper_mock.executemany.call_args[0][1] == [val1, val2]

    def test_max_last_modified_timestamp(self, custom_fields):
        psql_wrapper_mock = custom_fields.postgresql_wrapper
        dt = datetime.now()
        psql_wrapper_mock.execute.return_value = [[dt]]
        value = custom_fields.max_last_modified_timestamp()
        assert psql_wrapper_mock.execute.call_args[0][0] == custom_fields.max_last_modified_sql(
        )
        assert value == dt

    def test_count(self, custom_fields):
        psql_wrapper_mock = custom_fields.postgresql_wrapper
        psql_wrapper_mock.execute.return_value = [[5]]
        value = custom_fields.count()
        assert psql_wrapper_mock.execute.call_args[0][0] == custom_fields.count_sql(
        )
        assert value == 5

    def test_table_name(self, custom_fields):
        assert custom_fields.table_name() == 'tl_custom_fields'

    def test_status(self, custom_fields):
        status = custom_fields.status()

        assert status['database_table'] == 'tl_custom_fields'
        assert 'synced_entries' in status
        assert 'last_modified' in status
