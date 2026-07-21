# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import ACCEPTED, CREATED, NO_CONTENT, OK, UNAUTHORIZED
from logging import getLogger
from time import time

# Requests
import requests

# Zato
from zato.common.api import MicrosoftFabric
from zato.common.const import SECRETS
from zato.common.typing_ import cast_, tuple_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from requests import Response
    from zato.common.typing_ import anydict, anydictnone, bytesnone, stranydict, strnone

# ################################################################################################################################
# ################################################################################################################################

# A bearer token together with the time when it expires, as seconds since the Unix epoch.
token_info = tuple_[str, float]

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_default = MicrosoftFabric.Default

# How many seconds before a token's expiration time we already treat it as expired,
# which makes sure we never send a token that expires mid-flight.
_token_refresh_margin_seconds = 60

# Status codes that indicate a successful response, depending on the HTTP method used.
_success_codes = {
    'GET':    {OK, NO_CONTENT},
    'POST':   {OK, CREATED, ACCEPTED, NO_CONTENT},
    'PATCH':  {OK, ACCEPTED, NO_CONTENT},
    'PUT':    {OK, CREATED, ACCEPTED, NO_CONTENT},
    'DELETE': {OK, ACCEPTED, NO_CONTENT},
}

# ################################################################################################################################
# ################################################################################################################################

class MicrosoftFabricClient:
    """ Client for Microsoft Fabric APIs, using the OAuth2 client credentials grant.
    """
    def __init__(self, config:'stranydict') -> 'None':

        self.config = config
        self.name = config['name']
        self.tenant_id = config['tenant_id']
        self.client_id = config['client_id']

        # The secret lives in the secret column, except for connections created
        # before it moved there, which keep it in the opaque attributes.
        client_secret = config.get('secret')
        if (not client_secret) or client_secret.startswith(SECRETS.Auto_Generated_Prefix):
            client_secret = config['client_secret']
        self.client_secret = client_secret

        # The base address of the Fabric API - fall back to the public cloud if none was given on input.
        if address := config.get('address'):
            self.address = address.rstrip('/')
        else:
            self.address = _default.Address

        # The base address of the OneLake data plane - by default, it points to the public cloud,
        # while tests point it to their own servers.
        if onelake_address := config.get('onelake_address'):
            self.onelake_address = onelake_address.rstrip('/')
        else:
            self.onelake_address = _default.OneLake_Address

        # The endpoint that issues OAuth2 tokens - by default, it is derived from the tenant ID,
        # while tests point it to their own token servers.
        if token_url := config.get('token_url'):
            self.token_url = token_url
        else:
            self.token_url = f'{_default.Login_URL}/{self.tenant_id}/oauth2/v2.0/token'

        # A single session shared by all the requests this client makes.
        self.session = requests.Session()

        # The current OAuth2 bearer token for the Fabric API - it is obtained lazily, on the first request that needs it.
        self.token:'strnone' = None

        # When the current API token expires, as seconds since the Unix epoch.
        self.token_expires_at = 0.0

        # The current OAuth2 bearer token for the OneLake data plane - it uses the storage scope
        # and is likewise obtained lazily, on the first OneLake request.
        self.onelake_token:'strnone' = None

        # When the current OneLake token expires, as seconds since the Unix epoch.
        self.onelake_token_expires_at = 0.0

# ################################################################################################################################

    def _acquire_token_for_scope(self, scope:'str') -> 'token_info':
        """ Obtains a new OAuth2 bearer token for the given scope using the client credentials grant.
        """
        request_data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': scope,
        }

        # Ask the token endpoint for a new token ..
        response = self.session.post(self.token_url, data=request_data)

        # .. anything other than 200 OK means the credentials were rejected ..
        if response.status_code != OK:
            raise Exception(f'Fabric token error ({self.name}): {response.status_code} -> {repr(response.text)}')

        token_response = response.json()

        # .. extract the token itself ..
        token = token_response['access_token']

        # .. and compute when it expires, leaving a safety margin.
        now = time()
        expires_in = token_response['expires_in']
        expires_at = now + expires_in - _token_refresh_margin_seconds

        out = (token, expires_at)
        return out

