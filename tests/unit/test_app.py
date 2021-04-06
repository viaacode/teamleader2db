#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from unittest.mock import patch
from datetime import datetime
from psycopg2 import OperationalError as PSQLError
from app.app import App


@patch("app.app.TeamleaderClient")
@patch("app.app.Companies")
@patch("app.app.Contacts")
@patch("app.app.Departments")
# Events
# Invoices
# Projects
# Users(db_conf, table_names)
class TestApp:

    @patch.object(App, 'teamleader_sync', return_value=None)
    def test_main_full(
            self,
            sync_mock,
            teamleader_client_mock,
            companies_mock, contacts_mock, departments_mock
    ):
        # Mock max_last_modified_timestamp to return None
        # companies_mock().max_last_modified_timestamp.return_value = None
        app = App()
        app.teamleader_sync(full_sync=True)

        assert sync_mock.call_count == 1
        call_arg = sync_mock.call_args[1]
        assert call_arg['full_sync'] is True

    @patch.object(App, 'deewee_sync', return_value=None)
    def test_main_diff(
            self,
            sync_mock,
            deewee_client_mock,
            ldap_client_mock,
            avo_client_mock):
        # Mock max_last_modified_timestamp to return "now"
        deewee_client_mock().max_last_modified_timestamp.return_value = datetime.now()

        app = App()
        app.deewee_sync_job()

        assert sync_mock.call_count == 1
        assert deewee_client_mock().max_last_modified_timestamp.call_count == 1

        call_arg = sync_mock.call_args[0][0]
        assert isinstance(call_arg, datetime)

    # def test_sync_deewee(
    #        self,
    #        deewee_client_mock,
    #        ldap_client_mock,
    #        avo_client_mock):
    #    # Mock LdapClient to return certain orgs and persons
    #    ldap_client_mock().search_orgs.return_value = [['org1']]
    #    ldap_client_mock().search_people.return_value = [['person1']]

    #    app = App()
    #    app.deewee_sync_job()

    #    assert ldap_client_mock().search_orgs.call_count == 1
    #    assert ldap_client_mock().search_people.call_count == 1
    #    assert deewee_client_mock().upsert_ldap_results_many.call_count == 2
    #    assert deewee_client_mock().upsert_ldap_results_many.call_args[0][0] == [
    #        (['person1'], 'people')]

    def test_argh_command_line_help(
            self,
            deewee_client_mock,
            ldap_client_mock,
            avo_client_mock):

        app = App()
        with pytest.raises(SystemExit):
            app.main()

    def test_main_psql_error(self, deewee_client_mock,
                             ldap_client_mock, avo_client_mock):
        deewee_client_mock().max_last_modified_timestamp.side_effect = PSQLError
        app = App()
        with pytest.raises(PSQLError):
            app.teamleader_sync()

    @patch.object(App, 'deewee_sync', side_effect=SystemError)
    def test_main_ldap_error(self, sync_mock, deewee_client_mock,
                             ldap_client_mock, avo_client_mock):
        deewee_client_mock().max_last_modified_timestamp.return_value = None
        app = App()
        with pytest.raises(SystemError):
            app.teamleader_sync()
