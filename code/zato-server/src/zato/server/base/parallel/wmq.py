# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from binascii import unhexlify
from datetime import datetime, timedelta
from json import loads
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import sleep

# requests
from requests import get, post

# Zato
from zato.common import IPC, WebSphereMQCallData
from zato.common.broker_message import CHANNEL, DEFINITION, OUTGOING
from zato.common.util import get_free_port
from zato.common.util.json_ import dumps
from zato.common.util.proc import start_python_process

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

address_pattern='http://127.0.0.1:{}/{}'
not_enabled_msg = 'IBM MQ component is not enabled - set component_enabled.ibm_mq to True in server.conf ' \
                  'and restart all servers before IBM MQ connections can be used.'

# ################################################################################################################################

class WMQIPC(object):
    """ Implements communication with an IBM MQ MQ connector for a given server.
    """

# ################################################################################################################################

    def _check_enabled(self):
        if not self.fs_server_config.component_enabled.ibm_mq:
            raise Exception(not_enabled_msg)

# ################################################################################################################################

    def get_wmq_credentials(self, username=IPC.CONNECTOR.IBM_MQ.USERNAME):
        """ Returns a username/password pair that authentication with IBM MQ connectors is established with.
        """
        config = self.worker_store.basic_auth_get(username)['config']
        return config.username, config.password

# ################################################################################################################################

    def start_ibm_mq_connector(self, ipc_tcp_start_port, timeout=5):
        """ Starts an HTTP server acting as an IBM MQ MQ connector. Its port will be greater than ipc_tcp_start_port,
        which is the starting point to find a free port from.
        """
        self._check_enabled()

        self.wmq_ipc_tcp_port = get_free_port(ipc_tcp_start_port)
        logger.info('Starting IBM MQ connector for server `%s` on `%s`', self.name, self.wmq_ipc_tcp_port)

        # Credentials for both servers and connectors
        username, password = self.get_wmq_credentials()

        # Employ IPC to exchange subprocess startup configuration
        self.connector_config_ipc.set_config('zato-ibm-mq', dumps({
            'port': self.wmq_ipc_tcp_port,
            'username': username,
            'password': password,
            'server_port': self.port,
            'server_name': self.name,
            'server_path': '/zato/internal/callback/wmq',
            'base_dir': self.base_dir,
            'logging_conf_path': self.logging_conf_path
        }))

        # Start IBM MQ connector in a sub-process
        start_python_process('IBM MQ connector', False, 'zato.server.connection.jms_wmq.jms.container', '',
            extra_options={
                'deployment_key': self.deployment_key,
                'shmem_size': self.shmem_size
        })

        # Wait up to timeout seconds for the connector to start as indicated by its responding to a PING request
        now = datetime.utcnow()
        warn_after = now + timedelta(seconds=3)
        should_warn = False
        until = now + timedelta(seconds=timeout)
        is_ok = False
        address = address_pattern.format(self.wmq_ipc_tcp_port, 'ping')
        auth = self.get_wmq_credentials()

        while not is_ok or now >= until:
            if not should_warn:
                if now >= warn_after:
                    should_warn = True
            is_ok = self._ping_connector(address, auth, should_warn)
            if is_ok:
                break
            else:
                sleep(2)
                now = datetime.utcnow()

        if not is_ok:
            logger.warn('IBM MQ connector (%s) could not be started after %s', address, timeout)
        else:
            return is_ok

# ################################################################################################################################

    def _ping_connector(self, address, auth, should_warn):
        try:
            response = get(address, data='{}', auth=auth)
        except Exception:
            if should_warn:
                logger.info(format_exc())
        else:
            return response.ok

# ################################################################################################################################

    def ping_wmq(self, id):
        return self.invoke_wmq_connector({
            'action': DEFINITION.WMQ_PING.value,
            'id': id
        })

# ################################################################################################################################

    def send_wmq_message(self, msg):
        self._check_enabled()

        msg['action'] = OUTGOING.WMQ_SEND.value
        response = self.invoke_wmq_connector(msg)

        # If we are here, it means that there was no error because otherwise an exception
        # would have been raised by invoke_wmq_connector.
        response = loads(response.text)

        return WebSphereMQCallData(unhexlify(response['msg_id']).strip(), unhexlify(response['correlation_id']).strip())

# ################################################################################################################################

    def invoke_wmq_connector(self, msg, raise_on_error=True, address_pattern=address_pattern):
        self._check_enabled()

        address = address_pattern.format(self.wmq_ipc_tcp_port, 'api')
        response = post(address, data=dumps(msg), auth=self.get_wmq_credentials())

        if not response.ok:
            if raise_on_error:
                raise Exception(response.text)
            else:
                logger.warn('Error message from IBM MQ connector `{}`'.format(response.text))
        else:
            return response

# ################################################################################################################################

    def _create_initial_wmq_objects(self, config_dict, action, text_pattern, text_func):
        for value in config_dict.values():
            config = value['config']
            logger.info(text_pattern, text_func(config))
            config['action'] = action
            self.invoke_wmq_connector(config, False)

# ################################################################################################################################

    def create_initial_wmq_definitions(self, config_dict):
        def text_func(config):
            return '{} {}:{} (queue manager:{})'.format(config['name'], config['host'], config['port'], config['queue_manager'])

        text_pattern = 'Creating IBM MQ definition %s'
        action = DEFINITION.WMQ_CREATE.value
        self._create_initial_wmq_objects(config_dict, action, text_pattern, text_func)

# ################################################################################################################################

    def create_initial_wmq_outconns(self, config_dict):
        def text_func(config):
            return config['name']

        text_pattern = 'Creating IBM MQ outconn %s'
        action = OUTGOING.WMQ_CREATE.value
        self._create_initial_wmq_objects(config_dict, action, text_pattern, text_func)

# ################################################################################################################################

    def create_initial_wmq_channels(self, config_dict):
        def text_func(config):
            return config['name']

        text_pattern = 'Creating IBM MQ channel %s'
        action = CHANNEL.WMQ_CREATE.value
        self._create_initial_wmq_objects(config_dict, action, text_pattern, text_func)

# ################################################################################################################################
