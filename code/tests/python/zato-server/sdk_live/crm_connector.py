# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket

# Zato
from zato.common.sdk import Connector, CredentialsExpired, Field

# ################################################################################################################################
# ################################################################################################################################

class CRMClient:
    """ A client for a CRM gateway that speaks a line protocol - each request is one line of text
    and the gateway answers with one line too. A new connection is opened per request, which makes
    the client safe to share between concurrent calls.
    """
    def __init__(self, host:'str', port:'int', api_key:'str') -> 'None':
        self.host = host
        self.port = port
        self.api_key = api_key

# ################################################################################################################################

    def send(self, data:'str') -> 'str':

        # Connect for the duration of one request ..
        with socket.create_connection((self.host, self.port)) as conn:

            # .. send the request line, prefixed with the key the gateway expects ..
            request = f'{self.api_key} {data}\n'
            conn.sendall(request.encode('utf8'))

            # .. and read the response line back.
            with conn.makefile('r', encoding='utf8') as reader:
                response = reader.readline()

        out = response.strip()

        # The gateway rejected our key - the framework will refresh it and retry once.
        if out == 'error token-expired':
            raise CredentialsExpired(f'API key expired for {self.host}:{self.port}')

        return out

# ################################################################################################################################

    def renew_token(self) -> 'str':
        """ Asks the gateway for a fresh API key and returns it.
        """
        response = self.send('renew-token')
        out = response[len('token '):]
        return out

# ################################################################################################################################
# ################################################################################################################################

class CRMConnector(Connector):
    """ Wraps the CRM gateway's client as a connection type that services access through self.out.crm.
    """
    type = 'crm'

    # Configuration schema
    host = Field.Text()
    port = Field.Int(default=9950)
    api_key = Field.Secret()

# ################################################################################################################################

    def create_client(self) -> 'CRMClient':
        out = CRMClient(self.config.host, self.config.port, self.config.api_key)
        return out

# ################################################################################################################################

    def ping(self, client:'CRMClient') -> 'None':
        _ = client.send('ping')

# ################################################################################################################################

    def on_stop(self, client:'CRMClient') -> 'None':
        self.logger.info('CRM client for `%s` stopped', self.name)

# ################################################################################################################################

    def refresh_credentials(self) -> 'None':
        self.client.api_key = self.client.renew_token()
        self.logger.info('CRM key refreshed for `%s`', self.name)

# ################################################################################################################################

    def get_customer(self, customer_id:'str') -> 'str':
        out = self.client.send(f'get-customer {customer_id}')
        return out

# ################################################################################################################################
# ################################################################################################################################
