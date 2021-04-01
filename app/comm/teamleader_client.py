#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
# from datetime import datetime, timezone
# json

# WARNING: watch out for rate limit of 100 calls per minute !
# it will give HTTP 429 Too Many Requests error
# to avoid hitting the rate limit for now:
RATE_LIMIT_SLEEP = 0.6


class TeamleaderClient:
    """Acts as a client to query relevant information from Teamleader API"""

    def __init__(self, params: dict,):
        self.auth_uri = params['auth_uri']
        self.api_uri = params['api_uri']
        self.client_id = params['client_id']
        self.client_secret = params['client_secret']
        self.redirect_uri = params['redirect_uri']
        # TODO: fetch code, auth_token, refresh_token from db, as this overrides the default
        self.code = params['code']
        self.token = params['auth_token']
        self.refresh_token = params['refresh_token']
        self.secret_code_state = params['secret_code_state']

    def authcode_request_link(self):
        """ First request that results in a callback to redirect_uri that supplies a code
        for auth_token_request """

        # returns link to be opened in browser (that is also logged in into teamleader)
        # this then shows a page to allow/deny access and that makes a callback to
        # authcode_callback

        # we can't further automate/send it from here as the backend is not logged in
        # teamleader and has no session + we can't click on the 'accept' button on the
        # webpage. well we could do it with something like chrome selenium but that is
        # out of scope here.
        # auth_params = {
        #     'client_id': self.client_id,
        #     'response_type': 'code',
        #     'redirect_uri': self.redirect_uri,
        #     'state': self.secret_code_state
        # }
        # auth_result = requests.get(auth_uri, params=auth_params)

        auth_uri = self.auth_uri + '/oauth2/authorize'
        link = "{}?client_id={}&response_type=code&redirect_uri={}&state={}".format(
            auth_uri,
            self.client_id,
            self.redirect_uri,
            self.secret_code_state
        )

        return link

    # after user follows the authcode_request_link from above. we handle
    # the callback here, and update our tokens.
    # called with api route: /sync/oauth?code='supplied_by_teamleader'&state='self.secret_code_state'

    def authcode_callback(self, code, state):
        print(f"received callback: code={code} state={state}", flush=True)
        if state != self.secret_code_state:
            return "code rejected"

        try:
            self.code = code
            # self.code is updated, new fetch new token and refresh_token
            self.auth_token_request()
            return "code accepted"

        except ValueError as e:
            return 'code rejected: '+str(e)

    def handle_token_response(self, token_response):
        if token_response.status_code == 200:
            response = token_response.json()
            self.token = response['access_token']  # expires in 1 hour
            self.refresh_token = response['refresh_token']

            # TODO: store new tokens in database table auth_table!!!
            print("auth_token:", self.token, flush=True)
            print("\nrefresh_token:", self.refresh_token, flush=True)
        else:
            print(
                f"Error {token_response.status_code}: {token_response.text} in handle_token_response",
                flush=True
            )
            print(
                f"Login into teamleader and paste link in browser: {self.authcode_request_link()}",
                flush=True
            )

    def auth_token_request(self):
        """ use when auth_token_refresh fails """
        req_uri = self.auth_uri + '/oauth2/access_token'
        req_params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': self.code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        r = requests.post(req_uri, data=req_params)
        time.sleep(RATE_LIMIT_SLEEP)
        self.handle_token_response(r)

    def auth_token_refresh(self):
        """ to be called whenever we get 401 from expiry on api calls """
        r = requests.post(
            self.auth_uri + '/oauth2/access_token',
            data={
                'refresh_token': self.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': self.redirect_uri,
                'grant_type': 'refresh_token'
            }
        )
        time.sleep(RATE_LIMIT_SLEEP)
        self.handle_token_response(r)

    def request_page(self, resource_path, page=None, page_size=None, updated_since=None):
        path = self.api_uri + resource_path
        headers = {'Authorization': "Bearer {}".format(self.token)}
        params = {}
        if page:
            params['page[number]'] = page

        if page_size:
            params['page[size]'] = page_size

        if updated_since:
            # ex: '2021-03-29T16:44:33+00:00'
            params['filter[updated_since]'] = updated_since

        res = requests.get(path, params=params, headers=headers)
        if res.status_code == 401:
            self.auth_token_refresh()
            headers = {'Authorization': "Bearer {}".format(self.token)}
            res = requests.get(path, params=params, headers=headers)

        time.sleep(RATE_LIMIT_SLEEP)

        if res.status_code == 200:
            return res.json()['data']
        else:
            print('call to {} failed with code {}'.format(
                path, res.status_code), flush=True)
            return []

    def list_companies(self, page=1, page_size=20, updated_since=None):
        return self.request_page('/companies.list', page, page_size, updated_since)

    def list_contacts(self, page=1, page_size=20, updated_since=None):
        return self.request_page('/contacts.list', page, page_size, updated_since)

    def list_departments(self, page=1, page_size=20, updated_since=None):
        # departments has no pagination! we want a similar interface however,
        # so if page==2 we return []. otherwise our sync goes into infinite loop
        # as the page param is ignored here and we always get back 3 of the same deps.
        print(
            f"list_departments: page={page} size={page_size} updated_since={updated_since}")
        if page > 1:
            return []
        else:
            return self.request_page('/departments.list', page, page_size, updated_since)

    def list_events(self, page=1, page_size=20, updated_since=None):
        return self.request_page('/events.list', page, page_size, updated_since)

    def list_invoices(self, page=1, page_size=20, updated_since=None):
        return self.request_page('/invoices.list', page, page_size, updated_since)

    def list_projects(self, page=1, page_size=20, updated_since=None):
        return self.request_page('/projects.list', page, page_size, updated_since)

    def list_users(self, page=1, page_size=20, updated_since=None):
        return self.request_page('/users.list', page, page_size, updated_since)

    def current_user(self):
        return self.request_page('/users.me')
