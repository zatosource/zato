# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# requests
from requests import post

# Zato
from zato.common.util import get_free_port

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class WMQIPC(object):
    """ Implements communication with a WebSphere MQ connector for a given server.
    """

    def start_websphere_mq_connector(self, ipc_tcp_start_port):
        """ Starts an HTTP server acting as a WebSphere MQ connector.
        Its port will be equal to or greater than ipc_tcp_start_port, which is the starting point to find a free port from.
        """
        self.wmq_ipc_tcp_port = get_free_port(ipc_tcp_start_port)
        logger.info('Found TCP port `%s` for WebSphere MQ connector to use by server `%s`', self.wmq_ipc_tcp_port, self.name)

# ################################################################################################################################

    def invoke_wmq_connector(self, msg, address_pattern='http://127.0.0.1:{}/'):
        if self.is_first_worker:
            address = address_pattern.format(self.wmq_ipc_tcp_port)
            return post(address, data=str(msg))

# ################################################################################################################################
