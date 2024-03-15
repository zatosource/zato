# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Bunch
from bunch import bunchify

# Zato
from zato.common.util.api import start_connectors, wait_for_dict_key
from zato.server.base.worker.common import WorkerImpl

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.typing_ import any_, strdict
    from zato.server.base.worker import WorkerStore
    from zato.server.connection.connector import ConnectorStore

# ################################################################################################################################
# ################################################################################################################################

class WebSocket(WorkerImpl):
    """ WebSocket-related functionality for worker objects.
    """
    web_socket_api: 'ConnectorStore'

# ################################################################################################################################

    def web_socket_channel_create_edit(
        self:'WorkerStore', # type: ignore
        name,   # type: str
        msg,    # type: Bunch
        action, # type: str
        lock_timeout, # type: int
        start  # type: bool
    ) -> 'None':
        with self.server.zato_lock_manager(msg.config_cid, ttl=10, block=lock_timeout):

            # Get the name to delete, which may be actually an old name in case it is a rename ..
            config_name:'str' = msg.get('name', '') or msg.get('old_name', '')

            # .. delete the previous configuration, if any ..
            _:'any_' = self.worker_config.channel_web_socket.pop(config_name, None)

            # .. create the new one ..
            config = {
                'config': msg
            }

            # .. and assign it for later use ..
            self.worker_config.channel_web_socket[config_name] = config

            # .. now, proceed to the the low-level connector functionality.
            func = getattr(self.web_socket_api, action)
            func(name, msg, self.on_message_invoke_service, self.request_dispatcher.url_data.authenticate_web_socket)

# ################################################################################################################################

    def get_web_socket_channel_id_by_name(
        self: 'WorkerStore', # type: ignore
        channel_name: 'str'
    ) -> 'int':

        wait_for_dict_key(self.worker_config.channel_web_socket, channel_name, timeout=5) # type: ignore
        item:'strdict' = self.worker_config.channel_web_socket.get(channel_name)
        item_config = item['config']
        channel_id:'int' = item_config['id']
        return channel_id

# ################################################################################################################################

    def web_socket_channel_create(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.web_socket_channel_create_edit(msg.name, msg, 'create', 0, True)
        self.web_socket_api.start(msg.name)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_WEB_SOCKET_CREATE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if self.server.zato_lock_manager.acquire(msg.config_cid, ttl=10, block=False):
            start_connectors(self, 'zato.channel.web-socket.start', msg)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_WEB_SOCKET_EDIT(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        msg = bunchify(msg)
        self.web_socket_channel_create_edit(msg.old_name, msg, 'edit', 5, False)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_WEB_SOCKET_DELETE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        with self.server.zato_lock_manager(msg.config_cid, ttl=10, block=5):
            self.web_socket_api.delete(msg.name)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_WEB_SOCKET_BROADCAST(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.invoke('zato.channel.web-socket.broadcast', {
            'channel_name': msg.channel_name,
            'data': msg.data
        })

# ################################################################################################################################
