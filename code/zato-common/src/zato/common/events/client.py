# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from datetime import datetime
from logging import getLogger

# gevent
from gevent import sleep
from gevent.lock import RLock

# orjson
from orjson import dumps

# simdjson
from simdjson import loads

# Zato
from zato.common.events.common import Action
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

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

utcnow = datetime.utcnow

# ################################################################################################################################
# ################################################################################################################################

class Client:
    def __init__(self, host, port):
        # type: (str, int) -> None
        self.host = host
        self.port = port
        self.remote_addr_str = '{}:{}'.format(self.host, self.port)
        self.socket = None # type: socket.socket
        self.peer_name = '<Client-peer_name-default>'
        self.peer_name_str = '<Client-peer_name_str-default>'
        self.conn_id = 'zstrcl' + new_cid(bytes=4)
        self.max_wait_time = 30
        self.max_msg_size = 30_000_000
        self.read_buffer_size = 30_000_000
        self.recv_timeout = 30
        self.should_log_messages = False
        self.is_connected = False
        self.lock = RLock()

# ################################################################################################################################

    def connect(self):
        # For later use
        start = utcnow()

        with self.lock:
            if self.is_connected:
                return

            self.socket = socket.socket(type=socket.SOCK_STREAM)

            while not self.is_connected:
                logger.info('Connecting to %s', self.remote_addr_str)
                try:
                    self.socket.connect((self.host, self.port))
                    self.peer_name = self.socket.getpeername()
                    self.peer_name_str = '{}:{}'.format(*self.peer_name)
                except Exception as e:
                    logger.info('Connection error `%s` (%s) -> %s', e.args, utcnow() - start, self.remote_addr_str)
                    sleep(1)
                else:
                    logger.info('Connected to %s after %s', self.remote_addr_str, utcnow() - start)
                    self.is_connected = True

# ################################################################################################################################

    def send(self, action, data=b''):
        # type: (bytes) -> None
        with self.lock:
            try:
                self.socket.sendall(action + data + b'\n')
            except Exception as e:
                self.is_connected = False
                logger.warning('Socket send error `%s` -> %s', e.args, self.remote_addr_str)
                self.close()
                self.connect()

# ################################################################################################################################

    def read(self):
        # type: () -> bytes

        with self.lock:

            # Build a receive context ..
            ctx = SocketReaderCtx(
                self.conn_id,
                self.socket,
                self.max_wait_time,
                self.max_msg_size,
                self.read_buffer_size,
                self.recv_timeout,
                self.should_log_messages
            )

            # .. wait for the reply and return it.
            return read_from_socket(ctx)

# ################################################################################################################################

    def ping(self):
        logger.info('Pinging %s (%s)', self.peer_name_str, self.conn_id)

        # Send the ping message ..
        self.send(Action.Ping)

        # .. wait for the reply ..
        response = self.read()

        # .. and raise an exception in case of any error.
        if response and response != Action.PingReply:
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

    def get_table(self):

        # Request the tabulated data ..
        self.send(Action.GetTable)

        # .. wait for the reply ..
        response = self.read()

        # .. and raise an exception in case of any error.
        if response and (not response.startswith(Action.GetTableReply)):
            raise ValueError('Unexpected response received from `{}` -> `{}`'.format(self.peer_name, response))

        table = response[Action.LenAction:]
        return loads(table) if table else None

# ################################################################################################################################

    def sync_state(self):

        # Request that the database sync its state with persistent storage ..
        self.send(Action.SyncState)

        # .. wait for the reply
        self.read()

# ################################################################################################################################

    def close(self):
        self.socket.close()

# ################################################################################################################################

    def run(self):

        # Make sure that we have a port to connect to ..
        wait_until_port_taken(self.port, 5)

        # .. do connect now ..
        self.connect()

        # .. and ping the remote end to confirm that we have connectivity.
        self.ping()

# ################################################################################################################################
# ################################################################################################################################
