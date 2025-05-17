# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import http.client as http_client
import logging

# MSAL
import msal

# Requests
import requests

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anydictnone, dictnone, strnone

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class DataverseClient:
    """ Client for Microsoft Dataverse (formerly Common Data Service) APIs.
    """
    def __init__(
        self,
        tenant_id: 'str',
        client_id: 'str',
        client_secret: 'str',
        org_url: 'str',
        *,
        api_version: 'str' = 'v9.0'
        ) -> 'None':
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.org_url = org_url
        self.api_version = api_version
        self.token = None
        self.base_url = f'{self.org_url}/api/data/{self.api_version}'

# ################################################################################################################################

    def get_access_token(self) -> 'strnone':
        """ Obtains an OAuth access token for Dataverse API.
        """
        app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=f'https://login.microsoftonline.com/{self.tenant_id}'
        )

        scopes = [f'{self.org_url}/.default']

        result = app.acquire_token_for_client(scopes=scopes)

        if 'access_token' in result:  # type: ignore
            self.token = result['access_token']  # type: ignore
            return self.token
        else:
            raise Exception(f'Error obtaining Dataverse token: {result}')

# ################################################################################################################################

    def _get_headers(self) -> 'anydict':
        """ Returns headers required for Dataverse API requests.
        """
        if not self.token:
            self.token = self.get_access_token()

        return {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/json',
            'OData-MaxVersion': '4.0',
            'OData-Version': '4.0',
            'Content-Type': 'application/json',
        }

# ################################################################################################################################

    def _make_request(self, method: 'str', path: 'str', data: 'anydictnone'=None) -> 'dictnone':
        """ Makes an HTTP request to the Dataverse API.
        """
        url = f'{self.base_url}/{path}'
        headers = self._get_headers()
        request_func = getattr(requests, method.lower())

        if method in ('get', 'delete'):
            response = request_func(url, headers=headers)
        else:
            response = request_func(url, headers=headers, json=data)

        # Define success codes based on the request method
        if method == 'post':
            success_codes = {http_client.OK, http_client.CREATED, http_client.NO_CONTENT}
        else:
            success_codes = {http_client.OK, http_client.NO_CONTENT}

        # Check if the request was successful
        success = response.status_code in success_codes

        if not success:
            raise Exception(f'Dataverse error: {response.status_code} -> {repr(response.text)}')

        # Return appropriate response based on content
        if response.content:
            return response.json()

# ################################################################################################################################

    def get(self, path: 'str') -> 'dictnone':
        """ Performs a GET request to the Dataverse API.
        """
        return self._make_request('get', path)

# ################################################################################################################################

    def post(self, path: 'str', data: 'anydict') -> 'dictnone':
        """ Performs a POST request to the Dataverse API.
        """
        return self._make_request('post', path, data)

# ################################################################################################################################

    def patch(self, path: 'str', data: 'anydict') -> 'dictnone':
        """ Performs a PATCH request to the Dataverse API.
        """
        return self._make_request('patch', path, data)

# ################################################################################################################################

    def delete(self, path: 'str') -> 'dictnone':
        """ Performs a DELETE request to the Dataverse API.
        """
        return self._make_request('delete', path)

# ################################################################################################################################
# ################################################################################################################################
