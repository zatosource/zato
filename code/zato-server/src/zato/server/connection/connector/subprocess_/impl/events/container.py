# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.events.common import Action
from zato.common.util.json_ import JSONParser
from zato.common.util.tcp import ZatoStreamServer
from zato.server.connection.connector.subprocess_.base import BaseConnectionContainer
from zato.server.connection.connector.subprocess_.impl.events.database import EventsDatabase, OpCode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from socket import socket

    Bunch = Bunch
    socket = socket

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# For later use
utcnow = datetime.utcnow

# ################################################################################################################################
# ################################################################################################################################

class EventsConnectionContainer(BaseConnectionContainer):

    connection_class = object
    ipc_name = conn_type = logging_file_name = 'events'

    remove_id_from_def_msg = False
    remove_name_from_def_msg = False

# ################################################################################################################################

    def __init__(self, *args, **kwargs):
        # type: (str, int, int) -> None
        super().__init__(*args, **kwargs)

        # By default, keep running forever
        self.keep_running = True

        # A reusable JSON parser
        self._json_parser = JSONParser()

        # Map handler names to actual handler methods
        self._action_map = {
            Action.Ping: self._on_event_ping,
            Action.Push: self._on_event_push,
            Action.GetTable: self._on_event_get_table,
        }

# ################################################################################################################################

    def enrich_options(self):
        # type: (dict) -> None
        if not self.options['zato_subprocess_mode']:
            self.options['fs_data_path'] = '/tmp/dev-events'
            self.options['sync_threshold'] = 1
            self.options['sync_interval'] = 1

# ################################################################################################################################

    def post_init(self):

        try:
            fs_data_path = self.options['fs_data_path']
            sync_threshold = int(self.options['sync_threshold'])
            sync_interval = int(self.options['sync_interval'])

            self.events_db = EventsDatabase(logger, fs_data_path, sync_threshold, sync_interval)

        except Exception:
            logger.warning('Exception in post_init -> `%s`', format_exc())

# ################################################################################################################################

    def _on_event_ping(self, ignored_data, address_str):
        # type: (str) -> str
        logger.info('Ping received from `%s`', address_str)
        return Action.PingReply

# ################################################################################################################################

    def _on_event_push(self, data, ignored_address_str, _opcode=OpCode.Push):
        # type: (str, str, str) -> None

        # We received JSON bytes so we now need to load a Python object out of it ..
        data = self._json_parser.parse(data)
        data = data.as_dict() # type: dict

        # .. now, we can push it to the database.
        self.events_db.access_state(_opcode, data)

# ################################################################################################################################

    def _on_event_get_table(self, ignored_address_str, _opcode=OpCode.Tabulate):
        # type: (str, str) -> str
        data = self.events_db.get_table()
        return Action.GetTableReply + data.to_json().encode('utf8')

# ################################################################################################################################

    def _on_new_connection(self, socket, address):
        # type: (socket, str) -> None

        # For later use
        address_str = '{}:{}'.format(address[0], address[1])

        # A new client connected to our server
        logger.info('New stream connection from %s', address_str)

        # Get access to the underlying file object
        socket_file = socket.makefile(mode='rb')

        try:

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
                    logger.warning('No handler for `%r` found. Disconnecting stream client (%s)', action, address_str)
                    break

                # .. otherwise, handle the action ..
                data = line[2:]

                try:
                    response = func(data, address_str) # type: str
                except Exception as e:
                    logger.warning('Exception when calling func `%s` -> %s -> %s -> %s', func, address_str, data, e.args)

                # .. not all actions will result in a response ..
                if response:
                    response = response.encode('utf8') if isinstance(response, str) else response

                    # .. now, we can send the response to the client.
                    socket.sendall(response)

            # If we are here, it means that the client disconnected.
            socket_file.close()

        except Exception:
            logger.warning('Exception in _on_new_connection (%s) -> `%s`', address_str, format_exc())

# ################################################################################################################################

    def make_server(self):
        return ZatoStreamServer((self.host, self.port), self._on_new_connection)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    container = EventsConnectionContainer()
    container.run()

# ################################################################################################################################
# ################################################################################################################################
