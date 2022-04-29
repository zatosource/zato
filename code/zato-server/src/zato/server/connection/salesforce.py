# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# requests
from requests import get as request_get, post as requests_post

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, dictnone, stranydict, strnone

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    PathLogin = '/services/oauth2/token'
    PathPing = '/services/data/v{api_version}/'

    MethodGet = 'get'
    MethodPost = 'post'

# ################################################################################################################################
# ################################################################################################################################

method_map = {
    ModuleCtx.MethodGet: request_get,
    ModuleCtx.MethodPost: requests_post,
}

# ################################################################################################################################
# ################################################################################################################################

class SalesforceClient:

    api_version: 'str'
    address: 'str'
    username: 'str'
    password: 'str'
    consumer_key: 'str'
    consumer_secret: 'str'
    access_token: 'str'
    http_bearer: 'str'

    def __init__(
        self,
        *,
        api_version, # type: str
        address, # type: str
        username, # type: str
        password, # type: str
        consumer_key, # type: str
        consumer_secret, # type: str
    ) -> 'None':

        self.api_version = api_version
        self.address = address
        self.username = username
        self.password = password
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

# ################################################################################################################################

    @staticmethod
    def from_config(config:'stranydict') -> 'SalesforceClient':
        return SalesforceClient(
            api_version = config[''],
            address = config[''],
            username = config[''],
            password = config[''],
            consumer_key = config[''],
            consumer_secret = config[''],
        )

# ################################################################################################################################

    def _invoke_http(
        self,
        *,
        path,    # type: str
        data,    # type: strnone
        headers, # type: dictnone
        params,  # type: dictnone
        method=ModuleCtx.MethodGet,  # type: str
    ) -> 'anydict':

        # Build a full URL now for the upcoming request.
        url = self.address + path

        # Invoke Salesforce now ..
        func = method_map[method]

        '''
        print()
        print('QQQ-1', func)
        print('QQQ-2', url)
        print('QQQ-3', data)
        '''

        response = func(url, data=data, headers=headers, params=params)

        print(111, response)
        print(222, response.text)
        print()

        # .. convert the response to JSON ..
        response_json = response.json()

        # .. and return it to our caller.
        return response_json

# ################################################################################################################################

    def ensure_access_token_is_assigned(self):

        # This information is sent in headers ..
        headers = {
            'X-PrettyPrint': '1',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        # .. while this goes to POST parameters.
        params = {
            'grant_type': 'password',
            'username': self.username,
            'password': self.password,
            'client_id': self.consumer_key,
            'client_secret': self.consumer_secret,
        }

        # .. obtain a JSON response ..
        response_json = self._invoke_http(
            path=ModuleCtx.PathLogin,
            data=None,
            headers=headers,
            params=params,
            method=ModuleCtx.MethodPost
        )

        # .. and try extract the access token now for later use.
        access_token = response_json.get('access_token')
        if not access_token:
            raise Exception('No Salesforce access token found in response `{}`)'.format(response_json))
        else:
            self.access_token = access_token
            self.http_bearer = 'Bearer ' + self.access_token

# ################################################################################################################################

    def _send_request(
        self,
        *,
        path,   # type: str
        method, # type: str
        data=None, # type: strnone
        headers=None, # type: dictnone
    ) -> 'any_':

        # Before sending the request, make sure we have an access token to authenticate with.
        self.ensure_access_token_is_assigned()

        # Headers required for the request.
        _headers = {
            'X-PrettyPrint': '1',
            'Authorization': self.http_bearer,
            'Content-Type':'application/json'
        }

        if headers:
            _headers.update(headers)

        return self._invoke_http(
            path=path,
            data=data,
            headers=_headers,
            params=None,
            method=method
        )

# ################################################################################################################################

    def get(
        self,
        path, # type: str
    ) -> 'any_':

        return self._send_request(
            path=path,
            method=ModuleCtx.MethodGet,
        )

# ################################################################################################################################

    def post(
        self,
        path,      # type: str
        data=None, # type: dictnone
    ) -> 'any_':

        _data = dumps(data)

        return self._send_request(
            path=path,
            data=_data,
            method=ModuleCtx.MethodPost
        )

# ################################################################################################################################

    def ping(self):
        """ Sends a ping-like request to Salesforce.
        """
        return self._send_request(
            path=ModuleCtx.PathPing,
            method=ModuleCtx.MethodGet
        )

# ################################################################################################################################
# ################################################################################################################################
