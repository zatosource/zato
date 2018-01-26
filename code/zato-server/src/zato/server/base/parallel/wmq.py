# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os
from copy import deepcopy
from datetime import datetime, timedelta
from httplib import OK
from json import dumps
from logging import getLogger, Logger
from traceback import format_exc

# gevent
from gevent import sleep

# requests
from requests import get, post

# Zato
from zato.common import IPC
from zato.common.broker_message import DEFINITION
from zato.common.proc_util import start_python_process
from zato.common.util import get_free_port

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

address_pattern='http://127.0.0.1:{}/{}'

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

    def start_websphere_mq_connector(self, ipc_tcp_start_port, timeout=5):
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

        # Wait up to timeout seconds for the connector to start as indicated by its responding to a PING request
        now = datetime.utcnow()
        until = timedelta(seconds=timeout)
        is_ok = False
        address = address_pattern.format(self.wmq_ipc_tcp_port, 'ping')
        auth = (address, username)

        while not is_ok or now >= until:
            is_ok = self._ping_connector(address, auth)
            if is_ok:
                break
            else:
                sleep(0.2)
                now = datetime.utcnow()

        if not is_ok:
            logger.warn('WebSphere MQ connector (%s) could not be started after %s', address, timeout)
        else:
            return is_ok

# ################################################################################################################################

    def _ping_connector(self, address, auth):
        try:
            response = get(address, data='{}', auth=auth)
        except Exception as e:
            logger.warn(format_exc())
        else:
            return response.ok

# ################################################################################################################################

    def ping_wmq(self, id):
        response = self.invoke_wmq_connector({
            'action': DEFINITION.WMQ_PING.value,
            'id': id
        })

        if not response.ok:
            raise Exception(response.text)

# ################################################################################################################################

    def invoke_wmq_connector(self, msg, address_pattern=address_pattern):
        address = address_pattern.format(self.wmq_ipc_tcp_port, 'api')
        return post(address, data=dumps(msg), auth=self.get_wmq_credentials())

# ################################################################################################################################

    def create_initial_wmq_definitions(self, config_dict):
        for value in config_dict.values():
            config = value['config']
            config['action'] = DEFINITION.WMQ_CREATE.value
            self.invoke_wmq_connector(config)

# ################################################################################################################################
