# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.api import IPC
from zato.common.broker_message import CHANNEL
from zato.server.connection.connector.subprocess_.ipc import SubprocessIPC

# ################################################################################################################################
# ################################################################################################################################

class FTPIPC(SubprocessIPC):
    """ Implements communication with an FTP connector for a given server.
    """
    connector_name = 'FTP'
    callback_suffix = 'ftp'
    ipc_config_name = 'zato-ftp'
    auth_username = IPC.CONNECTOR.USERNAME.SFTP
    pidfile_suffix = 'ftp'

    connector_module = 'zato.server.connection.connector.subprocess_.impl.ftp'

    action_channel_create = CHANNEL.FTP_CREATE
    action_ping = CHANNEL.FTP_PING

# ################################################################################################################################

# Public API methods

# ################################################################################################################################

    def start_ftp_connector(self, *args, **kwargs):
        return self.start_connector(*args, **kwargs)

# ################################################################################################################################

    def invoke_ftp_connector(self, *args, **kwargs):
        return self.invoke_connector(*args, **kwargs)

# ################################################################################################################################

    def ping_ftp(self, *args, **kwargs):
        return self.ping(*args, **kwargs)

# ################################################################################################################################

    def create_initial_ftp_channels(self, config_dict):
        def text_func(config):
            return config['name']
        return self.create_initial_channels(config_dict, text_func)

# ################################################################################################################################
# ################################################################################################################################
