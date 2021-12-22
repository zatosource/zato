# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http.client import OK
from json import dumps, loads
from unittest import TestCase

# Bunch
from bunch import Bunch, bunchify

# Requests
import requests

# sh
import sh

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.config import TestConfig
from zato.sso import status_code

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from requests import Response
    from zato.common.typing_ import any_, anytuple, callable_, optional

# ################################################################################################################################
# ################################################################################################################################

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class RESTClientTestCase(TestCase):

    needs_bunch = True
    needs_current_app = True
    payload_only_messages = True

    def __init__(self, *args, **kwargs) -> 'None': # type: ignore
        super().__init__(*args, **kwargs)
        self.rest_client = _RESTClient(self.needs_bunch, self.needs_current_app, self.payload_only_messages)

# ################################################################################################################################

    def api_invoke(self, *args, **kwargs) -> 'any_':
        return self.rest_client.api_invoke(*args, **kwargs)

# ################################################################################################################################

    def get(self, *args, **kwargs): # type: ignore
        return self.rest_client.get(*args, **kwargs)

# ################################################################################################################################

    def post(self, *args, **kwargs): # type: ignore
        return self.rest_client.post(*args, **kwargs)

# ################################################################################################################################

    def patch(self, *args, **kwargs): # type: ignore
        return self.rest_client.patch(*args, **kwargs)

# ################################################################################################################################

    def delete(self, *args, **kwargs): # type: ignore
        return self.rest_client.delete(*args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################

class _RESTClient:

    def __init__(
        self,
        needs_bunch=True,          # type: bool
        needs_current_app=True,    # type: bool
        payload_only_messages=True # type: bool
        ) -> 'None':
        self.needs_bunch = needs_bunch
        self.needs_current_app = needs_current_app
        self.payload_only_messages = payload_only_messages

        self._api_invoke_username = 'pubapi'
        self._api_invoke_password = 'p6Ig-UuwGQzgM85kH3y1J8dS6_l8JpjG'

# ################################################################################################################################

    def init(self) -> 'None':
        return

        # Local aliases
        sec_name = 'pubapi'

        # A shortcut
        command = sh.zato # type: ignore

        # Generate a new password ..
        self._api_invoke_password = CryptoManager.generate_password().decode('utf8')

        # .. wrap everything in a dict ..
        payload = {
            'name': sec_name,
            'password1': self._api_invoke_password,
            'password2': self._api_invoke_password,
        }

        # .. serialise to JSON, as expected by the CLI ..
        payload = dumps(payload)

        # .. log what we are about to do ..
        logger.info('Changing password for HTTP Basic Auth `%s`', sec_name)

        # .. and reset the password now.
        command('service', 'invoke', TestConfig.server_location,
            'zato.security.basic-auth.change-password', '--payload', payload)

# ################################################################################################################################

    def _invoke(
        self,
        func,      # type: callable_
        func_name, # type: str
        url_path,  # type: str
        request,   # type: any_
        expect_ok, # type: bool
        auth=None, # type: optional[anytuple]
        _unexpected=object() # type: any_
        ) -> 'Bunch':

        address = TestConfig.server_address.format(url_path)
        if self.needs_current_app:
            request['current_app'] = TestConfig.current_app
        data = dumps(request)

        logger.info('Invoking %s %s with %s', func_name, address, data)
        response = func(address, data=data, auth=auth) # type: Response

        logger.info('Response received %s %s', response.status_code, response.text)

        data = loads(response.text)

        if self.needs_bunch:
            data = bunchify(data)

        # Most SSO tests require status OK and CID
        if expect_ok:

            # This is used if everything about the response is in the payload itself,
            # e.g. HTTP headers are not used to signal or relay anything.
            if self.payload_only_messages:
                cid = data.get('cid', _unexpected)
                if cid is _unexpected:
                    raise Exception('Unexpected CID found in response `{}`'.format(response.text))
                if data['status'] != status_code.ok:
                    raise Exception('Unexpected data.status found in response `{}` ({})'.format(response.text, data['status']))

            # This checks HTTP headers only
            if response.status_code != OK:
                raise Exception('Unexpected response.status_code found in request `{}` ({})'.format(
                    response.text, response.status_code))

        return data

# ################################################################################################################################

    def api_invoke(self, service:'str', request:'any_'=None) -> 'any_':

        prefix = '/zato/api/invoke/'
        url_path = prefix + service
        auth = (self._api_invoke_username, self._api_invoke_password)

        return self.post(url_path, request or {}, auth=auth)

# ################################################################################################################################

    def get(self, url_path:'str', request:'str'='', expect_ok:'bool'=True, auth:'any_'=None) -> 'Bunch':
        return self._invoke(requests.get, 'GET', url_path, request, expect_ok, auth)

# ################################################################################################################################

    def post(self, url_path:'str', request:'str'='', expect_ok:'bool'=True, auth:'any_'=None) -> 'Bunch':
        return self._invoke(requests.post, 'POST', url_path, request, expect_ok, auth)

# ################################################################################################################################

    def patch(self, url_path:'str', request:'str'='', expect_ok:'bool'=True, auth:'any_'=None) -> 'Bunch':
        return self._invoke(requests.patch, 'PATCH', url_path, request, expect_ok, auth)

# ################################################################################################################################

    def delete(self, url_path:'str', request:'str'='', expect_ok:'bool'=True, auth:'any_'=None) -> 'Bunch':
        return self._invoke(requests.delete, 'DELETE', url_path, request, expect_ok, auth)

# ################################################################################################################################
# ################################################################################################################################
