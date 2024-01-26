# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from binascii import unhexlify
from http.client import RemoteDisconnected

# Requests
from requests.exceptions import ConnectionError

# urllib3
from urllib3.exceptions import ProtocolError

# Zato
from zato.common.api import IPC, WebSphereMQCallData
from zato.common.broker_message import CHANNEL, DEFINITION, OUTGOING
from zato.common.exception import ConnectorClosedException
from zato.server.connection.connector.subprocess_.ipc import SubprocessIPC

# ################################################################################################################################
# ################################################################################################################################

_connector_not_reachable = (ConnectionError, ProtocolError, RemoteDisconnected, ConnectorClosedException)

# ################################################################################################################################
# ################################################################################################################################

class IBMMQIPC(SubprocessIPC):
    """ Implements communication with an IBM MQ connector for a given server.
    """
    check_enabled = 'ibm_mq'
    connector_name = 'IBM MQ'
    callback_suffix = 'wmq'
    ipc_config_name = 'zato-ibm-mq'
    auth_username = IPC.CONNECTOR.USERNAME.IBM_MQ
    pidfile_suffix = 'ibm-mq'

    connector_module = 'zato.server.connection.connector.subprocess_.impl.ibm_mq'

    action_definition_create = DEFINITION.WMQ_CREATE
    action_outgoing_create = OUTGOING.WMQ_CREATE
    action_channel_create = CHANNEL.WMQ_CREATE
    action_send = OUTGOING.WMQ_SEND
    action_ping = DEFINITION.WMQ_PING

# ################################################################################################################################

# Public API methods

# ################################################################################################################################

    def start_ibm_mq_connector(self, *args, **kwargs):
        return self.start_connector(*args, **kwargs)

# ################################################################################################################################

    def invoke_wmq_connector(self, *args, **kwargs):
        return self.invoke_connector(*args, **kwargs)

# ################################################################################################################################

    def send_wmq_message(self, *args, **kwargs):
        try:
            out = self.send_message(*args, **kwargs)
        except Exception as e:
            if isinstance(e, _connector_not_reachable):
                raise ConnectorClosedException(e, 'IBM MQ connector not reachable')
            else:
                raise
        else:
            return WebSphereMQCallData(unhexlify(out['msg_id']).strip(), unhexlify(out['correlation_id']).strip())

    def ping_wmq(self, *args, **kwargs):
        return self.ping(*args, **kwargs)

# ################################################################################################################################

    def create_initial_wmq_definitions(self, config_dict):
        def text_func(config):
            return '{} {}:{} (queue manager:{})'.format(config['name'], config['host'], config['port'], config['queue_manager'])

        return self.create_initial_definitions(config_dict, text_func)

# ################################################################################################################################

    def create_initial_wmq_outconns(self, config_dict):
        def text_func(config):
            return config['name']

        return self.create_initial_outconns(config_dict, text_func)

# ################################################################################################################################

    def create_initial_wmq_channels(self, config_dict):
        def text_func(config):
            return config['name']

        return self.create_initial_channels(config_dict, text_func)

# ################################################################################################################################
# ################################################################################################################################
