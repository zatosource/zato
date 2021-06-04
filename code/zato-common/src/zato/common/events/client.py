# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from logging import getLogger

# Zato
from zato.common.events.common import Action
from zato.common.util.tcp import SocketReaderCtx, wait_until_port_taken

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

        print()
        print(111, self.socket)
        print()

        '''
        self.conn_id =
        socket
        max_wait_time
        max_msg_size
        read_buffer_size
        recv_timeout
        should_log_messages
        '''

    def connect(self):
        self.socket.connect((self.host, self.port))

    def ping(self):
        logger.info('PING')

        # Send the ping message ..
        #self.socket.sendall(Action.Ping)

        # .. build a receive context ..
        #ctx = SocketReaderCtx()

        # .. wait for the reply ..

        # .. and raise an exception in case of any error.

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

    sleep(2)

# ################################################################################################################################
# ################################################################################################################################
