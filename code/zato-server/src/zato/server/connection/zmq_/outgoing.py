# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# gevent
from gevent import sleep

# ZeroMQ
import zmq.green as zmq

# Zato
from zato.server.store import BaseAPI, BaseStore

logger = logging.getLogger(__name__)

# ################################################################################################################################

class ZMQFacade(object):
    """ A ZeroMQ facade for services so they aren't aware that sending ZMQ
    messages actually requires us to use the Zato broker underneath.
    """
    def __init__(self, server):
        self.server = server
        self.connect_sleep = float(self.server.fs_server_config.misc.zeromq_connect_sleep)

    def send(self, msg, out_name, *args, **kwargs):

        # Connection info and a new context so everything is bound to that greenlet only
        conn_info = self.server.worker_store.zmq_out_api.get(out_name, False)
        ctx = zmq.Context()

        # Create a socket and connect
        socket = ctx.socket(getattr(zmq, conn_info.config.socket_type))
        socket.setsockopt(zmq.LINGER, 0)
        socket.connect(conn_info.config.address)

        # Don't send yet - we may still not be connected
        sleep(kwargs.get('connect_sleep', self.connect_sleep))

        # Send now
        socket.send(msg if isinstance(msg, bytes) else msg.encode('utf-8'))

        # And clean up
        socket.close()
        ctx.destroy()

    def conn(self):
        """ Returns self. Added to make the facade look like other outgoing
        connection wrappers.
        """
        return self

# ################################################################################################################################

class ZMQAPI(BaseAPI):
    """ API to obtain ZeroMQ connections through.
    """

class ZMQConnStore(BaseStore):
    """ Stores outgoing connections to ZeroMQ.
    """
    def create_impl(self, config, config_no_sensitive):
        pass
