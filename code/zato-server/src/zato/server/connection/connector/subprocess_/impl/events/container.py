# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from logging import getLogger
from tempfile import NamedTemporaryFile
from time import time
from traceback import format_exc

# Bunch
from bunch import bunchify

# gevent
from gevent.server import StreamServer

# Zato
from zato.common.api import SFTP
from zato.common.json_internal import dumps
from zato.common.sftp import SFTPOutput
from zato.server.connection.connector.subprocess_.base import BaseConnectionContainer, Response
from zato.server.connection.connector.subprocess_.impl.events.database import EventsDatabase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from socket import socket

    Bunch = Bunch
    socket = socket

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato_events')

# ################################################################################################################################
# ################################################################################################################################

# For later use
utcnow = datetime.utcnow

# All event actions possible
class Action:
    Ping = b'01'
    Push = b'zz'

# Maps incoming events to handler functions
action_map = {
    Action.Ping: '_on_event_ping',
    Action.Push: '_on_event_push',
}

# ################################################################################################################################
# ################################################################################################################################

class _StreamServer(StreamServer):
    def shutdown(self):
        self.close()

# ################################################################################################################################
# ################################################################################################################################

class EventsConnectionContainer(BaseConnectionContainer):

    connection_class = object
    ipc_name = conn_type = logging_file_name = 'events'

    remove_id_from_def_msg = False
    remove_name_from_def_msg = False

# ################################################################################################################################

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fs_data_path = '/tmp/zzz-parquet'
        sync_threshold = 1
        sync_interval_ms = 120_000

        # This is where events are kept
        self.events_db = EventsDatabase(fs_data_path, sync_threshold, sync_interval_ms)

        # By default, keep running forever
        self.keep_running = True

        # Remap handler names to actual handler methods
        self._action_map = {}
        for key, value in action_map.items():
            self._action_map[key] = getattr(self, value)

# ################################################################################################################################

    def _on_event_ping(self, data, address_str):
        # type: (str, str) -> str
        return 'vvv'

# ################################################################################################################################

    def _on_event_push(self, msg, is_reconnect=False, _utcnow=utcnow):
        out = {'a':22}
        #data = msg['data']

        elem = 'aaa' + utcnow().isoformat()
        x = int(time() * 1_000_000)

        data = {
            'id': elem + utcnow().isoformat(),
            'cid': 'cid.' + elem,
            'timestamp': '2021-05-12T07:07:01.4841' + elem,

            'source_type': 'zato.server' + elem,
            'source_id': 'server1' + elem,

            'object_type': elem,
            'object_id': elem,

            'source_type': elem,
            'source_id': elem,

            'recipient_type': elem,
            'recipient_id': elem,

            'total_time_ms': x,
        }

        self.events_db.push(data)

        return dumps(out)

# ################################################################################################################################

    def _on_new_connection(self, socket, address):
        # type: (socket, str) -> None

        # For later use
        address_str = '{}:{}'.format(address[0], address[1])

        # A new client connected to our server
        logger.info('New stream connection from %s', address_str)

        # Get access to the underlying file object
        socket_file = socket.makefile(mode='rb')

        # Keep running until explicitly requested not to
        while self.keep_running:

            # We work on a line-by-line basis
            line = socket_file.readline()

            # No input = client is no longer connected
            if not line:
                logger.info('Stream client disconnected (%s)', address_str)
                break

            # Extract the action sent ..
            action = line[:2]

            # .. find the handler function ..
            func = self._action_map.get(action)

            # .. no such handler = disconnect the client ..
            if not func:
                logger.warn('No handler for `%r` found. Disconnecting stream client (%s)', action, address_str)
                break

            # .. otherwise, handle the action ..
            data = line[2:].decode('utf8')
            response = func(data, address_str) # type: str
            response = response.encode('utf8')

            # .. and send the response to the client.
            socket.sendall(response)

        # If we are here, it means that the client disconnected.
        socket_file.close()

# ################################################################################################################################

    def make_server(self):
        return _StreamServer((self.host, self.port), self._on_new_connection)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    container = EventsConnectionContainer()
    container.run()

# ################################################################################################################################
# ################################################################################################################################
