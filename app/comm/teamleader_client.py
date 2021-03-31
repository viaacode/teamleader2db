#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
import time
# from datetime import datetime, timezone

class TeamleaderClient:
    """Acts as a client to query relevant information from Teamleader API"""

    def __init__(self, params: dict,):
        self.auth_uri = params['auth_uri']
        self.api_uri = params['api_uri']
        self.client_id = params['client_id']
        self.client_secret = params['client_secret']
        self.redirect_uri = params['redirect_uri']
        self.code = params['code'] # TODO: fetch code from db, as this overrides the default
        self.token = params['auth_token'] # TODO: fetch from db, as this is more recent
        self.refresh_token = params['refresh_token'] # TODO: fetch from db, as this is more recent
        self.code_callback_completed = True

    def auth_code_request(self):
        """ First request that results in a callback to redirect_uri that supplies a code
        for auth_token_request """
        
        # we need to poll the self.code that should change after a callback
        self.code_callback_completed = False

        # this call initiates a callback to our fast-api
        # which in turn calls auth_code_callback
        auth_uri = self.auth_uri + '/oauth2/authorize'
        requests.get(auth_uri, params={
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri
        })

        # bail out after 20 seconds
        tries = 1
        while not self.code_callback_completed:
            if tries % 100 == 0:
                raise Exception("auth_code_request timed out.")
            time.sleep(0.2)
            tries += 1


    # todo this should be linked to a route from api, 
    # and then this route is to be set in redirect_uri
    def auth_code_callback(self, code):
        self.code_callback_completed = True
        self.code = code

    def auth_token_request(self):
        """ use when auth_token_refresh fails """
        r = requests.post(
            self.auth_uri + '/oauth2/access_token',
            params={
                'code': self.code,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': self.redirect_uri,
                'grant_type': 'authorization_code'
            }
        )

        response = r.json()
        print("auth_token_request response=", response, flush=True)
        self.token = response['access_token'] # expires in 1 hour
        self.refresh_token = response['refresh_token']

        # TODO: if this fails, use auth_code_request to get new code to request new tokens

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

        response = r.json()
        print("auth_token_refresh response status =", r.status_code, flush=True)
        self.token = response['access_token'] # expires in 1 hour
        self.refresh_token = response['refresh_token']

        # TODO: if this fails, use auth_token_request to get new code to request new tokens
        # TODO: store new tokens here in database table auth_table!!!
        print("auth_token:", self.token, flush=True)
        print("\nrefresh_token:", self.refresh_token, flush=True)


    def get_page(self, resource_path, page=None, page_size=None):
        path = self.api_uri + resource_path
        headers = {'Authorization': "Bearer {}".format(self.token)} 
        params = {}
        if page or page_size:
            if not page:
                page=1
            if not page_size:
                page_size=20

            params = {
                'page[number]': page,
                'page[size]': page_size
            }

        res = requests.get(path, params=params, headers=headers)
        if res.status_code == 401:
            self.auth_token_refresh()
            headers = {'Authorization': "Bearer {}".format(self.token)} 
            res = requests.get(path, params=params, headers=headers)
                   
        if res.status_code == 200:
            return res.json()['data']
        else:
            print("call to {} failed status_code".format(path, res.status_code))
            __import__('pdb').set_trace()


    def list_companies(self, page=1, page_size=20):
        return self.get_page('/companies.list', page, page_size)

    def list_contacts(self, page=1, page_size=20):
        return self.get_page('/contacts.list', page, page_size)


    def list_departments(self, page=1, page_size=20):
        return self.get_page('/departments.list', page, page_size)

    def list_events(self, page=1, page_size=20):
        return self.get_page('/events.list', page, page_size)

    def list_invoices(self, page=1, page_size=20):
        return self.get_page('/invoices.list', page, page_size)

    def list_projects(self, page=1, page_size=20):
        return self.get_page('/projects.list', page, page_size)

    def list_users(self, page=1, page_size=20):
        return self.get_page('/users.list', page, page_size)

    def current_user(self):
        return self.get_page('/users.me')

