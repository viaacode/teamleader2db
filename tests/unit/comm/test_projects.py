import pytest
import uuid
import json
from unittest.mock import patch
from dataclasses import dataclass, field, asdict
from datetime import datetime
from viaa.configuration import ConfigParser
from app.models.projects import Projects


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


class TestProjects:

    @pytest.fixture
    @patch('app.models.projects.PostgresqlWrapper')
    def projects(self, postgresql_wrapper_mock):
        config = ConfigParser()
        db_conf = config.app_cfg['postgresql_teamleader']
        table_names = config.app_cfg['table_names']
        self.projects = Projects(db_conf, table_names)
        return self.projects

    def test_prepare_vars_upsert(self, projects):
        tlres = TeamleaderEntryMock()
        tlres.attributes['name'] = 'meemoo project'
        value = projects._prepare_vars_upsert(asdict(tlres), 'projects')
        assert value == (
            tlres.id,
            'projects',
            tlres.entry_to_json(),
        )

    def test_upsert_results_many(self, projects):
        psql_wrapper_mock = projects.postgresql_wrapper

        # Create 2 mock projects
        result_1 = TeamleaderEntryMock()
        result_1.attributes['name'] = 'project1'
        result_2 = TeamleaderEntryMock()
        result_2.attributes['name'] = 'project2'
        # Prepare to pass
        results = [([asdict(result_1), asdict(result_2)], 'projects')]
        projects.upsert_results(results)

        # The transformed mock teamleader result as tuple
        val1 = projects._prepare_vars_upsert(asdict(result_1), 'projects')
        val2 = projects._prepare_vars_upsert(asdict(result_2), 'projects')

        assert psql_wrapper_mock.executemany.call_count == 1
        assert psql_wrapper_mock.executemany.call_args[0][0] == projects.upsert_entities_sql(
        )
        assert psql_wrapper_mock.executemany.call_args[0][1] == [val1, val2]

    def test_max_last_modified_timestamp(self, projects):
        psql_wrapper_mock = projects.postgresql_wrapper
        dt = datetime.now()
        psql_wrapper_mock.execute.return_value = [[dt]]
        value = projects.max_last_modified_timestamp()
        assert psql_wrapper_mock.execute.call_args[0][0] == projects.max_last_modified_sql(
        )
        assert value == dt

    def test_count(self, projects):
        psql_wrapper_mock = projects.postgresql_wrapper
        psql_wrapper_mock.execute.return_value = [[5]]
        value = projects.count()
        assert psql_wrapper_mock.execute.call_args[0][0] == projects.count_sql(
        )
        assert value == 5

    def test_table_name(self, projects):
        assert projects.table_name() == 'tl_projects'

    def test_status(self, projects):
        status = projects.status()

        assert status['database_table'] == 'tl_projects'
        assert 'synced_entries' in status
        assert 'last_modified' in status
