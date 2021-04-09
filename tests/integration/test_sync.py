#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from unittest.mock import patch, Mock
from app.app import App


# pytestmark = [pytest.mark.vcr(ignore_localhost=True)]
# @pytest.fixture(scope="module")
# def vcr_config():
#     # important to add the filter_headers here to avoid exposing credentials
#     # in tests/cassettes!
#     return {
#         "record_mode": "once",
#         "filter_headers": ["authorization"]
#     }
# @pytest.mark.vcr

@patch('app.app.Users')
@patch('app.app.Projects')
@patch('app.app.Invoices')
@patch('app.app.Events')
@patch('app.app.Departments')
@patch('app.app.Companies')
@patch('app.app.Contacts')
@patch('app.comm.teamleader_client.TeamleaderAuth')
@patch('app.comm.teamleader_client.requests')
class TestSync:

    def test_contacts_sync(self, mock_requests, mock_auth_table, *models):
        ma = mock_auth_table.return_value
        ma.count.return_value = 0
        app = App()

        # mock requests.get so that contacts call returns something we want
        contacts = {'data': [
            # {'id':1},
            # {'id':2},
            # {'id':3}
        ]}
        mresp = Mock()
        mock_requests.get.return_value = mresp
        mresp.status_code = 200
        mresp.json.return_value = contacts
        app.contacts_sync(full_sync=True)

        assert mresp.json.call_count == 1

        # assert mock_get_contacts.call_count == 1
        # call_arg = mock_contacts.call_args[1]
        #  __import__('pdb').set_trace()
        # assert call_arg['full_sync'] is True

    def test_companies_sync(self, mock_requests, mock_auth_table, *models):
        ma = mock_auth_table.return_value
        ma.count.return_value = 0
        app = App()

        # mock requests.get so that api call returns something we want
        comp_data = {'data': []}
        mresp = Mock()
        mock_requests.get.return_value = mresp
        mresp.status_code = 200
        mresp.json.return_value = comp_data
        app.companies_sync(full_sync=True)

        assert mresp.json.call_count == 1

    def test_invoices_sync(self, mock_requests, mock_auth_table, *models):
        ma = mock_auth_table.return_value
        ma.count.return_value = 0
        app = App()

        # mock requests.get so that api call returns something we want
        inv_data = {'data': []}
        mresp = Mock()
        mock_requests.get.return_value = mresp
        mresp.status_code = 200
        mresp.json.return_value = inv_data
        app.invoices_sync(full_sync=True)

        assert mresp.json.call_count == 1

    def test_departments_sync(self, mock_requests, mock_auth_table, *models):
        ma = mock_auth_table.return_value
        ma.count.return_value = 0
        app = App()

        # mock requests.get so that api call returns something we want
        dep_data = {'data': []}
        mresp = Mock()
        mock_requests.get.return_value = mresp
        mresp.status_code = 200
        mresp.json.return_value = dep_data
        app.departments_sync(full_sync=True)

        assert mresp.json.call_count == 1

    def test_events_sync(self, mock_requests, mock_auth_table, *models):
        ma = mock_auth_table.return_value
        ma.count.return_value = 0
        app = App()

        # mock requests.get so that api call returns something we want
        ev_data = {'data': []}
        mresp = Mock()
        mock_requests.get.return_value = mresp
        mresp.status_code = 200
        mresp.json.return_value = ev_data
        app.events_sync(full_sync=True)

        assert mresp.json.call_count == 1

    def test_projects_sync(self, mock_requests, mock_auth_table, *models):
        ma = mock_auth_table.return_value
        ma.count.return_value = 0
        app = App()

        # mock requests.get so that api call returns something we want
        pr_data = {'data': []}
        mresp = Mock()
        mock_requests.get.return_value = mresp
        mresp.status_code = 200
        mresp.json.return_value = pr_data
        app.projects_sync(full_sync=True)

        assert mresp.json.call_count == 1

    def test_users_sync(self, mock_requests, mock_auth_table, *models):
        ma = mock_auth_table.return_value
        ma.count.return_value = 0
        app = App()

        # mock requests.get so that api call returns something we want
        user_data = {'data': []}
        mresp = Mock()
        mock_requests.get.return_value = mresp
        mresp.status_code = 200
        mresp.json.return_value = user_data
        app.users_sync(full_sync=True)

        assert mresp.json.call_count == 1

    def test_custom_fields(self, mock_requests, mock_auth_table, *models):
        ma = mock_auth_table.return_value
        ma.count.return_value = 0
        app = App()

        # mock requests.get so that api call returns something we want
        user_data = {'data': []}
        mresp = Mock()
        mock_requests.get.return_value = mresp
        mresp.status_code = 200
        mresp.json.return_value = user_data
        fields = app.tlc.list_custom_fields()

        assert mresp.json.call_count == 1
        assert fields == []
