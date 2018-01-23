# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os
from copy import deepcopy
from json import dumps
from logging import getLogger, Logger

# requests
from requests import post

# Zato
from zato.common import IPC
from zato.common.proc_util import start_python_process
from zato.common.util import get_free_port

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class WMQIPC(object):
    """ Implements communication with a WebSphere MQ connector for a given server.
    """

# ################################################################################################################################

    def get_wmq_credentials(self, username=IPC.CONNECTOR.WEBSPHERE_MQ.USERNAME):
        """ Returns a username/password pair that authentication with WebSphere MQ connectors is established with.
        """
        config = self.worker_store.basic_auth_get(username)['config']
        return config.username, config.password

# ################################################################################################################################

    def start_websphere_mq_connector(self, ipc_tcp_start_port):
        """ Starts an HTTP server acting as a WebSphere MQ connector. Its port will be greater than ipc_tcp_start_port,
        which is the starting point to find a free port from.
        """
        self.wmq_ipc_tcp_port = get_free_port(ipc_tcp_start_port)
        logger.info('Starting WebSphere MQ connector for server `%s` on `%s`', self.wmq_ipc_tcp_port, self.name)

        # Credentials for both servers and connectors
        username, password = self.get_wmq_credentials()

        # User kernel's facilities to store configuration
        self.keyutils.user_set(b'zato-wmq', dumps({
            'port': self.wmq_ipc_tcp_port,
            'username': username,
            'password': password,
            'server_pid': self.pid,
            'server_name': self.name,
            'cluster_name': self.cluster.name,
            'base_dir': self.base_dir,
            'logging_conf_path': self.logging_conf_path
        }), self.pid)

        # Start WebSphere MQ connector in a sub-process
        start_python_process(False, 'zato.server.connection.jms_wmq.jms.container', 'WebSphere MQ connector', '')

# ################################################################################################################################

    def invoke_wmq_connector(self, msg, address_pattern='http://127.0.0.1:{}/'):
        if self.is_first_worker:
            address = address_pattern.format(self.wmq_ipc_tcp_port)
            return post(address, data=dumps(msg), auth=self.get_wmq_credentials())

# ################################################################################################################################
