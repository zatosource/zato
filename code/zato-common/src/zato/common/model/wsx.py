# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import WEB_SOCKET
from zato.common.typing_ import anynone, boolnone, callnone, dataclass, from_dict, intnone, strnone
from zato.common.model.connector import ConnectorConfig

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class WSXConnectorConfig(ConnectorConfig):
    host: strnone
    port: intnone
    needs_tls: boolnone
    path: strnone
    needs_auth: boolnone
    sec_name: strnone
    sec_type: strnone
    data_format: str
    token_ttl: int
    new_token_wait_time: int
    max_len_messages_sent: intnone
    max_len_messages_received: intnone
    hook_service: callnone
    auth_func: callnone
    vault_conn_default_auth_method: strnone
    on_message_callback: callnone
    parallel_server: anynone
    pings_missed_threshold: intnone = WEB_SOCKET.DEFAULT.PINGS_MISSED_THRESHOLD
    ping_interval: intnone = WEB_SOCKET.DEFAULT.PING_INTERVAL
    is_audit_log_sent_active: bool = False
    is_audit_log_received_active: boolnone = False
    extra_properties: strnone = ''

    @staticmethod
    def from_dict(config_dict):
        # type: (dict) -> WSXConnectorConfig
        return from_dict(WSXConnectorConfig, config_dict)

# ################################################################################################################################
# ################################################################################################################################
