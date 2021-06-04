import pytest
import uuid
import json
import io
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

    def test_contact_upsert_results_many(self, contacts):
        psql_wrapper_mock = contacts.postgresql_wrapper

        # Create 2 mock contacts
        result_1 = TeamleaderEntryMock()
        result_1.attributes['name'] = 'contact1'
        result_2 = TeamleaderEntryMock()
        result_2.attributes['name'] = 'contact2'
        # Prepare to pass
        results = [([asdict(result_1), asdict(result_2)], 'contacts')]
        contacts.upsert_results(results)

        # The transformed mock teamleader result as tuple
        val1 = contacts._prepare_vars_upsert(asdict(result_1), 'contacts')
        val2 = contacts._prepare_vars_upsert(asdict(result_2), 'contacts')

        assert psql_wrapper_mock.executemany.call_count == 1
        assert psql_wrapper_mock.executemany.call_args[0][0] == contacts.upsert_entities_sql(
        )
        assert psql_wrapper_mock.executemany.call_args[0][1] == [val1, val2]

    def test_contact_last_modified_timestamp(self, contacts):
        psql_wrapper_mock = contacts.postgresql_wrapper
        dt = datetime.now()
        psql_wrapper_mock.execute.return_value = [[dt]]
        value = contacts.max_last_modified_timestamp()
        assert psql_wrapper_mock.execute.call_args[0][0] == contacts.max_last_modified_sql(
        )
        assert value == dt

    def test_contact_count(self, contacts):
        psql_wrapper_mock = contacts.postgresql_wrapper
        psql_wrapper_mock.execute.return_value = [[5]]
        value = contacts.count()
        assert psql_wrapper_mock.execute.call_args[0][0] == contacts.count_sql(
        )
        assert value == 5

    def test_table_name(self, contacts):
        assert contacts.table_name() == 'tl_contacts'

    def test_status(self, contacts):
        status = contacts.status()

        assert status['database_table'] == 'tl_contacts'
        assert 'synced_entries' in status
        assert 'last_modified' in status

    def select_contacts_fixture(self):
        return [
            [
                1, 'uuid1',
                json.loads("""
                    {
                        "website":"http://website1.com",
                        "weburl":"http://weburl1.com",
                        "emails":[
                            {
                                "type": "primary",
                                "email": "walter@meemoo.be"
                            }
                        ]
                    }""")
            ],
            [
                2, 'uuid2',
                json.loads("""
                    {
                        "website":"http://website2.com",
                        "weburl":"http://weburl2.com",
                        "emails":[
                            {
                                "type": "primary",
                                "email": "somebodye@meemoo.be"
                            }
                        ],
                        "telephones":[
                            {
                                "type": "phone",
                                "number": "0486118833"
                            }
                        ]
                    }""")
            ],
            [3, 'uuid3', json.loads('{"remarks": "beschrijving test"}')]
        ]

    @patch.object(Contacts, 'count')
    def test_export_csv(self, count_mock, contacts):
        # patch the self.count method to return 2 contacts
        def contact_count_result():
            return 2

        count_mock.side_effect = contact_count_result

        # return 2 fixtures with json like we get back from VKC
        # by mocking the select_page call with some seed/fixture data
        psql_wrapper_mock = contacts.postgresql_wrapper
        psql_wrapper_mock.execute.return_value = self.select_contacts_fixture()

        # this would work but writes an actual file
        # contacts.export_csv('tests/test_export.csv')

        # use stringio instead of actual file
        # we refactored out write_contacts_csv and pass a stringio object instead
        testfile = io.StringIO()
        contacts.write_contacts_csv(testfile)
        testfile.seek(0)

        contacts_csv = testfile.read()
        csv_rows = contacts_csv.split('\n')
        csv_header = csv_rows[0].split(';')

        # test csv output header is complient
        assert csv_header[0] == 'or_id'
        assert csv_header[1] == 'cp_name_catpro'
        assert csv_header[2] == 'email'
        assert csv_header[3] == 'phone'
        assert csv_header[4] == 'website'
        assert csv_header[5] == 'form_url'
        assert csv_header[6] == 'description'
        assert csv_header[7].strip() == 'accountmanager'

        # test rows match up with fixture data above
        assert csv_rows[1].strip() == ';;walter@meemoo.be;;http://website1.com;;;'
        assert csv_rows[2].strip() == ';;somebodye@meemoo.be;0486118833;http://website2.com;;;'
        assert csv_rows[3].strip() == ';;;;;;beschrijving test;'