# ################################################################################################################################

    def _acquire_token(self) -> 'None':
        """ Obtains a new OAuth2 bearer token for the Fabric API.
        """
        self.token, self.token_expires_at = self._acquire_token_for_scope(_default.Scope)

# ################################################################################################################################

    def _acquire_onelake_token(self) -> 'None':
        """ Obtains a new OAuth2 bearer token for the OneLake data plane.
        """
        self.onelake_token, self.onelake_token_expires_at = self._acquire_token_for_scope(_default.OneLake_Scope)

# ################################################################################################################################

    def _ensure_token(self) -> 'None':
        """ Makes sure a valid, non-expired API token is available.
        """

        # There is no token yet - get one.
        if not self.token:
            self._acquire_token()
            return

        # There is a token but it has expired - get a new one.
        now = time()
        if now >= self.token_expires_at:
            self._acquire_token()

# ################################################################################################################################

    def _ensure_onelake_token(self) -> 'None':
        """ Makes sure a valid, non-expired OneLake token is available.
        """

        # There is no token yet - get one.
        if not self.onelake_token:
            self._acquire_onelake_token()
            return

        # There is a token but it has expired - get a new one.
        now = time()
        if now >= self.onelake_token_expires_at:
            self._acquire_onelake_token()

# ################################################################################################################################

    def _get_headers(self) -> 'anydict':
        """ Returns the headers each Fabric API request needs.
        """
        return {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

# ################################################################################################################################

    def _get_onelake_headers(self) -> 'anydict':
        """ Returns the headers each OneLake data plane request needs.
        """
        return {
            'Authorization': f'Bearer {self.onelake_token}',
        }

# ################################################################################################################################

    def invoke(self, method:'str', path:'str', params:'anydictnone'=None, data:'anydictnone'=None) -> 'anydictnone':
        """ Invokes any Fabric endpoint, returning the parsed JSON response, if there was any.
        """

        # Make sure we have a token to send ..
        self._ensure_token()

        # .. build the full address of the endpoint ..
        url = f'{self.address}{path}'

        # .. invoke the endpoint ..
        headers = self._get_headers()
        response = self.session.request(method, url, headers=headers, params=params, json=data)

        # .. a 401 means our token was rejected, e.g. it was revoked server-side,
        # .. so obtain a new one and retry the request once ..
        if response.status_code == UNAUTHORIZED:
            self._acquire_token()
            headers = self._get_headers()
            response = self.session.request(method, url, headers=headers, params=params, json=data)

        # .. anything outside the success range for this method is an error ..
        success_codes = _success_codes[method]
        if response.status_code not in success_codes:
            raise Exception(f'Fabric error ({self.name}): {response.status_code} -> {repr(response.text)}')

        # .. and hand back the parsed response, if the endpoint returned one.
        if response.content:
            out = response.json()
            return out

# ################################################################################################################################

    def get(self, path:'str', params:'anydictnone'=None) -> 'anydictnone':
        """ Performs a GET request against the Fabric API.
        """
        out = self.invoke('GET', path, params=params)
        return out

# ################################################################################################################################

    def post(self, path:'str', data:'anydictnone'=None, params:'anydictnone'=None) -> 'anydictnone':
        """ Performs a POST request against the Fabric API.
        """
        out = self.invoke('POST', path, params=params, data=data)
        return out

# ################################################################################################################################

    def patch(self, path:'str', data:'anydictnone'=None, params:'anydictnone'=None) -> 'anydictnone':
        """ Performs a PATCH request against the Fabric API.
        """
        out = self.invoke('PATCH', path, params=params, data=data)
        return out

# ################################################################################################################################

    def delete(self, path:'str', params:'anydictnone'=None) -> 'anydictnone':
        """ Performs a DELETE request against the Fabric API.
        """
        out = self.invoke('DELETE', path, params=params)
        return out

# ################################################################################################################################

    def list_workspaces(self) -> 'anydict':
        """ Returns all the workspaces the connection's principal has access to.
        """
        response = self.get('/workspaces')

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def get_workspace(self, workspace_id:'str') -> 'anydict':
        """ Returns details of a single workspace.
        """
        response = self.get(f'/workspaces/{workspace_id}')

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def create_workspace(self, name:'str', description:'str'='') -> 'anydict':
        """ Creates a new workspace.
        """
        request_data = {'displayName': name}
        if description:
            request_data['description'] = description

        response = self.post('/workspaces', data=request_data)

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def delete_workspace(self, workspace_id:'str') -> 'None':
        """ Deletes a workspace.
        """
        _ = self.delete(f'/workspaces/{workspace_id}')

# ################################################################################################################################

    def list_items(self, workspace_id:'str', item_type:'str'='') -> 'anydict':
        """ Returns items in a workspace, optionally filtered by their type, e.g. Lakehouse or Notebook.
        """
        if item_type:
            params = {'type': item_type}
        else:
            params = None

        response = self.get(f'/workspaces/{workspace_id}/items', params=params)

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def get_item(self, workspace_id:'str', item_id:'str') -> 'anydict':
        """ Returns details of a single item in a workspace.
        """
        response = self.get(f'/workspaces/{workspace_id}/items/{item_id}')

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def create_item(self, workspace_id:'str', name:'str', item_type:'str', description:'str'='') -> 'anydict':
        """ Creates a new item in a workspace, e.g. a lakehouse or a notebook.
        """
        request_data = {'displayName': name, 'type': item_type}
        if description:
            request_data['description'] = description

        response = self.post(f'/workspaces/{workspace_id}/items', data=request_data)

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def update_item(self, workspace_id:'str', item_id:'str', data:'anydict') -> 'anydict':
        """ Updates an item in a workspace, e.g. its display name or description.
        """
        response = self.patch(f'/workspaces/{workspace_id}/items/{item_id}', data=data)

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def delete_item(self, workspace_id:'str', item_id:'str') -> 'None':
        """ Deletes an item from a workspace.
        """
        _ = self.delete(f'/workspaces/{workspace_id}/items/{item_id}')

# ################################################################################################################################

    def run_job(self, workspace_id:'str', item_id:'str', job_type:'str', payload:'anydictnone'=None) -> 'anydictnone':
        """ Runs an item's job on demand, e.g. executes a notebook or a data pipeline.
        """
        params = {'jobType': job_type}
        out = self.post(f'/workspaces/{workspace_id}/items/{item_id}/jobs/instances', data=payload, params=params)

        return out

# ################################################################################################################################

    def get_job(self, workspace_id:'str', item_id:'str', job_id:'str') -> 'anydict':
        """ Returns details of a single job instance of an item.
        """
        response = self.get(f'/workspaces/{workspace_id}/items/{item_id}/jobs/instances/{job_id}')

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def cancel_job(self, workspace_id:'str', item_id:'str', job_id:'str') -> 'None':
        """ Cancels a job instance of an item.
        """
        _ = self.post(f'/workspaces/{workspace_id}/items/{item_id}/jobs/instances/{job_id}/cancel')

# ################################################################################################################################

    def list_shortcuts(self, workspace_id:'str', item_id:'str') -> 'anydict':
        """ Returns OneLake shortcuts defined in an item.
        """
        response = self.get(f'/workspaces/{workspace_id}/items/{item_id}/shortcuts')

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def create_shortcut(self, workspace_id:'str', item_id:'str', data:'anydict') -> 'anydict':
        """ Creates a OneLake shortcut in an item.
        """
        response = self.post(f'/workspaces/{workspace_id}/items/{item_id}/shortcuts', data=data)

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def delete_shortcut(self, workspace_id:'str', item_id:'str', shortcut_path:'str', shortcut_name:'str') -> 'None':
        """ Deletes a OneLake shortcut from an item.
        """
        _ = self.delete(f'/workspaces/{workspace_id}/items/{item_id}/shortcuts/{shortcut_path}/{shortcut_name}')

# ################################################################################################################################

    def list_capacities(self) -> 'anydict':
        """ Returns all the capacities the connection's principal has access to.
        """
        response = self.get('/capacities')

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def _invoke_onelake(
        self,
        method:'str',
        path:'str',
        params:'anydictnone'=None,
        data:'bytesnone'=None,
        ) -> 'Response':
        """ Invokes a OneLake data plane endpoint, retrying once if the token was rejected.
        """

        # Make sure we have a OneLake token to send ..
        self._ensure_onelake_token()

        # .. build the full address of the endpoint ..
        url = f'{self.onelake_address}{path}'

        # .. invoke the endpoint ..
        headers = self._get_onelake_headers()
        response = self.session.request(method, url, headers=headers, params=params, data=data)

        # .. a 401 means our token was rejected, e.g. it was revoked server-side,
        # .. so obtain a new one and retry the request once ..
        if response.status_code == UNAUTHORIZED:
            self._acquire_onelake_token()
            headers = self._get_onelake_headers()
            response = self.session.request(method, url, headers=headers, params=params, data=data)

        # .. anything outside the success range for this method is an error ..
        success_codes = _success_codes[method]
        if response.status_code not in success_codes:
            raise Exception(f'OneLake error ({self.name}): {response.status_code} -> {repr(response.text)}')

        out = response
        return out

# ################################################################################################################################

    def onelake_list(self, workspace_id:'str', directory:'str'='') -> 'anydict':
        """ Lists paths in a workspace's OneLake filesystem, optionally under a specific directory.
        """
        params = {'resource': 'filesystem', 'recursive': 'false'}
        if directory:
            params['directory'] = directory

        response = self._invoke_onelake('GET', f'/{workspace_id}', params=params)

        out = response.json()
        return out

# ################################################################################################################################

    def onelake_read(self, workspace_id:'str', file_path:'str') -> 'bytes':
        """ Reads a file from a workspace's OneLake filesystem.
        """
        response = self._invoke_onelake('GET', f'/{workspace_id}/{file_path}')

        out = response.content
        return out

# ################################################################################################################################

    def onelake_write(self, workspace_id:'str', file_path:'str', data:'bytes') -> 'None':
        """ Writes a file to a workspace's OneLake filesystem, creating it or overwriting it.
        """

        # First, create the file itself ..
        _ = self._invoke_onelake('PUT', f'/{workspace_id}/{file_path}', params={'resource': 'file'})

        # .. append the data to it ..
        append_params = {'action': 'append', 'position': '0'}
        _ = self._invoke_onelake('PATCH', f'/{workspace_id}/{file_path}', params=append_params, data=data)

        # .. and flush it, which makes the data visible to readers.
        data_length = len(data)
        flush_params = {'action': 'flush', 'position': str(data_length)}
        _ = self._invoke_onelake('PATCH', f'/{workspace_id}/{file_path}', params=flush_params)

# ################################################################################################################################

    def onelake_delete(self, workspace_id:'str', file_path:'str') -> 'None':
        """ Deletes a file from a workspace's OneLake filesystem.
        """
        _ = self._invoke_onelake('DELETE', f'/{workspace_id}/{file_path}')

# ################################################################################################################################

    def zato_delete_impl(self, reason:'str'='') -> 'None':
        """ Closes the underlying HTTP session when the connection is deleted. Having this method here
        also makes sure the queue's teardown never conflicts with the public .delete method above.
        """
        self.session.close()

# ################################################################################################################################

    def ping(self) -> 'None':
        """ Confirms that the connection's credentials are valid by listing its workspaces.
        """
        response = self.list_workspaces()
        workspaces = response['value']

        workspace_count = len(workspaces)
        suffix = 'workspace' if workspace_count == 1 else 'workspaces'

        logger.info('Microsoft Fabric ping OK (%s) -> %d %s', self.name, workspace_count, suffix)

# ################################################################################################################################
# ################################################################################################################################
