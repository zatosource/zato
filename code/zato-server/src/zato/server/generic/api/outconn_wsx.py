# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from traceback import format_exc

# ws4py
from ws4py.client.threadedclient import WebSocketClient

# Zato
from zato.common import ZATO_NONE
from zato.common.util import spawn_greenlet
from zato.server.connection.queue import Wrapper

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class _WSXClient(WebSocketClient):
    def __init__(self, on_connected_cb, on_message_cb, on_close_cb, *args, **kwargs):
        self.on_connected_cb = on_connected_cb
        self.on_message_cb = on_message_cb
        self.on_close_cb = on_close_cb
        super(_WSXClient, self).__init__(*args, **kwargs)

    def opened(self):
        self.on_connected_cb()

    def closed(self, code, reason=None):
        print(222, code, reason)

    def received_message(self, m):
        print(333, m)

class WSXClient(object):
    """ A client through which outgoing WebSocket messages can be sent,
    not meant to be used to invoke Zato services (this is what ZatoWSXClient is for).
    """
    def __init__(self, config):
        self.config = config
        self.is_connected = False
        spawn_greenlet(self._init)

    def _init(self):
        self.impl = _WSXClient(self._on_connected_cb, self._on_message_cb, self._on_close_cb, self.config.address)
        self.impl.connect()
        self.impl.run_forever()

    def _on_connected_cb(self):
        print('*' * 80)
        print('_on_connected_cb')
        print('*' * 80)
        self.is_connected = True

    def _on_message_cb(self):
        print('*' * 80)
        print('_on_message_cb')
        print('*' * 80)

    def _on_close_cb(self):
        print('*' * 80)
        print('_on_close_cb')
        print('*' * 80)

# ################################################################################################################################

class ZatoWSXClient(object):
    """ A client through which Zato services can be invoked over outgoing WebSocket connections.
    """

# ################################################################################################################################

class OutconnWSXWrapper(Wrapper):
    """ Wraps a queue of connections to WebSockets.
    """
    def __init__(self, config, server):
        self._set_service_names(config, server)
        super(OutconnWSXWrapper, self).__init__(config, 'outgoing WebSocket', server)

    def _set_service_names(self, config, server):

        if config.on_connect_service_id:
            config.on_connect_service_name = server.service_store.get_service_name_by_id(config.on_connect_service_id)

        if config.on_message_service_id:
            config.on_message_service_name = server.service_store.get_service_name_by_id(config.on_message_service_id)

        if config.on_close_service_id:
            config.on_close_service_name = server.service_store.get_service_name_by_id(config.on_close_service_id)

    def add_client(self):
        try:
            conn = WSXClient(self.config)
        except Exception:
            logger.warn('WSX client could not be built `%s`', format_exc())
        else:
            self.client.put_client(conn)

# ################################################################################################################################
