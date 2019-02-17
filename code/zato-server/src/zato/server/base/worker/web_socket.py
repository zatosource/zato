# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Bunch
from bunch import bunchify

# Zato
from zato.common.util import start_connectors
from zato.server.base.worker.common import WorkerImpl

# ################################################################################################################################

class WebSocket(WorkerImpl):
    """ WebSocket-related functionality for worker objects.
    """
    def __init__(self):
        super(WebSocket, self).__init__()
        self.web_socket_api = None

# ################################################################################################################################

    def web_socket_channel_create_edit(self, name, msg, action, lock_timeout, start):
        with self.server.zato_lock_manager(msg.config_cid, ttl=10, block=lock_timeout):
            func = getattr(self.web_socket_api, action)
            func(name, msg, self.on_message_invoke_service, self.request_dispatcher.url_data.authenticate_web_socket)

# ################################################################################################################################

    def web_socket_channel_create(self, msg):
        self.web_socket_channel_create_edit(msg.name, msg, 'create', 0, True)
        self.web_socket_api.start(msg.name)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_WEB_SOCKET_CREATE(self, msg):
        if self.server.zato_lock_manager.acquire(msg.config_cid, ttl=10, block=False):
            start_connectors(self, 'zato.channel.web-socket.start', msg)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_WEB_SOCKET_EDIT(self, msg):

        # Each worker uses a unique bind port
        msg = bunchify(msg)

        self.web_socket_channel_create_edit(msg.old_name, msg, 'edit', 5, False)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_WEB_SOCKET_DELETE(self, msg):
        with self.server.zato_lock_manager(msg.config_cid, ttl=10, block=5):
            self.web_socket_api.delete(msg.name)

# ################################################################################################################################
