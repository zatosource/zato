# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta
from http.client import NOT_ACCEPTABLE, SERVICE_UNAVAILABLE
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import sleep

# requests
from requests import get, post

# Zato
from zato.common.exception import ConnectorClosedException
from zato.common.json_internal import dumps, loads
from zato.common.util.api import get_free_port
from zato.common.util.config import get_url_protocol_from_config_item
from zato.common.util.proc import start_python_process

# ################################################################################################################################

if 0:
    from requests import Response
    from zato.server.base.parallel import ParallelServer
    ParallelServer = ParallelServer
    Response = Response

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

address_pattern='{}://127.0.0.1:{}/{}'
not_enabled_pattern  = '{connector_name} component is not enabled - install PyMQI, set component_enabled.{check_enabled} '
not_enabled_pattern += 'to True in server.conf and restart all servers before {connector_name} connections can be used.'

# ################################################################################################################################

_closed_status_code = (NOT_ACCEPTABLE, SERVICE_UNAVAILABLE)

# ################################################################################################################################

class SubprocessIPC:
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

    def __init__(self, server:'ParallelServer') -> 'None':
        self.server = server
        self.api_protocol = get_url_protocol_from_config_item(self.server.use_tls)
        self.ipc_tcp_port:'int | None' = None

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

    def start_connector(self, ipc_tcp_start_port, timeout=5, extra_options_kwargs=None):
        """ Starts an HTTP server acting as an connector process. Its port will be greater than ipc_tcp_start_port,
        which is the starting point to find a free port from.
        """
        # Ensure we are enabled before we continue
        if self.check_enabled:
            self._check_enabled()

        # Turn into a dict for later use
        extra_options_kwargs = extra_options_kwargs or {}

        self.ipc_tcp_port = get_free_port(ipc_tcp_start_port)
        logger.info('Starting {} connector for server `%s` on port `%s`'.format(self.connector_name),
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
        self._start_connector_process(extra_options_kwargs)

        # Wait up to timeout seconds for the connector to start as indicated by its responding to a PING request
        now = datetime.utcnow()
        warn_after = now + timedelta(seconds=60)
        should_warn = False
        until = now + timedelta(seconds=timeout)
        is_ok = False
        address = address_pattern.format(self.api_protocol, self.ipc_tcp_port, 'ping')
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
            logger.warning('{} connector (%s) could not be started after %s'.format(self.connector_name), address, timeout)
        else:
            return is_ok

# ################################################################################################################################

    def _start_connector_process(self, extra_options_kwargs):
        # type: (dict) -> None

        # Base extra options
        extra_options={
            'deployment_key': self.server.deployment_key,
            'shmem_size': self.server.shmem_size
        }

        # Merge any additional ones
        extra_options.update(extra_options_kwargs)

        # Start the process now
        start_python_process(
            '{} connector'.format(self.connector_name),
            False,
            self.connector_module,
            '',
            extra_options=extra_options,
            stderr_path=self.server.stderr_path
        )

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
        # type: (dict) -> None
        if self.check_enabled:
            self._check_enabled()

        for k, v in msg.items():
            if isinstance(v, bytes):
                msg[k] = v.decode('utf8')

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

        address = address_pattern.format(self.api_protocol, self.ipc_tcp_port, 'api')
        response = post(address, data=dumps(msg), auth=self.get_credentials()) # type: Response

        if not response.ok:
            if raise_on_error:
                if response.status_code in _closed_status_code:
                    raise ConnectorClosedException(None, response.text)
                else:
                    raise Exception(response.text)
            else:
                logger.warning('Error message from {} connector `{}`'.format(self.connector_name, response.text))
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
# ################################################################################################################################
