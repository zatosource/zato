# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.api import IPC
from zato.common.broker_message import OUTGOING
from zato.server.connection.connector.subprocess_.ipc import SubprocessIPC

# ################################################################################################################################
# ################################################################################################################################

class SFTPIPC(SubprocessIPC):
    """ Implements communication with an SFTP connector for a given server.
    """
    connector_name = 'SFTP'
    callback_suffix = 'sftp'
    ipc_config_name = 'zato-sftp'
    auth_username = IPC.CONNECTOR.USERNAME.SFTP
    pidfile_suffix = 'sftp'

    connector_module = 'zato.server.connection.connector.subprocess_.impl.outconn_sftp'

    action_outgoing_create = OUTGOING.SFTP_CREATE
    action_send = OUTGOING.SFTP_EXECUTE
    action_ping = OUTGOING.SFTP_PING

# ################################################################################################################################

# Public API methods

# ################################################################################################################################

    def start_sftp_connector(self, *args, **kwargs):
        return self.start_connector(*args, **kwargs)

# ################################################################################################################################

    def invoke_sftp_connector(self, *args, **kwargs):
        return self.invoke_connector(*args, **kwargs)

# ################################################################################################################################

    def ping_sftp(self, *args, **kwargs):
        return self.ping(*args, **kwargs)

# ################################################################################################################################

    def create_initial_sftp_outconns(self, config_dict):
        def text_func(config):
            return config['name']
        return self.create_initial_outconns(config_dict, text_func)

# ################################################################################################################################
# ################################################################################################################################
