import pytest
import uuid
import json
from unittest.mock import patch
from dataclasses import dataclass, field, asdict
from datetime import datetime
from viaa.configuration import ConfigParser
from app.models.companies import Companies


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


class TestCompanies:

    @pytest.fixture
    @patch('app.models.companies.PostgresqlWrapper')
    def companies(self, postgresql_wrapper_mock):
        config = ConfigParser()
        db_conf = config.app_cfg['postgresql_teamleader']
        table_names = config.app_cfg['table_names']
        self.companies = Companies(db_conf, table_names)
        return self.companies

    def test_prepare_vars_upsert(self, companies):
        tlres = TeamleaderEntryMock()
        tlres.attributes['name'] = 'meeoo'
        value = companies._prepare_vars_upsert(asdict(tlres), 'companies')
        assert value == (
            tlres.id,
            'companies',
            tlres.entry_to_json(),
        )

    def test_upsert_ldap_results_many(self, companies):
        psql_wrapper_mock = companies.postgresql_wrapper

        # Create 2 mock companies
        result_1 = TeamleaderEntryMock()
        result_1.attributes['name'] = 'comp1'
        result_2 = TeamleaderEntryMock()
        result_2.attributes['name'] = 'comp2'
        # Prepare to pass
        results = [([asdict(result_1), asdict(result_2)], 'companies')]
        companies.upsert_results(results)

        # The transformed mock teamleader result as tuple
        val1 = companies._prepare_vars_upsert(asdict(result_1), 'companies')
        val2 = companies._prepare_vars_upsert(asdict(result_2), 'companies')

        assert psql_wrapper_mock.executemany.call_count == 1
        assert psql_wrapper_mock.executemany.call_args[0][0] == companies.upsert_entities_sql(
        )
        assert psql_wrapper_mock.executemany.call_args[0][1] == [val1, val2]

    def test_max_last_modified_timestamp(self, companies):
        psql_wrapper_mock = companies.postgresql_wrapper
        dt = datetime.now()
        psql_wrapper_mock.execute.return_value = [[dt]]
        value = companies.max_last_modified_timestamp()
        assert psql_wrapper_mock.execute.call_args[0][0] == companies.max_last_modified_sql(
        )
        assert value == dt

    def test_count(self, companies):
        psql_wrapper_mock = companies.postgresql_wrapper
        psql_wrapper_mock.execute.return_value = [[5]]
        value = companies.count()
        assert psql_wrapper_mock.execute.call_args[0][0] == companies.count_sql(
        )
        assert value == 5

    def test_table_name(self, companies):
        assert companies.table_name() == 'tl_companies'

    def test_status(self, companies):
        status = companies.status()

        assert status['database_table'] == 'tl_companies'
        assert 'synced_entries' in status
        assert 'last_modified' in status
