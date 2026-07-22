# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
import time

# Zato
from zato.common.sdk import Connector, Field

# ################################################################################################################################
# ################################################################################################################################

# How long to wait for the helper process to start accepting connections, in seconds.
_startup_timeout = 15

# ################################################################################################################################
# ################################################################################################################################

class InventoryClient:
    """ A client for the inventory system, which is a Java component - the connector runs its jar
    as a helper process and this client talks to it over a local socket, one connection per request.
    """
    def __init__(self, host:'str', port:'int') -> 'None':
        self.host = host
        self.port = port

# ################################################################################################################################

    def send(self, data:'str') -> 'str':

        # Connect for the duration of one request ..
        with socket.create_connection((self.host, self.port)) as conn:
            conn.sendall(f'{data}\n'.encode('utf8'))

            # .. and read the response line back.
            with conn.makefile('r', encoding='utf8') as reader:
                response = reader.readline()

        out = response.strip()
        return out

# ################################################################################################################################
# ################################################################################################################################

class InventoryConnector(Connector):
    """ Wraps a Java inventory component - a jar run and supervised as a helper process
    that services access through self.out.inventory.
    """
    type = 'inventory'

    # Configuration schema
    jar_path = Field.Text()

# ################################################################################################################################

    def create_client(self) -> 'InventoryClient':

        # Run the jar as a supervised helper process - the '{port}' placeholder carries
        # the local port allocated for it (6.9).
        process = self.start_process(['java', '-jar', self.config.jar_path, '{port}'])

        client = InventoryClient('127.0.0.1', process.port)

        # The JVM needs a moment before it accepts connections.
        deadline = time.monotonic() + _startup_timeout

        while True:
            try:
                _ = client.send('hello')
            except OSError:
                if time.monotonic() > deadline:
                    raise Exception(f'The inventory helper did not start within {_startup_timeout}s')
                time.sleep(0.2)
            else:
                break

        self.logger.info('Inventory helper started for `%s` (pid %s)', self.name, process.pid)
        return client

# ################################################################################################################################

    def ping(self, client:'InventoryClient') -> 'None':
        _ = client.send('ping')

# ################################################################################################################################

    def get_stock(self, item:'str') -> 'str':
        out = self.client.send(f'stock {item}')
        return out

# ################################################################################################################################
# ################################################################################################################################
