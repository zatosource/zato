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
from zato.server.connection.queue import Wrapper

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class _WSXClient(WebSocketClient):
    def opened(self):
        print(111, self)

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
        self.impl = _WSXClient(self.config.address)
        self.impl.connect()
        self.impl.run_forever()

# ################################################################################################################################

class ZatoWSXClient(object):
    """ A client through which Zato services can be invoked over outgoing WebSocket connections.
    """

# ################################################################################################################################

class OutconnWSXWrapper(Wrapper):
    """ Wraps a queue of connections to WebSockets.
    """
    def __init__(self, config, server):
        super(OutconnWSXWrapper, self).__init__(config, 'outgoing WebSocket', server)

    def add_client(self):
        try:
            conn = WSXClient(self.config)
        except Exception:
            logger.warn('Could not build a WSX client `%s`', format_exc())
        else:
            self.client.put_client(conn)

# ################################################################################################################################
