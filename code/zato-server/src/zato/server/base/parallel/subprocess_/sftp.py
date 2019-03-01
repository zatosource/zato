# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from binascii import unhexlify

# Zato
from zato.common import IPC
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

    connector_module = 'zato.server.connection.connector.subprocess_.impl.sftp'

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

    def send_sftp_message(self, *args, **kwargs):
        out = self.send_message(*args, **kwargs)
        return out
        #return WebSphereMQCallData(unhexlify(out['msg_id']).strip(), unhexlify(out['correlation_id']).strip())

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

