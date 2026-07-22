# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket

# Zato
from zato.common.sdk import ConnectionLost, Field, PooledConnector

# ################################################################################################################################
# ################################################################################################################################

class MainframeConnection:
    """ One connection to a mainframe gateway that requires a logon handshake first and then
    holds a conversation, one call at a time - which is why a connection can never be shared
    between concurrent calls and the framework pools them instead.
    """
    def __init__(self, host:'str', port:'int', logon_token:'str') -> 'None':

        # Connect and keep the socket open for the connection's whole life ..
        self.socket = socket.create_connection((host, port))
        self.reader = self.socket.makefile('r', encoding='utf8')

        # .. log on first - the gateway answers with the session it assigned ..
        self._send_line(f'logon {logon_token}')
        response = self.reader.readline().strip()

        # .. anything other than an ok reply means the logon was rejected.
        if not response.startswith('ok '):
            raise Exception(f'Logon failed -> {response}')

        self.session_id = response[len('ok '):]

# ################################################################################################################################

    def _send_line(self, data:'str') -> 'None':
        self.socket.sendall(f'{data}\n'.encode('utf8'))

# ################################################################################################################################

    def send(self, data:'str') -> 'str':
        self._send_line(data)
        out = self.reader.readline().strip()
        return out

# ################################################################################################################################

    def close(self) -> 'None':
        self.reader.close()
        self.socket.close()

# ################################################################################################################################
# ################################################################################################################################

class MainframeConnector(PooledConnector):
    """ Wraps the mainframe gateway as a connection type that services access through self.out.mainframe.
    """
    type = 'mainframe'

    # Configuration schema
    host = Field.Text()
    port = Field.Int(default=9960)
    logon_token = Field.Secret()

# ################################################################################################################################

    def create_client(self) -> 'MainframeConnection':
        conn = MainframeConnection(self.config.host, self.config.port, self.config.logon_token)
        self.logger.info('Mainframe session `%s` logged on for `%s`', conn.session_id, self.name)
        return conn

# ################################################################################################################################

    def ping(self, conn:'MainframeConnection') -> 'None':

        # A dead socket answers with an empty line - the framework will discard the connection.
        response = conn.send('ping')
        if not response.endswith('ping'):
            raise ConnectionLost(f'The gateway did not answer a ping -> {response!r}')

# ################################################################################################################################

    def on_stop(self, conn:'MainframeConnection') -> 'None':
        conn.close()
        self.logger.info('Mainframe session `%s` closed for `%s`', conn.session_id, self.name)

# ################################################################################################################################

    def on_get_from_pool(self, conn:'MainframeConnection') -> 'None':
        self.logger.info('Mainframe session `%s` taken from pool', conn.session_id)

# ################################################################################################################################

    def on_return_to_pool(self, conn:'MainframeConnection') -> 'None':
        self.logger.info('Mainframe session `%s` returned to pool', conn.session_id)

# ################################################################################################################################

    def send_command(self, command:'str') -> 'str':

        # Each call borrows one connection for its whole duration - the gateway speaks
        # one call at a time per session, so the connection is never shared.
        with self.get_connection() as conn:
            out = conn.send(command)

        return out

# ################################################################################################################################
# ################################################################################################################################
