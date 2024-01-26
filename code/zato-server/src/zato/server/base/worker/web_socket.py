# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Bunch
from bunch import bunchify

# Zato
from zato.common.util.api import start_connectors
from zato.server.base.worker.common import WorkerImpl

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
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
            func = getattr(self.web_socket_api, action)
            func(name, msg, self.on_message_invoke_service, self.request_dispatcher.url_data.authenticate_web_socket)

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
