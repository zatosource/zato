# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.common.api import NO_DEFAULT_VALUE
from zato.server.store import BaseAPI, BaseStore

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ZMQFacade:
    """ A ZeroMQ message API for services.
    """
    def __init__(self, zmq_out_api):
        self.zmq_out_api = zmq_out_api

# ################################################################################################################################

    def __getitem__(self, name):
        return self.zmq_out_api.connectors[name]

# ################################################################################################################################

    def send(self, msg, out_name, *args, **kwargs):
        """ Preserved for backwards-compatibility with Zato < 3.0.
        """
        if self.zmq_out_api == NO_DEFAULT_VALUE:
            raise ValueError('ZeroMQ connections are disabled - ensure that component_enabled.zeromq in server.conf is True')

        conn = self.zmq_out_api.connectors[out_name]
        conn.send(msg, *args, **kwargs)

# ################################################################################################################################

    def conn(self):
        """ Returns self. Added to make the facade look like other outgoing
        connection wrappers.
        """
        return self

# ################################################################################################################################
# ################################################################################################################################

class ZMQAPI(BaseAPI):
    """ API to obtain ZeroMQ connections through.
    """

# ################################################################################################################################
# ################################################################################################################################

class ZMQConnStore(BaseStore):
    """ Stores outgoing connections to ZeroMQ.
    """
    def create_impl(self, config, config_no_sensitive):
        pass

# ################################################################################################################################
# ################################################################################################################################
