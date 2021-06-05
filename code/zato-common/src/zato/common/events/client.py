# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import socket
from logging import basicConfig, getLogger

# Zato
from zato.common.events.common import Action
from zato.common.util.api import new_cid
from zato.common.util.tcp import read_from_socket, SocketReaderCtx, wait_until_port_taken

# ################################################################################################################################
# ################################################################################################################################

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Client:
    def __init__(self, host, port):
        # type: (str, int) -> None
        self.host = host
        self.port = port
        self.socket = socket.socket(type=socket.SOCK_STREAM)
        self.peer_name = '<Client-peer_name-default>'
        self.conn_id = 'zstrcl' + new_cid(bytes=4)
        self.max_wait_time = 30
        self.max_msg_size = 30_000_000
        self.read_buffer_size = 30_000_000
        self.recv_timeout = 30
        self.should_log_messages = True

# ################################################################################################################################

    def connect(self):
        self.socket.connect((self.host, self.port))
        self.peer_name = self.socket.getpeername()

# ################################################################################################################################

    def send(self, data):
        # type: (bytes) -> None
        self.socket.sendall(data + b'\n')

# ################################################################################################################################

    def ping(self):
        logger.info('Pinging %s (%s)', self.peer_name)

        # Send the ping message ..
        self.send(Action.Ping)

        # .. build a receive context ..
        ctx = SocketReaderCtx(
            self.conn_id,
            self.socket,
            self.max_wait_time,
            self.max_msg_size,
            self.read_buffer_size,
            self.recv_timeout,
            self.should_log_messages
        )

        # .. wait for the reply ..
        response = read_from_socket(ctx)

        # .. and raise an exception in case of any error.
        print()
        print(111, response)
        print()

# ################################################################################################################################

    def close(self):
        self.socket.close()

# ################################################################################################################################

    def run(self):

        # Make sure that we have a port to connect to ..
        wait_until_port_taken(self.port, 10)

        # .. do connect now ..
        self.connect()

        # .. and ping the remote end to confirm that we have connectivity.
        self.ping()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    from time import sleep

    host = '127.0.0.1'
    port = 34567

    client = Client(host, port)
    client.run()
    client.close()

    sleep(2)

# ################################################################################################################################
# ################################################################################################################################
