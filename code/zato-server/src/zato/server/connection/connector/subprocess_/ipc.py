# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime, timedelta
from json import loads
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import sleep

# requests
from requests import get, post

# Zato
from zato.common.util import get_free_port
from zato.common.util.json_ import dumps
from zato.common.util.proc import start_python_process

# ################################################################################################################################

# Type checking
import typing

if typing.TYPE_CHECKING:

    # Zato
    from zato.server.base.parallel import ParallelServer

    # For pyflakes
    ParallelServer = ParallelServer

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

address_pattern='http://127.0.0.1:{}/{}'
not_enabled_pattern = '{connector_name} component is not enabled - install PyMQI and set component_enabled.{check_enabled} ' \
     'to True in server.conf and restart all servers before {connector_name} connections can be used.'

# ################################################################################################################################

class SubprocessIPC(object):
    """ Base class for IPC with subprocess-based connectors.
    """
    check_enabled = None
    connector_name = '<connector-name-empty>'
    callback_suffix = '<callback-suffix-empty>'
    ipc_config_name = '<ipc-config-name-empty>'
    auth_username = '<auth-username-empty>'
    pidfile_suffix = 'not-configured'

    connector_module = '<connector-module-empty>'

    action_definition_create = None
    action_outgoing_create = None
    action_channel_create = None
    action_ping = None

# ################################################################################################################################

    def __init__(self, server):
        # type: (ParallelServer)
        self.server = server

# ################################################################################################################################

    def _check_enabled(self):
        if not self.server.fs_server_config.component_enabled[self.check_enabled]:
            raise Exception(not_enabled_pattern.format(**{
                'connector_name': self.connector_name,
                'check_enabled': self.check_enabled
            }))

# ################################################################################################################################

    def get_credentials(self):
        """ Returns a username/password pair using which it is possible to authenticate with a connector.
        """
        config = self.server.worker_store.basic_auth_get(self.auth_username)['config']
        return config.username, config.password

# ################################################################################################################################

    def start_connector(self, ipc_tcp_start_port, timeout=5):
        """ Starts an HTTP server acting as an connector process. Its port will be greater than ipc_tcp_start_port,
        which is the starting point to find a free port from.
        """
        if self.check_enabled:
            self._check_enabled()

        self.ipc_tcp_port = get_free_port(ipc_tcp_start_port)
        logger.info('Starting {} connector for server `%s` on `%s`'.format(self.connector_name),
            self.server.name, self.ipc_tcp_port)

        # Credentials for both servers and connectors
        username, password = self.get_credentials()

        # Employ IPC to exchange subprocess startup configuration
        self.server.connector_config_ipc.set_config(self.ipc_config_name, dumps({
            'port': self.ipc_tcp_port,
            'username': username,
            'password': password,
            'server_port': self.server.port,
            'server_name': self.server.name,
            'server_path': '/zato/internal/callback/{}'.format(self.callback_suffix),
            'base_dir': self.server.base_dir,
            'needs_pidfile': not self.server.has_fg,
            'pidfile_suffix': self.pidfile_suffix,
            'logging_conf_path': self.server.logging_conf_path
        }))

        # Start connector in a sub-process
        start_python_process('{} connector'.format(self.connector_name), False, self.connector_module, '', extra_options={
            'deployment_key': self.server.deployment_key,
            'shmem_size': self.server.shmem_size
        })

        # Wait up to timeout seconds for the connector to start as indicated by its responding to a PING request
        now = datetime.utcnow()
        warn_after = now + timedelta(seconds=3)
        should_warn = False
        until = now + timedelta(seconds=timeout)
        is_ok = False
        address = address_pattern.format(self.ipc_tcp_port, 'ping')
        auth = self.get_credentials()

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
            logger.warn('{} connector (%s) could not be started after %s'.format(self.connector_name), address, timeout)
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

    def ping(self, id):
        return self.invoke_connector({
            'action': self.action_ping.value,
            'id': id
        })

# ################################################################################################################################

    def send_message(self, msg):
        if self.check_enabled:
            self._check_enabled()

        msg['action'] = self.action_send.value
        response = self.invoke_connector(msg)

        # If we are here, it means that there was no error because otherwise an exception
        # would have been raised by invoke_connector.
        response = loads(response.text)

        return response

# ################################################################################################################################

    def invoke_connector(self, msg, raise_on_error=True, address_pattern=address_pattern):
        if self.check_enabled:
            self._check_enabled()

        address = address_pattern.format(self.ipc_tcp_port, 'api')
        response = post(address, data=dumps(msg), auth=self.get_credentials())

        if not response.ok:
            if raise_on_error:
                raise Exception(response.text)
            else:
                logger.warn('Error message from {} connector `{}`'.format(self.connector_name, response.text))
        else:
            return response

# ################################################################################################################################

    def _create_initial_objects(self, config_dict, action, text_pattern, text_func):
        for value in config_dict.values():
            config = value['config']
            logger.info(text_pattern, text_func(config))
            config['action'] = action.value
            self.invoke_connector(config, False)

# ################################################################################################################################

    def create_initial_definitions(self, config_dict, text_func):
        text_pattern = 'Creating {} definition `%s`'.format(self.connector_name)
        self._create_initial_objects(config_dict, self.action_definition_create, text_pattern, text_func)

# ################################################################################################################################

    def create_initial_outconns(self, config_dict, text_func):
        text_pattern = 'Creating {} outconn `%s`'.format(self.connector_name)
        self._create_initial_objects(config_dict, self.action_outgoing_create, text_pattern, text_func)

# ################################################################################################################################

    def create_initial_channels(self, config_dict, text_func):
        text_pattern = 'Creating {} channel `%s`'.format(self.connector_name)
        self._create_initial_objects(config_dict, self.action_channel_create, text_pattern, text_func)

# ################################################################################################################################
