# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import socket
from datetime import datetime
from logging import basicConfig, getLogger

# orjson
from orjson import dumps

# Zato
from zato.common.events.common import Action, PushCtx
from zato.common.typing_ import asdict
from zato.common.util.api import new_cid
from zato.common.util.tcp import read_from_socket, SocketReaderCtx, wait_until_port_taken

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.events.common import PushCtx

    PushCtx = PushCtx

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
        self.peer_name_str = '<Client-peer_name_str-default>'
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
        self.peer_name_str = '{}:{}'.format(*self.peer_name)

# ################################################################################################################################

    def send(self, action, data=b''):
        # type: (bytes) -> None
        self.socket.sendall(action + data + b'\n')

# ################################################################################################################################

    def ping(self):
        logger.info('Pinging %s (%s)', self.peer_name_str, self.conn_id)

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
        if response != Action.PingReply:
            raise ValueError('Unexpected response received from `{}` -> `{}`'.format(self.peer_name, response))

# ################################################################################################################################

    def push(self, ctx):
        # type: (PushCtx) -> None

        # Serialise the context to dict ..
        data = asdict(ctx)

        # .. now to JSON ..
        data = dumps(data)

        # .. and send it across (there will be no response).
        self.send(Action.Push, data)

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

    n_iters = 100_000

    for x in range(n_iters):

        if x % 1000 == 0:
            logger.info('ZZZ %s', x)

        ctx = PushCtx()
        ctx.id = new_cid()
        ctx.cid = new_cid()
        ctx.object_id = new_cid()
        ctx.object_type = '001'
        ctx.recipient_id = new_cid()
        ctx.recipient_type = 'ABC'
        ctx.source_id = new_cid()
        ctx.source_type = 'ZZZ'
        ctx.timestamp = datetime.utcnow().isoformat()
        ctx.total_time_ms = x

        client.push(ctx)

    client.close()

    sleep(2)

# ################################################################################################################################
# ################################################################################################################################
