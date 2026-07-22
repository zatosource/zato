# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
import subprocess
import time

# Zato
from zato.common.sdk import Connector, Field

# ################################################################################################################################
# ################################################################################################################################

# How long to wait for the CLI tool to start serving its local API, in seconds.
_startup_timeout = 15

# How long a one-shot command may take, in seconds.
_command_timeout = 30

# ################################################################################################################################
# ################################################################################################################################

class TunnelClient:
    """ Talks to the long-lived CLI tool's local API over a socket, one connection per request -
    the way tools like ngrok expose what they know about their tunnels.
    """
    def __init__(self, host:'str', port:'int') -> 'None':
        self.host = host
        self.port = port

# ################################################################################################################################

    def send(self, data:'str') -> 'str':

        with socket.create_connection((self.host, self.port)) as conn:
            conn.sendall(f'{data}\n'.encode('utf8'))

            with conn.makefile('r', encoding='utf8') as reader:
                response = reader.readline()

        out = response.strip()
        return out

# ################################################################################################################################
# ################################################################################################################################

class TunnelConnector(Connector):
    """ Wraps a CLI tool both ways at once - the long-lived session runs as a supervised helper
    process the connection's whole life, the way an ngrok tunnel would, and one-shot commands
    are plain methods that run the binary and return its output.
    """
    type = 'tunnel'

    # Configuration schema
    binary_path = Field.Text()

# ################################################################################################################################

    def create_client(self) -> 'TunnelClient':

        # The long-lived session starts with the connection and dies with it - deleting
        # the definition stops the tunnel (3.3).
        process = self.start_process([self.config.binary_path, 'serve', '{port}'])

        client = TunnelClient('127.0.0.1', process.port)

        # The tool needs a moment before its local API accepts connections.
        deadline = time.monotonic() + _startup_timeout

        while True:
            try:
                _ = client.send('address')
            except OSError:
                if time.monotonic() > deadline:
                    raise Exception(f'The tunnel did not start within {_startup_timeout}s')
                time.sleep(0.2)
            else:
                break

        self.logger.info('Tunnel started for `%s` (pid %s)', self.name, process.pid)
        return client

# ################################################################################################################################

    def ping(self, client:'TunnelClient') -> 'None':
        _ = client.send('address')

# ################################################################################################################################

    def get_address(self) -> 'str':
        """ The tunnel's address, read from the tool's local API.
        """
        out = self.client.send('address')
        return out

# ################################################################################################################################

    def get_status(self, name:'str') -> 'str':
        """ A one-shot command wrapped as a client method - run the binary, return its output.
        """
        result = subprocess.run(
            [self.config.binary_path, 'status', name],
            capture_output=True, text=True, timeout=_command_timeout, check=True)

        out = result.stdout.strip()
        return out

# ################################################################################################################################
# ################################################################################################################################
