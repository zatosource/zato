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
from zato.common.api import MicrosoftPowerAutomate
from zato.common.const import SECRETS
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anydictnone, stranydict, strnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_default = MicrosoftPowerAutomate.Default

# How many seconds before a token's expiration time we already treat it as expired,
# which makes sure we never send a token that expires mid-flight.
_token_refresh_margin_seconds = 60

# Status codes that indicate a successful response, depending on the HTTP method used.
_success_codes = {
    'GET':    {OK, NO_CONTENT},
    'POST':   {OK, CREATED, ACCEPTED, NO_CONTENT},
    'PATCH':  {OK, NO_CONTENT},
    'DELETE': {OK, ACCEPTED, NO_CONTENT},
}

# ################################################################################################################################
# ################################################################################################################################

class MicrosoftPowerAutomateClient:
    """ Client for Microsoft Power Automate APIs, using the OAuth2 client credentials grant.
    """
    def __init__(self, config:'stranydict') -> 'None':

        self.config = config
        self.name = config['name']
        self.tenant_id = config['tenant_id']
        self.client_id = config['client_id']
        self.environment_id = config['environment_id']

        # The secret lives in the secret column, except for connections created
        # before it moved there, which keep it in the opaque attributes.
        client_secret = config.get('secret')
        if (not client_secret) or client_secret.startswith(SECRETS.Auto_Generated_Prefix):
            client_secret = config['client_secret']
        self.client_secret = client_secret

        # The base address of the Power Automate API - fall back to the public cloud if none was given on input.
        if address := config.get('address'):
            self.address = address.rstrip('/')
        else:
            self.address = _default.Address

        # The endpoint that issues OAuth2 tokens - by default, it is derived from the tenant ID,
        # while tests point it to their own token servers.
        if token_url := config.get('token_url'):
            self.token_url = token_url
        else:
            self.token_url = f'{_default.Login_URL}/{self.tenant_id}/oauth2/v2.0/token'

        # A single session shared by all the requests this client makes.
        self.session = requests.Session()

        # The current OAuth2 bearer token - it is obtained lazily, on the first request that needs it.
        self.token:'strnone' = None

        # When the current token expires, as seconds since the Unix epoch.
        self.token_expires_at = 0.0

# ################################################################################################################################

    def _acquire_token(self) -> 'None':
        """ Obtains a new OAuth2 bearer token using the client credentials grant.
        """
        request_data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': _default.Scope,
        }

        # Ask the token endpoint for a new token ..
        response = self.session.post(self.token_url, data=request_data)

        # .. anything other than 200 OK means the credentials were rejected ..
        if response.status_code != OK:
            raise Exception(f'Power Automate token error ({self.name}): {response.status_code} -> {repr(response.text)}')

        token_response = response.json()

        # .. store the token itself ..
        self.token = token_response['access_token']

        # .. and remember when it expires, leaving a safety margin.
        now = time()
        expires_in = token_response['expires_in']
        self.token_expires_at = now + expires_in - _token_refresh_margin_seconds

