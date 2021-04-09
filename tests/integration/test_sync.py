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

class TestSync:
    def test_contacts_sync(self):

        pass
        return

        print("before app instantiation", flush=True)
        app = App()
        mock_contacts = patch('app.tlc.requests.get')
        contacts = []
        mock_get_contacts = mock_contacts.start()

        mock_get_contacts.return_value = Mock(status_code=200)
        mock_get_contacts.return_value.json = contacts

        print("before full sync call", flush=True)
        app.contacts_sync(full_sync=False)
        print("done", flush=True)

        mock_contacts.stop()

        # ... this is gonna get messy, we need to mock a lot more this way

        # assert 1==2
        # assert mock_get_contacts.call_count == 1
        # call_arg = mock_contacts.call_args[1]
        #  __import__('pdb').set_trace()
        # assert call_arg['full_sync'] is True
