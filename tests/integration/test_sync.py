#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from unittest.mock import patch, MagicMock
from app.app import App

API_URL = 'https://api.focus.teamleader.eu'


class MockResponse:
    def __init__(self, code, data):
        self.status_code = code
        self.data = data

    def json(self):
        return self.data


@patch('app.app.Users')
@patch('app.app.Projects')
@patch('app.app.Invoices')
@patch('app.app.Events')
@patch('app.app.Departments')
@patch('app.app.Companies')
@patch('app.app.Contacts')
@patch('app.app.CustomFields')
@patch('app.comm.teamleader_client.TeamleaderAuth')
@patch('app.comm.teamleader_client.requests')
@patch('app.comm.teamleader_client.RATE_LIMIT_SLEEP', 0)
class TestSync:

    def mock_api_calls(self, *args, **kwargs):
        url = args[0]
        if '.list' in url:
            assert args[0] == f'{API_URL}/{self.resource_name}.list'
            page = kwargs['params']['page[number]']
            if page > 1:  # only mock a single page of data
                response = MockResponse(200, {'data': []})
            else:
                response = MockResponse(200, {'data': [{'id': 'uuid1'}]})
        elif '.info' in url:
            assert args[0] == f'{API_URL}/{self.resource_name}.info'
            response = MockResponse(
                200, {'data': {'id': 'uuid1', 'data': 'api response data here'}})
        else:
            print(f"\n args={args} kwargs={kwargs}", flush=True)

        return response

    def test_contacts_sync(self, mock_requests, mock_auth_table, *models):
        ma = mock_auth_table.return_value
        ma.count.return_value = 0
        app = App()

        self.resource_name = 'contacts'
        mock_requests.get = MagicMock(side_effect=self.mock_api_calls)
        app.contacts_sync(full_sync=True)

    def test_companies_sync(self, mock_requests, mock_auth_table, *models):
        ma = mock_auth_table.return_value
        ma.count.return_value = 0
        app = App()

        self.resource_name = 'companies'
        mock_requests.get = MagicMock(side_effect=self.mock_api_calls)
        app.companies_sync(full_sync=True)

    def test_invoices_sync(self, mock_requests, mock_auth_table, *models):
        ma = mock_auth_table.return_value
        ma.count.return_value = 0
        app = App()

        self.resource_name = 'invoices'
        mock_requests.get = MagicMock(side_effect=self.mock_api_calls)
        app.invoices_sync(full_sync=True)

    def test_departments_sync(self, mock_requests, mock_auth_table, *models):
        ma = mock_auth_table.return_value
        ma.count.return_value = 0
        app = App()

        self.resource_name = 'departments'
        mock_requests.get = MagicMock(side_effect=self.mock_api_calls)
        app.departments_sync(full_sync=True)

    def test_events_sync(self, mock_requests, mock_auth_table, *models):
        ma = mock_auth_table.return_value
        ma.count.return_value = 0
        app = App()

        self.resource_name = 'events'
        mock_requests.get = MagicMock(side_effect=self.mock_api_calls)
        app.events_sync(full_sync=True)

    def test_projects_sync(self, mock_requests, mock_auth_table, *models):
        ma = mock_auth_table.return_value
        ma.count.return_value = 0
        app = App()

        self.resource_name = 'projects'
        mock_requests.get = MagicMock(side_effect=self.mock_api_calls)
        app.projects_sync(full_sync=True)

    def test_users_sync(self, mock_requests, mock_auth_table, *models):
        ma = mock_auth_table.return_value
        ma.count.return_value = 0
        app = App()

        self.resource_name = 'users'
        mock_requests.get = MagicMock(side_effect=self.mock_api_calls)
        app.users_sync(full_sync=True)
