# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# gevent
from gevent import spawn

# stompest
from stompest.config import StompConfig
from stompest.error import StompConnectionError
from stompest.sync import Stomp

# Zato
from zato.common import CHANNEL as common_channel
from zato.common.broker_message import CHANNEL, OUTGOING
from zato.common.util import new_cid
from zato.server.connection import BaseConnPoolStore, BasePoolAPI

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class STOMPConnection(Stomp):
    def __init__(self, *args, **kwargs):
        super(STOMPConnection, self).__init__(*args, **kwargs)
        self.keep_running = True

# ################################################################################################################################

def _channel_main_loop(item, worker):
    session = item.conn
    stomp_channel = common_channel.STOMP
    service_name = item.config.service_name

    for name in item.config.sub_to.splitlines():
        session.subscribe(name)

    try:
        while session.keep_running:
            frame = session.receiveFrame()
            worker.on_message_invoke_service({
                'cid': new_cid(),
                'service': service_name,
                'payload': frame
            }, stomp_channel, 'STOMP_CHANNEL_MSG')

    except StompConnectionError:

        # We want to report it only if we are still to run,
        # otherwise it's just an exception signalling the connection was closed.
        if session.keep_running:
            raise

def channel_main_loop(*args, **kwargs):
    spawn(_channel_main_loop, *args, **kwargs)

# ################################################################################################################################

def create_stomp_session(config):
    session = STOMPConnection(StompConfig(
        'tcp://' + config.address, config.username or None, config.password or None, config.proto_version))
    session.connect(connectTimeout=config.timeout, connectedTimeout=config.timeout)

    return session

# ################################################################################################################################

class STOMPAPI(BasePoolAPI):
    """ API through which connections to STOMP can be obtained.
    """

# ################################################################################################################################

class STOMPConnStore(BaseConnPoolStore):
    """ Stores connections to STOMP.
    """
    def create_session(self, name, config, config_no_sensitive):
        config.timeout = int(config.timeout)
        config.pool_size = 5

        return create_stomp_session(config)

    def delete_session_hook(self, item):
        """ Closes our underlying session.
        """
        item.conn.disconnect()

# ################################################################################################################################

class OutconnSTOMPConnStore(STOMPConnStore):
    conn_name = 'STOMP outconn'
    dispatcher_events = [OUTGOING.STOMP_DELETE, OUTGOING.STOMP_EDIT]
    delete_event = OUTGOING.STOMP_DELETE
    dispatcher_listen_for = OUTGOING

# ################################################################################################################################


class ChannelSTOMPConnStore(STOMPConnStore):
    conn_name = 'STOMP channel'
    dispatcher_events = [CHANNEL.STOMP_DELETE, CHANNEL.STOMP_EDIT]
    delete_event = CHANNEL.STOMP_DELETE
    dispatcher_listen_for = CHANNEL

    def delete_session_hook(self, item):
        """ Closes our mainloop and calls parent implementation.
        """
        item.conn.keep_running = False
        super(ChannelSTOMPConnStore, self).delete_session_hook(item)

# ################################################################################################################################
