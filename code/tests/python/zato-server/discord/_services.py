# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The test services of the Discord suite - the services that send through self.discord and the services that
# read and change the connections as the Dashboard does.

# stdlib
from base64 import b64decode
from traceback import format_exc

# Zato
from zato.common.api import GENERIC
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylistnone, callable_, stranydict

# ################################################################################################################################
# ################################################################################################################################

# The columns of a generic connection an edit sends back as they are
_own_fields = ('id', 'name', 'type_', 'address', 'pool_size', 'is_active', 'is_internal', 'is_channel', 'is_outconn')

# The opaque attributes of a Discord connection
_opaque_fields = ('timeout', 'default_channel_id')

# ################################################################################################################################
# ################################################################################################################################

def _get_config(service:'Service', conn_name:'str') -> 'stranydict':
    """ The configuration a Discord connection has right now.
    """
    out = service.server.config_manager.chat_discord[conn_name]
    return out

# ################################################################################################################################

def _decode_files(files:'anylistnone') -> 'anylistnone':
    """ Files arrive as pairs of a file name and base64 content and leave as pairs of a file name and bytes.
    """
    if files is None:
        return None

    out = []
    for file_name, encoded in files:
        out.append((file_name, b64decode(encoded)))

    return out

# ################################################################################################################################

def _run(service:'Service', func:'callable_') -> 'None':
    """ Runs one call and answers with its result or with the error it raised.
    """
    try:
        response = func()
    except Exception as e:
        service.logger.warning(format_exc())
        service.response.payload = {'is_ok': False, 'error': str(e)}
    else:
        service.response.payload = {'is_ok': True, 'response': response}

# ################################################################################################################################
# ################################################################################################################################

class Send(Service):
    """ Sends a message through self.discord.send.
    """
    name = 'test.discord.send'

    def handle(self) -> 'None':

        request = self.request.raw_request

        conn_name = request['conn_name']
        content = request['content']
        channel_id = request.get('channel_id', '')
        embeds = request.get('embeds')
        files = _decode_files(request.get('files'))
        allowed_mentions = request.get('allowed_mentions')

        def call() -> 'stranydict':
            out = self.discord.send(conn_name, content, channel_id, embeds, files, allowed_mentions)
            return out

        _run(self, call)

# ################################################################################################################################
# ################################################################################################################################

class SendDirect(Service):
    """ Sends a direct message through self.discord.send_direct.
    """
    name = 'test.discord.send-direct'

    def handle(self) -> 'None':

        request = self.request.raw_request

        conn_name = request['conn_name']
        user_id = request['user_id']
        content = request['content']
        embeds = request.get('embeds')
        files = _decode_files(request.get('files'))

        def call() -> 'stranydict':
            out = self.discord.send_direct(conn_name, user_id, content, embeds, files)
            return out

        _run(self, call)

# ################################################################################################################################
# ################################################################################################################################

class Invoke(Service):
    """ Invokes any endpoint of the Discord API through the client of a connection.
    """
    name = 'test.discord.invoke'

    def handle(self) -> 'None':

        request = self.request.raw_request

        conn_name = request['conn_name']
        http_method = request['http_method']
        path = request['path']
        data = request.get('data')

        def call() -> 'stranydict':
            out = self.discord[conn_name].invoke(http_method, path, data)
            return out

        _run(self, call)

# ################################################################################################################################
# ################################################################################################################################

class Ping(Service):
    """ Pings a connection through its client.
    """
    name = 'test.discord.ping'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        def call() -> 'None':
            self.discord[conn_name].ping()

        _run(self, call)

# ################################################################################################################################
# ################################################################################################################################

class GetConnection(Service):
    """ Answers with the configuration a connection has right now and with the state of its client.
    """
    name = 'test.discord.get-connection'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        connections = self.server.config_manager.chat_discord

        if conn_name not in connections:
            self.response.payload = {'is_found': False}
            return

        config = connections[conn_name]
        client = config.conn.shared_client

        out:'stranydict' = {
            'is_found': True,
            'is_ready': client.ready.is_set(),
            'last_error': client.last_error,
            'stop_reason': client.stop_reason,
            'has_handshake_greenlet': client.handshake_greenlet is not None,
        }

        for field_name in _own_fields + _opaque_fields:
            out[field_name] = config[field_name]

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

class CreateConnection(Service):
    """ Creates a connection as the Dashboard does - the connection first, its token afterwards.
    """
    name = 'test.discord.create-connection'

    def handle(self) -> 'None':

        request = self.request.raw_request

        create_request = {
            'name': request['name'],
            'type_': GENERIC.CONNECTION.TYPE.CHAT_DISCORD,
            'is_active': True,
            'is_internal': False,
            'is_channel': False,
            'is_outconn': True,
            'pool_size': 1,
            'address': request['address'],
            'timeout': request['timeout'],
            'default_channel_id': request['default_channel_id'],
            'secret': request['token'],
        }

        response = self.invoke('zato.generic.connection.create', create_request)

        self.response.payload = {'id': response['id']}

# ################################################################################################################################
# ################################################################################################################################

class EditConnection(Service):
    """ Changes some fields of a connection as the Dashboard does.
    """
    name = 'test.discord.edit-connection'

    def handle(self) -> 'None':

        request = self.request.raw_request

        conn_name = request['conn_name']
        changes = request['changes']

        config = _get_config(self, conn_name)

        edit_request = {}
        for field_name in _own_fields + _opaque_fields:
            edit_request[field_name] = config[field_name]

        edit_request.update(changes)

        _ = self.invoke('zato.generic.connection.edit', edit_request)

        self.response.payload = {'id': config['id']}

# ################################################################################################################################
# ################################################################################################################################

class DeleteConnection(Service):
    """ Deletes a connection as the Dashboard does.
    """
    name = 'test.discord.delete-connection'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        config = _get_config(self, conn_name)
        conn_id = config['id']

        _ = self.invoke('zato.generic.connection.delete', {'id': conn_id})

        self.response.payload = {'id': conn_id}

# ################################################################################################################################
# ################################################################################################################################
