# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.server.connection.connector.subprocess_.ipc import SubprocessIPC

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ZatoEventsIPC(SubprocessIPC):
    """ Implements communication with a Zato events connector for a given server.
    """
    check_enabled = False
    connector_name = 'Zato events'
    callback_suffix = 'zato_events'
    ipc_config_name = 'zato-events'
    auth_username = None
    pidfile_suffix = 'zato-events'

    connector_module = 'zato.server.connection.connector.subprocess_.impl.events.container'

# ################################################################################################################################

    def get_credentials(self):
        return '<ZatoEventsIPC-no-username>', '<ZatoEventsIPC-no-password>'

# ################################################################################################################################

    def _ping_connector(self, ignored_address, ignored_auth, should_warn):

        # stdlib
        import socket

        # Zato
        from zato.common.util.tcp import wait_until_port_taken

        # Wait a few seconds to ensure the connector started
        wait_until_port_taken(self.ipc_tcp_port, timeout=5)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: # type: socket
            try:
                s.settimeout(1)
                s.connect(('127.0.0.1', self.ipc_tcp_port))
            except Exception as e:
                logger.warning('IPC ping failed. Could not connect to 127.0.0.1:%s; e=%s', self.ipc_tcp_port, e.args)
            else:
                return True

# ################################################################################################################################

# Public API methods

# ################################################################################################################################

    def start_zato_events_connector(self, *args, **kwargs):
        return self.start_connector(*args, **kwargs)

# ################################################################################################################################

    def invoke_zato_events_connector(self, *args, **kwargs):
        return self.invoke_connector(*args, **kwargs)

# ################################################################################################################################
