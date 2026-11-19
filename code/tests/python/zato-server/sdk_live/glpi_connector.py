# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import UNAUTHORIZED

# requests
import requests

# Zato
from zato.common.sdk import Connector, CredentialsExpired, Field

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from requests import Response
    from zato.common.typing_ import anydict, anydictnone, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# The error code GLPI returns when a session expired or was closed
_session_token_invalid = 'ERROR_SESSION_TOKEN_INVALID'

# ################################################################################################################################
# ################################################################################################################################

class GLPIClient:
    """ A client for the GLPI REST API - it opens a session with the application token
    and the user token, and each request after that includes the session token.
    """
    def __init__(self, address:'str', app_token:'str', user_token:'str') -> 'None':
        self.api_url = f'{address}/apirest.php'
        self.user_token = user_token
        self.session_token = ''

        # Every request to GLPI includes the application token.
        self.http = requests.Session()
        self.http.headers['App-Token'] = app_token

# ################################################################################################################################

    def _send(self, method:'str', path:'str', headers:'strstrdict', data:'anydictnone'=None) -> 'Response':

        # Send the request ..
        response = self.http.request(method, f'{self.api_url}/{path}', headers=headers, json=data)

        # .. GLPI describes an error as a list of its code and message ..
        if not response.ok:
            error_code, error_message = response.json()

            # .. an expired session is renewed by the platform, which then retries the call ..
            if response.status_code == UNAUTHORIZED and error_code == _session_token_invalid:
                raise CredentialsExpired(f'GLPI session expired at {self.api_url}')

            # .. and any other error goes to the caller.
            else:
                raise Exception(f'GLPI returned {response.status_code} {error_code} - {error_message}')

        return response

# ################################################################################################################################

    def init_session(self) -> 'None':

        # Exchange the user token for a new session ..
        headers = {'Authorization': f'user_token {self.user_token}'}
        response = self._send('GET', 'initSession', headers)

        # .. and keep its token for the requests that follow.
        self.session_token = response.json()['session_token']

# ################################################################################################################################

    def call(self, method:'str', path:'str', data:'anydictnone'=None) -> 'Response':
        headers = {'Session-Token': self.session_token}
        out = self._send(method, path, headers, data)
        return out

# ################################################################################################################################

    def close_session(self) -> 'None':
        _ = self.call('GET', 'killSession')

# ################################################################################################################################

    def get_item(self, item_type:'str', item_id:'int') -> 'anydict':
        response = self.call('GET', f'{item_type}/{item_id}')
        out = response.json()
        return out

# ################################################################################################################################

    def create_item(self, item_type:'str', fields:'anydict') -> 'int':
        response = self.call('POST', item_type, {'input': fields})
        out = response.json()['id']
        return out

# ################################################################################################################################
# ################################################################################################################################

class GLPIConnector(Connector):
    """ Wraps the GLPI REST API as a connection type that services access through self.out.glpi.
    """
    type = 'glpi'

    # Configuration schema
    address = Field.Text()
    app_token = Field.Secret()
    user_token = Field.Secret()

# ################################################################################################################################

    def create_client(self) -> 'GLPIClient':
        out = GLPIClient(self.config.address, self.config.app_token, self.config.user_token)
        out.init_session()
        return out

# ################################################################################################################################

    def ping(self, client:'GLPIClient') -> 'None':
        _ = client.call('GET', 'getFullSession')

# ################################################################################################################################

    def validate(self, client:'GLPIClient') -> 'None':
        """ Sends nothing before a call - an expired session is renewed when a call reports it.
        """

# ################################################################################################################################

    def refresh_credentials(self) -> 'None':
        self.client.init_session()
        self.logger.info('GLPI session renewed for `%s`', self.name)

# ################################################################################################################################

    def on_stop(self, client:'GLPIClient') -> 'None':
        client.close_session()

# ################################################################################################################################

    def get_ticket(self, ticket_id:'int') -> 'anydict':
        out = self.client.get_item('Ticket', ticket_id)
        return out

# ################################################################################################################################

    def create_ticket(self, name:'str', content:'str') -> 'int':
        out = self.client.create_item('Ticket', {'name': name, 'content': content})
        return out

# ################################################################################################################################
# ################################################################################################################################
