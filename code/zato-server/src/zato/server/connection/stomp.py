# -*- coding: utf-8 -*-

"""
Copyright (C) 2015 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from traceback import format_exc

# gevent
from gevent.lock import RLock

# stompest
from stompest.config import StompConfig
from stompest.sync import Stomp

# Zato
from zato.server.connection.queue import ConnectionQueue, Wrapper

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class STOMPWrapper(Wrapper):
    """ Wraps a queue of connections to a STOMP broker.
    """
    def __init__(self, config, server):
        config.timeout = int(config.timeout)
        config.username_pretty = config.username or '(None)'
        config.auth_url = config.address
        config.pool_size = 5
        super(STOMPWrapper, self).__init__(config, 'Outgoing STOMP', server)

    def _get_connected_client(self):
        client = Stomp(StompConfig(
            'tcp://' + self.config.address, self.config.username or None, self.config.password or None, self.config.proto_version))
        client.connect(connectTimeout=self.config.timeout, connectedTimeout=self.config.timeout)

        return client

    def _get_client(self):
        return self._get_connected_client()

    def ping(self):
        client = self._get_connected_client()
        client.disconnect()

    def add_client(self):
        self.client.put_client(self._get_client())

# ################################################################################################################################

class STOMPChannelWrapper(STOMPWrapper):
    """ Wraps a queue of connections to a STOMP broker listening for messsages and invoking a Zato service
    upon receiving each.
    """
    def __init__(self, *args, **kwargs):
        super(STOMPChannelWrapper, self).__init__(*args, **kwargs)
        self.keep_running = True

    def main_loop(self, client):
        while self.keep_running:
            frame = client.receiveFrame()
            self.server.worker_storeaaaa 'kasn d{ASID