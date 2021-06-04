import pytest
import uuid
import json
from unittest.mock import patch
from dataclasses import dataclass, field, asdict
from datetime import datetime
from viaa.configuration import ConfigParser
from app.models.contacts import Contacts


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


class TestContacts:

    @pytest.fixture
    @patch('app.models.contacts.PostgresqlWrapper')
    def contacts(self, postgresql_wrapper_mock):
        config = ConfigParser()
        db_conf = config.app_cfg['postgresql_teamleader']
        table_names = config.app_cfg['table_names']
        self.contacts = Contacts(db_conf, table_names)
        return self.contacts

    def test_prepare_vars_upsert(self, contacts):
        tlres = TeamleaderEntryMock()
        tlres.attributes['name'] = 'meemoo'
        value = contacts._prepare_vars_upsert(asdict(tlres), 'contacts')
        assert value == (
            tlres.id,
            'contacts',
            tlres.entry_to_json(),
        )

    # def test_upsert_results_many(self, contacts):
    #     psql_wrapper_mock = contacts.postgresql_wrapper

    #     # Create 2 mock contacts
    #     result_1 = TeamleaderEntryMock()
    #     result_1.attributes['name'] = 'comp1'
    #     result_2 = TeamleaderEntryMock()
    #     result_2.attributes['name'] = 'comp2'
    #     # Prepare to pass
    #     results = [([asdict(result_1), asdict(result_2)], 'contacts')]
    #     contacts.upsert_results(results)

    #     # The transformed mock teamleader result as tuple
    #     val1 = contacts._prepare_vars_upsert(asdict(result_1), 'contacts')
    #     val2 = contacts._prepare_vars_upsert(asdict(result_2), 'contacts')

    #     assert psql_wrapper_mock.executemany.call_count == 1
    #     assert psql_wrapper_mock.executemany.call_args[0][0] == contacts.upsert_entities_sql(
    #     )
    #     assert psql_wrapper_mock.executemany.call_args[0][1] == [val1, val2]

    # def test_max_last_modified_timestamp(self, contacts):
    #     psql_wrapper_mock = contacts.postgresql_wrapper
    #     dt = datetime.now()
    #     psql_wrapper_mock.execute.return_value = [[dt]]
    #     value = contacts.max_last_modified_timestamp()
    #     assert psql_wrapper_mock.execute.call_args[0][0] == contacts.max_last_modified_sql(
    #     )
    #     assert value == dt

    # def test_count(self, contacts):
    #     psql_wrapper_mock = contacts.postgresql_wrapper
    #     psql_wrapper_mock.execute.return_value = [[5]]
    #     value = contacts.count()
    #     assert psql_wrapper_mock.execute.call_args[0][0] == contacts.count_sql(
    #     )
    #     assert value == 5

    def test_table_name(self, contacts):
        assert contacts.table_name() == 'tl_contacts'

    def test_status(self, contacts):
        status = contacts.status()

        assert status['database_table'] == 'tl_contacts'
        assert 'synced_entries' in status
        assert 'last_modified' in status
