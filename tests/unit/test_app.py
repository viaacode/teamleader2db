#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from unittest.mock import patch
from psycopg2 import OperationalError as PSQLError
from app.app import App


@patch('app.app.Users')
@patch('app.app.Projects')
@patch('app.app.Invoices')
@patch('app.app.Events')
@patch('app.app.Departments')
@patch('app.app.Companies')
@patch('app.app.Contacts')
@patch('app.comm.teamleader_client.TeamleaderAuth')
@patch("app.app.TeamleaderClient")
class TestApp:

    @patch.object(App, 'teamleader_sync', return_value=None)
    def test_main_full(
        self,
        sync_mock,
        teamleader_client_mock,
        tl_auth_mock, contacts_mock, companies_mock, departments_mock,
        events_mock, invoices_mock, projects_mock, users_mock
    ):
        # Mock max_last_modified_timestamp to return None
        companies_mock().max_last_modified_timestamp.return_value = None
        contacts_mock().max_last_modified_timestamp.return_value = None
        departments_mock().max_last_modified_timestamp.return_value = None
        events_mock().max_last_modified_timestamp.return_value = None
        invoices_mock().max_last_modified_timestamp.return_value = None
        projects_mock().max_last_modified_timestamp.return_value = None
        users_mock().max_last_modified_timestamp.return_value = None

        app = App()
        app.teamleader_sync(full_sync=True)

        assert sync_mock.call_count == 1
        call_arg = sync_mock.call_args[1]
        assert call_arg['full_sync'] is True

    @patch.object(App, 'teamleader_sync', return_value=None)
    def test_main_diff(
        self,
        sync_mock,
        teamleader_client_mock,
        *models_mock
    ):
        app = App()
        app.teamleader_sync(full_sync=False)

        assert sync_mock.call_count == 1
        call_arg = sync_mock.call_args[1]
        assert call_arg['full_sync'] is False

    @pytest.mark.skip(reason="systemerror only thrown with make coverage, not with make test")
    def test_argh_command_line_help(
        self,
        teamleader_client_mock,
        *models_mock
    ):
        app = App()
        with pytest.raises(SystemExit):
            app.main()

    def test_main_psql_error(
        self,
        teamleader_client_mock,
        *models_mock
    ):
        companies_mock = models_mock[2]
        companies_mock().max_last_modified_timestamp.side_effect = PSQLError
        app = App()
        with pytest.raises(PSQLError):
            app.teamleader_sync()
