# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import ACCEPTED, CREATED, NO_CONTENT, OK, UNAUTHORIZED
from logging import getLogger
from time import monotonic, sleep, time

# Requests
import requests

# Zato
from zato.common.api import MicrosoftFabric
from zato.common.audit_log.calls import record_remote_call
from zato.common.audit_log.common import AuditSource
from zato.common.const import SECRETS
from zato.common.typing_ import cast_, tuple_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from requests import Response
    from zato.common.typing_ import anydict, anydictnone, bytesnone, stranydict, strnone, strstrdict

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
_operation_status = MicrosoftFabric.Operation_Status

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

class MicrosoftFabricBase:
    """ The Fabric client's plumbing - tokens, HTTP requests, long-running operations and the OneLake data plane.
    """
    def __init__(self, config:'stranydict') -> 'None':

        self.config = config
        self.name = config['name']
        self.tenant_id = config['tenant_id']
        self.client_id = config['client_id']

        # The secret column may hold the real secret or an auto-generated placeholder ..
        client_secret = config.get('secret')

        # .. a placeholder is not a credential, so it counts as no secret at all ..
        if client_secret:
            if client_secret.startswith(SECRETS.Auto_Generated_Prefix):
                client_secret = ''

        # .. and when there is no secret in the column, it lives in the opaque attributes.
        if not client_secret:
            client_secret = config['client_secret']

        self.client_secret = client_secret

        # The base address of the Fabric API - the public cloud address is the default.
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

        # One shared Spark session per lakehouse, keyed by workspace ID and lakehouse ID.
        self._spark_sessions:'strstrdict' = {}

        # The audit log every call is recorded in - the wrapper attaches it after construction
        self.zato_audit_log = None

# ################################################################################################################################

    def _record_call(self, url:'str', start:'float', error:'str'='') -> 'None':
        """ Records one completed call as an audit event - what the alerting collectors
        read. A client with no audit log attached, e.g. one built in a test, records nothing.
        """
        if self.zato_audit_log is None:
            return

        duration_ms = int((monotonic() - start) * 1000)

        record_remote_call(self.zato_audit_log, AuditSource.Microsoft_Cloud, self.name,
            is_ok=not error, duration_ms=duration_ms, status=error, endpoint=url)

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

    def invoke_raw(self, method:'str', path:'str', params:'anydictnone'=None, data:'anydictnone'=None) -> 'Response':
        """ Invokes any Fabric endpoint and returns the whole response, headers included.
        """

        # The path may already be a full URL, e.g. a Location header or a continuation URI.
        if path.startswith(('https://', 'http://')):
            url = path
        else:
            url = f'{self.address}{path}'

        start = monotonic()

        # A failed call is recorded too, before the caller learns about it
        try:

            # Make sure we have a token to send ..
            self._ensure_token()

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

        except Exception as e:
            self._record_call(url, start, str(e))
            raise

        self._record_call(url, start)

        out = response
        return out

# ################################################################################################################################

    def invoke(self, method:'str', path:'str', params:'anydictnone'=None, data:'anydictnone'=None) -> 'anydictnone':
        """ Invokes any Fabric endpoint, returning the parsed JSON response, if there was any.
        """
        response = self.invoke_raw(method, path, params=params, data=data)

        # Hand back the parsed response, if the endpoint returned one.
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

    def get_operation(self, location:'str') -> 'anydict':
        """ Returns the current state of a long-running operation, given the address of its status endpoint.
        """
        response = self.get(location)

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def wait_for_operation(
        self,
        location:'str',
        timeout:'int'=_default.Operation_Timeout,
        interval:'float'=_default.Operation_Poll_Interval,
        ) -> 'anydict':
        """ Waits until a long-running operation completes and returns its final state.
        """
        deadline = monotonic() + timeout

        while True:

            # Check where the operation stands now ..
            operation = self.get_operation(location)
            status = operation['status']

            # .. a completed operation goes back to the caller ..
            if status == _operation_status.Succeeded:
                out = operation
                return out

            # .. a failed one ends with an exception ..
            if status == _operation_status.Failed:
                raise Exception(f'Fabric operation failed ({self.name}) -> {operation}')

            # .. give up if the operation did not complete in time ..
            now = monotonic()
            if now >= deadline:
                raise Exception(f'Fabric operation timed out after {timeout}s ({self.name}) -> {location}')

            # .. otherwise, wait before the next check.
            sleep(interval)

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

        # The full address of the endpoint - built first so a failure can be recorded against it
        url = f'{self.onelake_address}{path}'

        start = monotonic()

        # A failed call is recorded too, before the caller learns about it
        try:

            # Make sure we have a OneLake token to send ..
            self._ensure_onelake_token()

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

        except Exception as e:
            self._record_call(url, start, str(e))
            raise

        self._record_call(url, start)

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
# ################################################################################################################################
