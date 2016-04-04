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

# ################################################################################################################################

    def __getitem__(self, name):
        return self.server.worker_store.zmq_out_api.connectors[name]

# ################################################################################################################################

    def send(self, msg, out_name, *args, **kwargs):
        """ Preserved for backwards-compatibility with Zato < 3.0.
        """
        conn = self.server.worker_store.zmq_out_api.connectors[out_name]
        conn.send(msg, *args, **kwargs)

# ################################################################################################################################

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