# ################################################################################################################################

    def _ensure_token(self) -> 'None':
        """ Makes sure a valid, non-expired token is available.
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

    def _get_headers(self) -> 'anydict':
        """ Returns the headers each Power Automate API request needs.
        """
        return {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

# ################################################################################################################################

    def invoke(self, method:'str', path:'str', params:'anydictnone'=None, data:'anydictnone'=None) -> 'anydictnone':
        """ Invokes any Power Automate endpoint, returning the parsed JSON response, if there was any.
        """

        # Make sure we have a token to send ..
        self._ensure_token()

        # .. build the full address of the endpoint ..
        url = f'{self.address}{path}'

        # .. each request carries the API version unless the caller chose one explicitly ..
        query_params = {'api-version': _default.API_Version}
        if params:
            query_params.update(params)

        # .. invoke the endpoint ..
        headers = self._get_headers()
        response = self.session.request(method, url, headers=headers, params=query_params, json=data)

        # .. a 401 means our token was rejected, e.g. it was revoked server-side,
        # .. so obtain a new one and retry the request once ..
        if response.status_code == UNAUTHORIZED:
            self._acquire_token()
            headers = self._get_headers()
            response = self.session.request(method, url, headers=headers, params=query_params, json=data)

        # .. anything outside the success range for this method is an error ..
        success_codes = _success_codes[method]
        if response.status_code not in success_codes:
            raise Exception(f'Power Automate error ({self.name}): {response.status_code} -> {repr(response.text)}')

        # .. and hand back the parsed response, if the endpoint returned one.
        if response.content:
            out = response.json()
            return out

# ################################################################################################################################

    def get(self, path:'str', params:'anydictnone'=None) -> 'anydictnone':
        """ Performs a GET request against the Power Automate API.
        """
        out = self.invoke('GET', path, params=params)
        return out

# ################################################################################################################################

    def post(self, path:'str', data:'anydictnone'=None, params:'anydictnone'=None) -> 'anydictnone':
        """ Performs a POST request against the Power Automate API.
        """
        out = self.invoke('POST', path, params=params, data=data)
        return out

# ################################################################################################################################

    def patch(self, path:'str', data:'anydictnone'=None, params:'anydictnone'=None) -> 'anydictnone':
        """ Performs a PATCH request against the Power Automate API.
        """
        out = self.invoke('PATCH', path, params=params, data=data)
        return out

# ################################################################################################################################

    def delete(self, path:'str', params:'anydictnone'=None) -> 'anydictnone':
        """ Performs a DELETE request against the Power Automate API.
        """
        out = self.invoke('DELETE', path, params=params)
        return out

# ################################################################################################################################

    def _get_environment_path(self) -> 'str':
        """ Returns the URL path prefix of the environment this connection points to.
        """
        out = f'/providers/Microsoft.ProcessSimple/environments/{self.environment_id}'
        return out

# ################################################################################################################################

    def list_flows(self) -> 'anydict':
        """ Returns all the flows in the connection's environment.
        """
        environment_path = self._get_environment_path()
        response = self.get(f'{environment_path}/flows')

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def get_flow(self, flow_id:'str') -> 'anydict':
        """ Returns details of a single flow.
        """
        environment_path = self._get_environment_path()
        response = self.get(f'{environment_path}/flows/{flow_id}')

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def enable_flow(self, flow_id:'str') -> 'None':
        """ Turns a flow on.
        """
        environment_path = self._get_environment_path()
        _ = self.post(f'{environment_path}/flows/{flow_id}/start')

# ################################################################################################################################

    def disable_flow(self, flow_id:'str') -> 'None':
        """ Turns a flow off.
        """
        environment_path = self._get_environment_path()
        _ = self.post(f'{environment_path}/flows/{flow_id}/stop')

# ################################################################################################################################

    def list_runs(self, flow_id:'str') -> 'anydict':
        """ Returns the run history of a flow.
        """
        environment_path = self._get_environment_path()
        response = self.get(f'{environment_path}/flows/{flow_id}/runs')

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def get_run(self, flow_id:'str', run_id:'str') -> 'anydict':
        """ Returns details of a single run of a flow.
        """
        environment_path = self._get_environment_path()
        response = self.get(f'{environment_path}/flows/{flow_id}/runs/{run_id}')

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def cancel_run(self, flow_id:'str', run_id:'str') -> 'None':
        """ Cancels a run of a flow.
        """
        environment_path = self._get_environment_path()
        _ = self.post(f'{environment_path}/flows/{flow_id}/runs/{run_id}/cancel')

# ################################################################################################################################

    def resubmit_run(self, flow_id:'str', run_id:'str', trigger_name:'str'=_default.Trigger_Name) -> 'None':
        """ Resubmits a run of a flow, which makes the flow execute again with the same trigger data.
        """
        environment_path = self._get_environment_path()
        _ = self.post(f'{environment_path}/flows/{flow_id}/triggers/{trigger_name}/histories/{run_id}/resubmit')

# ################################################################################################################################

    def get_trigger_url(self, flow_id:'str', trigger_name:'str'=_default.Trigger_Name) -> 'str':
        """ Returns the callback URL of a flow's HTTP request trigger.
        """
        environment_path = self._get_environment_path()
        response = self.post(f'{environment_path}/flows/{flow_id}/triggers/{trigger_name}/listCallbackUrl')
        response = cast_('anydict', response)

        # The URL itself is nested in the response.
        response_data = response['response']

        out = response_data['value']
        return out

# ################################################################################################################################

    def trigger(self, flow_id:'str', payload:'anydictnone'=None, trigger_name:'str'=_default.Trigger_Name) -> 'anydictnone':
        """ Runs an instant flow by sending a payload to its HTTP request trigger.
        """

        # First, look up the trigger's callback URL ..
        url = self.get_trigger_url(flow_id, trigger_name)

        # .. and then invoke it with the payload given on input.
        out = self.trigger_url(url, payload)
        return out

# ################################################################################################################################

    def trigger_url(self, url:'str', payload:'anydictnone'=None) -> 'anydictnone':
        """ Runs an instant flow by sending a payload directly to a trigger's callback URL.
        The URL carries its own authorization so no bearer token is needed.
        """
        response = self.session.post(url, json=payload)

        # Anything outside the POST success range is an error ..
        success_codes = _success_codes['POST']
        if response.status_code not in success_codes:
            raise Exception(f'Power Automate trigger error ({self.name}): {response.status_code} -> {repr(response.text)}')

        # .. otherwise, hand back the parsed response, if the flow returned one.
        if response.content:
            out = response.json()
            return out

# ################################################################################################################################

    def ping(self) -> 'None':
        """ Confirms that the connection's credentials and environment are valid by listing its flows.
        """
        response = self.list_flows()
        flows = response['value']

        flow_count = len(flows)
        suffix = 'flow' if flow_count == 1 else 'flows'

        logger.info('Microsoft Power Automate ping OK (%s) -> %d %s', self.name, flow_count, suffix)

# ################################################################################################################################
# ################################################################################################################################
