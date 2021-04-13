#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from unittest.mock import patch, Mock, MagicMock
from app.app import App

API_URL = 'https://api.teamleader.eu'


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
@patch('app.comm.teamleader_client.TeamleaderAuth')
@patch('app.comm.teamleader_client.requests')
@patch('app.comm.teamleader_client.RATE_LIMIT_SLEEP', 0)
class TestTeamleaderClient:

    def mock_api_calls(self, *args, **kwargs):
        url = args[0]
        if '.list' in url:
            assert args[0] == f'{API_URL}/{self.resource_name}.list'
            page = kwargs['params']['page[number]']
            if page > 1:  # only mock a single page of data
                return MockResponse(200, {'data': []})
            else:
                if self.list_unauthorized:
                    self.list_unauthorized = False
                    return MockResponse(401, {'error': 'access denied'})
                else:
                    return MockResponse(200, {'data': [{'id': 'uuid1'}]})

        if '.info' in url:
            assert args[0] == f'{API_URL}/{self.resource_name}.info'

            if self.details_unauthorized:
                self.details_unauthorized = False
                return MockResponse(401, {'error': 'access denied'})
            else:
                return MockResponse(
                    200,
                    {'data': {'id': 'uuid1', 'data': 'resource data here'}}
                )

        print(
            f"ERROR UNHANDLED REQUEST \n args={args} kwargs={kwargs}",
            flush=True
        )

    def test_unauth_listing(self, mock_requests, mock_auth_table, *models):
        ma = mock_auth_table.return_value
        ma.count.return_value = 0
        app = App()
        self.list_unauthorized = True
        self.resource_name = 'contacts'
        mock_requests.get = MagicMock(side_effect=self.mock_api_calls)

        result = app.tlc.request_page(
            f'/{self.resource_name}.list',
            1, 20, None
        )

        assert result == [{'id': 'uuid1'}]
        assert not self.list_unauthorized

    def test_unauth_details(self, mock_requests, mock_auth_table, *models):
        ma = mock_auth_table.return_value
        ma.count.return_value = 0
        app = App()
        self.details_unauthorized = True
        self.resource_name = 'contacts'
        mock_requests.get = MagicMock(side_effect=self.mock_api_calls)

        result = app.tlc.request_item(
            f'/{self.resource_name}.info',
            'uuid1'
        )

        assert result == {'data': 'resource data here', 'id': 'uuid1'}
        assert not self.details_unauthorized

    def test_authcode_callback_invalid(
            self, mock_requests,
            mock_auth_table, *models):
        ma = mock_auth_table.return_value
        ma.count.return_value = 0
        app = App()
        result = app.tlc.authcode_callback('auth_code', 'wrong_state')
        assert result == 'code rejected'

    def test_authcode_callback_valid(
            self, mock_requests,
            mock_auth_table, *models):
        ma = mock_auth_table.return_value
        ma.count.return_value = 0
        app = App()
        result = app.tlc.authcode_callback(
            'auth_code',
            'code_to_validate_callback'
        )
        assert result == 'code accepted'

    def test_custom_fields(self, mock_requests, mock_auth_table, *models):
        ma = mock_auth_table.return_value
        ma.count.return_value = 0
        app = App()
        # mock requests.get so that api call returns something we want
        fields_data = {'data': []}
        mresp = Mock()
        mock_requests.get.return_value = mresp
        mresp.status_code = 200
        mresp.json.return_value = fields_data
        fields = app.tlc.list_custom_fields()

        assert mresp.json.call_count == 1
        assert fields == fields_data['data']

    def test_custom_field_get(self, mock_requests, mock_auth_table, *models):
        ma = mock_auth_table.return_value
        ma.count.return_value = 0
        app = App()
        # mock requests.get so that api call returns something we want
        field_data = {'data': {'id': 'uidhere'}}
        mresp = Mock()
        mock_requests.get.return_value = mresp
        mresp.status_code = 200
        mresp.json.return_value = field_data
        result = app.tlc.get_custom_field('uidhere')

        assert mresp.json.call_count == 1
        assert result == field_data['data']

    def test_current_user(self, mock_requests, mock_auth_table, *models):
        ma = mock_auth_table.return_value
        ma.count.return_value = 0
        app = App()
        # mock requests.get so that api call returns something we want
        user_data = {'data': {'name': 'current_user'}}
        mresp = Mock()
        mock_requests.get.return_value = mresp
        mresp.status_code = 200
        mresp.json.return_value = user_data
        result = app.tlc.current_user()

        assert mresp.json.call_count == 1
        assert result == user_data['data']
