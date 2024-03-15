# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.common.api import WEB_SOCKET

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_, strdict, strnone
    from zato.common.wsx_client import MessageFromServer
    from zato.server.base.parallel import ParallelServer
    from zato.server.generic.api.outconn.wsx.base import OutconnWSXWrapper

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class WSXCtx:
    """ Details of a message received from a WebSocket outgoing connection.
    """
    type = None
    invoke_service:'callable_'

    def __init__(self, config:'strdict', conn:'OutconnWSXWrapper') -> 'None':
        self.config = config
        self.conn = conn

# ################################################################################################################################
# ################################################################################################################################

class Connected(WSXCtx):

    type = WEB_SOCKET.OUT_MSG_TYPE.CONNECT

    def invoke_service(self, server:'ParallelServer', service_name:'str') -> 'None':
        instance, _ = server.service_store.new_instance_by_name(service_name)
        instance.on_connected(self) # type: ignore

OnConnected = Connected

# ################################################################################################################################
# ################################################################################################################################

class OnMessage(WSXCtx):

    type = WEB_SOCKET.OUT_MSG_TYPE.MESSAGE

    def __init__(self, data:'strdict | MessageFromServer', *args:'any_', **kwargs:'any_') -> 'None':
        self.data = data
        super(OnMessage, self).__init__(*args, **kwargs)

    def invoke_service(self, server:'ParallelServer', service_name:'str') -> 'None':
        instance, _ = server.service_store.new_instance_by_name(service_name)
        instance.on_message_received(self) # type: ignore

OnMessageReceived = OnMessage

# ################################################################################################################################
# ################################################################################################################################

class Close(WSXCtx):

    type = WEB_SOCKET.OUT_MSG_TYPE.CLOSE

    def __init__(self, code:'int', reason:'strnone'=None, *args:'any_', **kwargs:'any_') -> 'None':
        self.code = code
        self.reason = reason
        super(Close, self).__init__(*args, **kwargs)

    def invoke_service(self, server:'ParallelServer', service_name:'str') -> 'None':
        instance, _ = server.service_store.new_instance_by_name(service_name)
        instance.on_closed(self) # type: ignore

OnClosed = Close

# ################################################################################################################################
# ################################################################################################################################

class _BaseWSXClient:
    def __init__(
        self,
        server: 'ParallelServer',
        config:'strdict',
        on_connected_cb:'callable_',
        on_message_cb:'callable_',
        on_close_cb:'callable_',
    ) -> 'None':
        self.config = config
        self.on_connected_cb = on_connected_cb
        self.on_message_cb = on_message_cb
        self.on_close_cb = on_close_cb

# ################################################################################################################################

    def opened(self) -> 'None':
        self.on_connected_cb(self)

# ################################################################################################################################

    def received_message(self, msg:'MessageFromServer') -> 'None':
        self.on_message_cb(msg.data)

# ################################################################################################################################

    def closed(self, code:'int', reason:'strnone'=None) -> 'None':
        self.on_close_cb(code, reason)

# ################################################################################################################################
# ################################################################################################################################

# For flake8
_BaseWSXClient = _BaseWSXClient # type: ignore

# ################################################################################################################################
# ################################################################################################################################
