#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from unittest.mock import patch, Mock  # , MagicMock
from app.app import App


# class MockResponse:
#     def __init__(self, code, data):
#         self.status_code = code
#         self.data = data
#
#     def json(self):
#         return self.data


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

    # def mock_api_calls(self, *args, **kwargs):
    #    url = args[0]
    #    if '.list' in url:
    #        assert args[0] == f'api_uri/{self.resource_name}.list'
    #        page = kwargs['params']['page[number]']
    #        if page > 1:  # only mock a single page of data
    #            response = MockResponse(200, {'data': []})
    #        else:
    #            response = MockResponse(200, {'data': [{'id': 'uuid1'}]})
    #    elif '.info' in url:
    #        assert args[0] == f'api_uri/{self.resource_name}.info'
    #        response = MockResponse(
    #            200, {'data': {'id': 'uuid1', 'data': 'company data here'}})
    #    else:
    #        print(f"\n args={args} kwargs={kwargs}", flush=True)

    #    return response

    # def test_contacts_sync(self, mock_requests, mock_auth_table, *models):
    #    ma = mock_auth_table.return_value
    #    ma.count.return_value = 0
    #    app = App()

    #    self.resource_name = 'contacts'
    #    mock_requests.get = MagicMock(side_effect=self.mock_api_calls)
    #    app.contacts_sync(full_sync=True)

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
