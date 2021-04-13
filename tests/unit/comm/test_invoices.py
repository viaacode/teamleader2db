import pytest
import uuid
import json
from unittest.mock import patch
from dataclasses import dataclass, field, asdict
from datetime import datetime
from viaa.configuration import ConfigParser
from app.models.invoices import Invoices


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


class TestInvoices:

    @pytest.fixture
    @patch('app.models.invoices.PostgresqlWrapper')
    def invoices(self, postgresql_wrapper_mock):
        config = ConfigParser()
        db_conf = config.app_cfg['postgresql_teamleader']
        table_names = config.app_cfg['table_names']
        self.invoices = Invoices(db_conf, table_names)
        return self.invoices

    def test_prepare_vars_upsert(self, invoices):
        tlres = TeamleaderEntryMock()
        tlres.attributes['name'] = 'meemoo invoice'
        value = invoices._prepare_vars_upsert(asdict(tlres), 'invoices')
        assert value == (
            tlres.id,
            'invoices',
            tlres.entry_to_json(),
        )

    def test_upsert_results_many(self, invoices):
        psql_wrapper_mock = invoices.postgresql_wrapper

        # Create 2 mock invoices
        result_1 = TeamleaderEntryMock()
        result_1.attributes['name'] = 'invoice1'
        result_2 = TeamleaderEntryMock()
        result_2.attributes['name'] = 'invoice2'
        # Prepare to pass
        results = [([asdict(result_1), asdict(result_2)], 'invoices')]
        invoices.upsert_results(results)

        # The transformed mock teamleader result as tuple
        val1 = invoices._prepare_vars_upsert(asdict(result_1), 'invoices')
        val2 = invoices._prepare_vars_upsert(asdict(result_2), 'invoices')

        assert psql_wrapper_mock.executemany.call_count == 1
        assert psql_wrapper_mock.executemany.call_args[0][0] == invoices.upsert_entities_sql(
        )
        assert psql_wrapper_mock.executemany.call_args[0][1] == [val1, val2]

    def test_max_last_modified_timestamp(self, invoices):
        psql_wrapper_mock = invoices.postgresql_wrapper
        dt = datetime.now()
        psql_wrapper_mock.execute.return_value = [[dt]]
        value = invoices.max_last_modified_timestamp()
        assert psql_wrapper_mock.execute.call_args[0][0] == invoices.max_last_modified_sql(
        )
        assert value == dt

    def test_count(self, invoices):
        psql_wrapper_mock = invoices.postgresql_wrapper
        psql_wrapper_mock.execute.return_value = [[5]]
        value = invoices.count()
        assert psql_wrapper_mock.execute.call_args[0][0] == invoices.count_sql(
        )
        assert value == 5

    def test_table_name(self, invoices):
        assert invoices.table_name() == 'tl_invoices'

    def test_status(self, invoices):
        status = invoices.status()

        assert status['database_table'] == 'tl_invoices'
        assert 'synced_entries' in status
        assert 'last_modified' in status
