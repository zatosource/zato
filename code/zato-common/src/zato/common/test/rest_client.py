# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http.client import OK
from json import dumps, loads
from time import sleep

# Bunch
from bunch import Bunch, bunchify

# Requests
import requests

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test import BaseZatoTestCase
from zato.common.test.config import TestConfig
from zato.sso import status_code

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from requests import Response
    from zato.common.typing_ import any_, anydictnone, anytuple, callable_, optional
    anytuple = anytuple
    callable_ = callable_
    optional = optional
    Response = Response

# ################################################################################################################################
# ################################################################################################################################

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class RESTClientTestCase(BaseZatoTestCase):

    needs_bunch = True
    needs_current_app = True
    payload_only_messages = True

    def __init__(self, *args, **kwargs) -> 'None': # type: ignore
        super().__init__(*args, **kwargs)
        self.rest_client = RESTClient(self.needs_bunch, self.needs_current_app, self.payload_only_messages)

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

class RESTClient:

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
        self._api_invoke_password = ''
        self._auth = None

        self.base_address = '<invalid-base-address>'

# ################################################################################################################################

    def init(self, /, username:'str'='', sec_name:'str'='') -> 'None':

        # Zato
        from zato.common.util.cli import get_zato_sh_command

        username = username or 'pubapi'
        sec_name = sec_name or 'pubapi'

        # Assign for later use
        self._api_invoke_username = username

        # A shortcut
        command = get_zato_sh_command()

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

        # .. reset the password now ..
        command('service', 'invoke', TestConfig.server_location,
            'zato.security.basic-auth.change-password', '--payload', payload)

        sleep(4)

        # .. and store the credentials for later use.
        self._auth = (self._api_invoke_username, self._api_invoke_password)

# ################################################################################################################################

    def _invoke(
        self,
        func,      # type: callable_
        func_name, # type: str
        url_path,  # type: str
        request,   # type: any_
        expect_ok, # type: bool
        auth=None, # type: optional[anytuple]
        qs=None,    # type: anydictnone
        _unexpected=object() # type: any_
        ) -> 'Bunch':

        if self.base_address != TestConfig.invalid_base_address:
            base_adddress = self.base_address
        else:
            base_adddress = TestConfig.server_address

        address = base_adddress.format(url_path)

        if self.needs_current_app:
            if request:
                request['current_app'] = TestConfig.current_app

        data = dumps(request) if request else ''
        auth = auth or self._auth

        logger.info('Invoking %s %s with %s (%s) (%s)', func_name, address, data, auth, qs)
        response = func(address, data=data, auth=auth, params=qs) # type: Response

        logger.info('Response received %s %s', response.status_code, response.text)

        # Most tests require for responses to indicate a successful invocation
        if expect_ok:

            # This checks HTTP headers only
            if response.status_code != OK:
                raise Exception('Unexpected response.status_code found in response_data `{}` ({})'.format(
                    response.text, response.status_code))

            if response.text:
                response_data = loads(response.text)
                if self.needs_bunch:
                    response_data = bunchify(response_data)
            else:
                response_data = response.text

            # This is used if everything about the response is in the payload itself,
            # e.g. HTTP headers are not used to signal or relay anything.
            if self.payload_only_messages:
                cid = response_data.get('cid', _unexpected)
                if cid is _unexpected:
                    raise Exception('Unexpected CID found in response `{}`'.format(response.text))
                if response_data['status'] != status_code.ok:
                    raise Exception('Unexpected response_data.status found in response `{}` ({})'.format(
                        response.text, response_data['status']))

        # We are here if expect_ok is not True
        else:
            if response.text:
                response_data = loads(response.text)
                response_data = bunchify(response_data)
            else:
                response_data = response.text

        return response_data

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

    def post(self, url_path:'str', request:'any_'='', expect_ok:'bool'=True, auth:'any_'=None) -> 'Bunch':
        return self._invoke(requests.post, 'POST', url_path, request, expect_ok, auth)

# ################################################################################################################################

    def patch(self, url_path:'str', request:'str'='', expect_ok:'bool'=True, auth:'any_'=None) -> 'Bunch':
        return self._invoke(requests.patch, 'PATCH', url_path, request, expect_ok, auth)

# ################################################################################################################################

    def delete(self, url_path:'str', request:'str'='', expect_ok:'bool'=True, auth:'any_'=None, qs:'anydictnone'=None) -> 'Bunch':
        qs = qs or {}
        return self._invoke(requests.delete, 'DELETE', url_path, request, expect_ok, auth, qs)

# ################################################################################################################################
# ################################################################################################################################
