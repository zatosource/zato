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
from zato.common import WEB_SOCKET, ZATO_NONE
from zato.common.wsx_client import Client as _ZatoWSXClientImpl, Config as _ZatoWSXConfigImpl
from zato.common.util import new_cid, spawn_greenlet
from zato.server.connection.queue import Wrapper

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class WSXCtx(object):
    """ Details of a message received from a WebSocket outgoing connection.
    """
    type = None

    def __init__(self, config, conn):
        self.config = config
        self.conn = conn

# ################################################################################################################################

class Connected(WSXCtx):
    type = WEB_SOCKET.OUT_MSG_TYPE.CONNECT

# ################################################################################################################################

class OnMessage(WSXCtx):
    type = WEB_SOCKET.OUT_MSG_TYPE.MESSAGE

    def __init__(self, data, *args, **kwargs):
        self.data = data
        super(OnMessage, self).__init__(*args, **kwargs)

# ################################################################################################################################

class Close(WSXCtx):
    type = WEB_SOCKET.OUT_MSG_TYPE.CLOSE

    def __init__(self, code, reason=None, *args, **kwargs):
        self.code = code
        self.reason = reason
        super(OnMessage, self).__init__(*args, **kwargs)

# ################################################################################################################################

class _BaseWSXClient(object):
    def __init__(self, config, on_connected_cb, on_message_cb, on_close_cb, *ignored_args, **ignored_kwargs):
        self.config = config
        self.on_connected_cb = on_connected_cb
        self.on_message_cb = on_message_cb
        self.on_close_cb = on_close_cb

# ################################################################################################################################

    def opened(self):
        self.on_connected_cb()

# ################################################################################################################################

    def received_message(self, msg):
        self.on_message_cb(msg.data)

# ################################################################################################################################

    def closed(self, code, reason=None):
        self.on_close_cb(code, reason)

# ################################################################################################################################

class _WSXClient(_BaseWSXClient, WebSocketClient):
    def __init__(self, config, on_connected_cb, on_message_cb, on_close_cb, *args, **kwargs):
        _BaseWSXClient.__init__(self, config, on_connected_cb, on_message_cb, on_close_cb)
        WebSocketClient.__init__(self, *args, **kwargs)

# ################################################################################################################################

class ZatoWSXClient(_BaseWSXClient):
    """ A client through which Zato services can be invoked over outgoing WebSocket connections.
    """
    def __init__(self, *args, **kwargs):
        super(ZatoWSXClient, self).__init__(*args, **kwargs)

        self._zato_client_config = _ZatoWSXConfigImpl()
        self._zato_client_config.client_name = 'WSX outconn - {}'.format(self.config.name)
        self._zato_client_config.client_id = 'wsx.outconn.{}'.format(new_cid())
        self._zato_client_config.address = self.config.address
        self._zato_client_config.username = 'user1'
        self._zato_client_config.secret = 'secret1'
        self._zato_client_config.on_request_callback = self.on_message_cb

        self._zato_client = _ZatoWSXClientImpl(self._zato_client_config)

    def connect(self):
        self._zato_client.run()
        response = self._zato_client.invoke({
            'service':'zato.ping'
        })

        logger.warn('111 %s', response)

    def run_forever(self):
        print(444, `self.config`)

# ################################################################################################################################

class WSXClient(object):
    """ A client through which outgoing WebSocket messages can be sent.
    """
    def __init__(self, config):
        self.config = config
        self.is_connected = False
        spawn_greenlet(self._init)

    def _init(self):
        _impl_class = ZatoWSXClient if self.config.is_zato else _WSXClient
        self.impl = _impl_class(self.config, self.on_connected_cb, self.on_message_cb, self.on_close_cb, self.config.address)
        self.impl.connect()
        self.impl.run_forever()

    def on_connected_cb(self):
        self.is_connected = True
        self.config.parent.on_connected_cb()

    def on_message_cb(self, msg):
        self.config.parent.on_message_cb(msg)

    def on_close_cb(self, code, reason=None):
        self.config.parent.on_close_cb(code, reason)

# ################################################################################################################################

class OutconnWSXWrapper(Wrapper):
    """ Wraps a queue of connections to WebSockets.
    """
    def __init__(self, config, server):
        config.parent = self
        self._set_service_names(config, server)
        super(OutconnWSXWrapper, self).__init__(config, 'outgoing WebSocket', server)

# ################################################################################################################################

    def _set_service_names(self, config, server):

        if config.on_connect_service_id:
            config.on_connect_service_name = server.service_store.get_service_name_by_id(config.on_connect_service_id)

        if config.on_message_service_id:
            config.on_message_service_name = server.service_store.get_service_name_by_id(config.on_message_service_id)

        if config.on_close_service_id:
            config.on_close_service_name = server.service_store.get_service_name_by_id(config.on_close_service_id)

# ################################################################################################################################

    def on_connected_cb(self):
        self.is_connected = True
        if self.config.on_connect_service_name:
            self.server.invoke(self.config.on_connect_service_name, {
                'ctx': Connected(self.config, self)
            })

# ################################################################################################################################

    def on_message_cb(self, msg):
        if self.config.on_message_service_name:
            self.server.invoke(self.config.on_message_service_name, {
                'ctx': OnMessage(msg, self.config, self)
            })

# ################################################################################################################################

    def on_close_cb(self, code, reason=None):
        if self.config.on_close_service_name:
            self.server.invoke(self.config.on_close_service_name, {
                'ctx': Close(code, reason, self.config, self)
            })

# ################################################################################################################################

    def add_client(self):
        try:
            conn = WSXClient(self.config)
        except Exception:
            logger.warn('WSX client could not be built `%s`', format_exc())
        else:
            self.client.put_client(conn)

# ################################################################################################################################
