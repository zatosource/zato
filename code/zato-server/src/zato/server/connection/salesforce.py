# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# requests
from requests import delete as requests_delete, get as requests_get, patch as requests_patch, post as requests_post

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dictnone, stranydict, strnone

    dictnone = dictnone
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    PathLogin = '/services/oauth2/token'
    PathBase = '/services/data/v{api_version}'
    PathDataRoot = '/services/data/'

    MethodGet = 'get'
    MethodPost = 'post'
    MethodPatch = 'patch'
    MethodDelete = 'delete'

# ################################################################################################################################
# ################################################################################################################################

_method_map = {
    ModuleCtx.MethodGet: requests_get,
    ModuleCtx.MethodPost: requests_post,
    ModuleCtx.MethodPatch: requests_patch,
    ModuleCtx.MethodDelete: requests_delete,
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
        api_version:'str',
        address:'str',
        username:'str',
        password:'str',
        consumer_key:'str',
        consumer_secret:'str',
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
        out = SalesforceClient(
            api_version = config['api_version'],
            address = config['address'],
            username = config['username'],
            password = config['password'],
            consumer_key = config['consumer_key'],
            consumer_secret = config['consumer_secret'],
        )
        return out

# ################################################################################################################################

    def _invoke_http(
        self,
        *,
        path:'str',
        data:'strnone',
        headers:'dictnone',
        params:'dictnone',
        method:'str'=ModuleCtx.MethodGet,
    ) -> 'any_':

        # Build a full URL now for the incoming request - the login path and paths
        # that already carry the API prefix, such as nextRecordsUrl values
        # from query responses, are used as they are.
        if path == ModuleCtx.PathLogin:
            path_prefix = ''
        elif path.startswith(ModuleCtx.PathDataRoot):
            path_prefix = ''
        else:
            path_prefix = ModuleCtx.PathBase.format(api_version=self.api_version)

        url = self.address + path_prefix + path

        # Invoke Salesforce now ..
        func = _method_map[method]

        response = func(url, data=data, headers=headers, params=params)

        # .. a 204 No Content answer to PATCH or DELETE carries no JSON to parse ..
        if not response.text:
            out = {}

        # .. any other response is converted to JSON ..
        else:
            out = response.json()

        # .. and returned to our caller.
        return out

# ################################################################################################################################

    def ensure_access_token_is_assigned(self) -> 'None':

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
        if not (access_token := response_json.get('access_token')):
            raise Exception(f'No Salesforce access token found in response `{response_json}`')

        self.access_token = access_token
        self.http_bearer = 'Bearer ' + self.access_token

# ################################################################################################################################

    def _send_request(
        self,
        *,
        path:'str',
        method:'str',
        data:'strnone'=None,
        headers:'dictnone'=None,
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

        out = self._invoke_http(
            path=path,
            data=data,
            headers=_headers,
            params=None,
            method=method
        )
        return out

# ################################################################################################################################

    def get(
        self,
        path:'str',
    ) -> 'any_':

        out = self._send_request(
            path=path,
            method=ModuleCtx.MethodGet,
        )
        return out

# ################################################################################################################################

    def post(
        self,
        path:'str',
        data:'dictnone'=None,
    ) -> 'any_':

        _data = dumps(data)

        out = self._send_request(
            path=path,
            data=_data,
            method=ModuleCtx.MethodPost
        )
        return out

# ################################################################################################################################

    def patch(
        self,
        path:'str',
        data:'dictnone'=None,
    ) -> 'any_':

        _data = dumps(data)

        out = self._send_request(
            path=path,
            data=_data,
            method=ModuleCtx.MethodPatch
        )
        return out

# ################################################################################################################################

    def delete(
        self,
        path:'str',
    ) -> 'any_':

        out = self._send_request(
            path=path,
            method=ModuleCtx.MethodDelete
        )
        return out

# ################################################################################################################################

    def ping(self) -> 'any_':
        """ Sends a ping-like request to Salesforce - the base path alone lists the API's resources.
        """
        out = self._send_request(
            path='/',
            method=ModuleCtx.MethodGet
        )
        return out

# ################################################################################################################################
# ################################################################################################################################
