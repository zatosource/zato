# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from logging import DEBUG
from http.client import BAD_REQUEST, FORBIDDEN, INTERNAL_SERVER_ERROR, NOT_ACCEPTABLE, OK, responses, SERVICE_UNAVAILABLE
from time import sleep
from traceback import format_exc

# Bunch
from bunch import Bunch, bunchify

# Zato
from zato.common.util.json_ import dumps
from zato.server.connection.jms_wmq.jms import WebSphereMQException, NoMessageAvailableException
from zato.server.connection.jms_wmq.jms.connection import WebSphereMQConnection
from zato.server.connection.jms_wmq.jms.core import TextMessage
from zato.server.connection.connector.subprocess_.base import BaseConnectionContainer, Response

# ################################################################################################################################

# 1 MB = 8,000 kilobits
mb_to_kbit = 8000

# ################################################################################################################################
# ################################################################################################################################

class SFTPConnection(object):

    def __init__(self, logger, **config):
        self.logger = logger
        self.config = bunchify(config)     # type: Bunch

        print(self.config)

        self.id = self.config.id                # type: int
        self.name = self.config.name            # type: str
        self.is_active = self.config.is_active  # type: str

        self.host = self.config.host or ''      # type: str
        self.port = self.config.port or None     # type: int

        self.username = self.config.username       # type: str
        self.password = self.config.password or '' # type: str
        self.secret = self.config.secret or ''     # type: str

        self.sftp_command = self.config.sftp_command # type: str
        self.ping_command = self.config.ping_command # type: str

        self.identity_file = self.config.identity_file or ''     # type: str
        self.ssh_config_file = self.config.ssh_config_file or '' # type: str

        self.log_level = int(self.config.log_level)  # type: int
        self.should_flush = self.config.should_flush # type: bool
        self.buffer_size = self.config.buffer_size   # type: int

        self.ssh_options = self.config.ssh_options or ''     # type: str
        self.force_ip_type = self.config.force_ip_type or '' # type: str

        self.should_preserve_meta = self.config.should_preserve_meta     # type: bool
        self.is_compression_enabled = self.config.is_compression_enabled # type: bool

        # SFTP expects kilobits instead of megabytes
        self.bandwidth_limit = float(self.config.bandwidth_limit) * mb_to_kbit # type: float

        # Added for API completeness
        self.is_connected = True

# ################################################################################################################################

    def execute(self, data):
        """ Executes a single or multiple SFTP commands from the input 'data' string.
        """

# ################################################################################################################################

    def connect(self):
        # We do not maintain long-running connections but we may still want to ping the remote end
        # to make sure we are actually able to connect to it.
        return self.ping()

# ################################################################################################################################

    def close(self):
        # Added for API completeness
        pass

# ################################################################################################################################

    def ping(self):
        self.logger.warn('QQQ %s', self.config)

# ################################################################################################################################
# ################################################################################################################################

class SFTPConnectionContainer(BaseConnectionContainer):

    connection_class = SFTPConnection
    ipc_name = conn_type = logging_file_name = 'sftp'

    remove_id_from_def_msg = False
    remove_name_from_def_msg = False

# ################################################################################################################################

    def _on_OUTGOING_SFTP_PING(self, msg):
        return super(SFTPConnectionContainer, self).on_definition_ping(msg)

# ################################################################################################################################

    def _on_OUTGOING_SFTP_DELETE(self, msg):
        return super(SFTPConnectionContainer, self).on_definition_delete(msg)

    _on_GENERIC_CONNECTION_EDIT = _on_OUTGOING_SFTP_DELETE

# ################################################################################################################################

    def _on_OUTGOING_SFTP_CREATE(self, msg):
        return super(SFTPConnectionContainer, self).on_definition_create(msg)

# ################################################################################################################################

    def _on_OUTGOING_SFTP_EDIT(self, msg):
        return super(SFTPConnectionContainer, self).on_definition_edit(msg)

    _on_GENERIC_CONNECTION_EDIT = _on_OUTGOING_SFTP_EDIT

# ################################################################################################################################

    def _on_OUTGOING_SFTP_CHANGE_PASSWORD(self, msg):
        return super(SFTPConnectionContainer, self).on_definition_change_password(msg)

    _on_GENERIC_CONNECTION_CHANGE_PASSWORD = _on_OUTGOING_SFTP_CHANGE_PASSWORD

# ################################################################################################################################

    def _on_OUTGOING_SFTP_EXECUTE(self, msg, is_reconnect=False):
        pass

# ################################################################################################################################

if __name__ == '__main__':

    container = SFTPConnectionContainer()
    container.run()

# ################################################################################################################################

'''
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Bunch
from bunch import Bunch, bunchify

# sh
from sh import sftp

print(333, `sftp`)

# ################################################################################################################################

logging.basicConfig(level=logging.INFO)

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

# 1 MB = 8,000 kilobits
mb_to_kbit = 8000

# ################################################################################################################################
# ################################################################################################################################

class SFTPConnection(object):

    def __init__(self, logger, **config):
        self.logger = logger
        self.config = bunchify(config)     # type: Bunch

        self.id = self.config.id                # type: int
        self.name = self.config.name            # type: str
        self.is_active = self.config.is_active  # type: str

        self.host = self.config.host or ''      # type: str
        self.port = self.config.port or None     # type: int

        self.username = self.config.username       # type: str
        self.password = self.config.password or '' # type: str
        self.secret = self.config.secret or ''     # type: str

        self.sftp_command = self.config.sftp_command # type: str
        self.ping_command = self.config.ping_command # type: str

        self.identity_file = self.config.identity_file or ''     # type: str
        self.ssh_config_file = self.config.ssh_config_file or '' # type: str

        self.log_level = int(self.config.log_level)  # type: int
        self.should_flush = self.config.should_flush # type: bool
        self.buffer_size = self.config.buffer_size   # type: int

        self.ssh_options = self.config.ssh_options or ''     # type: str
        self.force_ip_type = self.config.force_ip_type or '' # type: str

        self.should_preserve_meta = self.config.should_preserve_meta     # type: bool
        self.is_compression_enabled = self.config.is_compression_enabled # type: bool

        # SFTP expects kilobits instead of megabytes
        self.bandwidth_limit = float(self.config.bandwidth_limit) * mb_to_kbit # type: float

        # Added for API completeness
        self.is_connected = True

# ################################################################################################################################

    def execute(self, data):
        """ Executes a single or multiple SFTP commands from the input 'data' string.
        """
        print(111, data)

# ################################################################################################################################

    def connect(self):
        # We do not maintain long-running connections but we may still want to ping the remote end
        # to make sure we are actually able to connect to it.
        self.ping()

# ################################################################################################################################

    def close(self):
        # Added for API completeness
        pass

# ################################################################################################################################

    def ping(self):
        self.execute(self.ping_command)

# ################################################################################################################################
# ################################################################################################################################

config = {
    'id': 123,
    'name': 'My SFTP connection',
    'is_active': True,

    'host': 'localhost',
    'port': 22,

    'username': None,
    'password': None,
    'secret': None,

    'sftp_command': 'sftp',
    'ping_command': 'ls .',

    'identity_file': None,
    'ssh_config_file': None,

    'log_level': 4,
    'should_flush': True,
    'buffer_size': 32678,

    'ssh_options': None,
    'force_ip_type': None,

    'should_preserve_meta': True,
    'is_compression_enabled': True,

    'bandwidth_limit': '10'
}

conn = SFTPConnection(logger, **config)
conn.connect()
command = 'whoami'
result = conn.execute(command)
'''
