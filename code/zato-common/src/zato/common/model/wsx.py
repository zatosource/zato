# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import Callable as callable_, Optional as optional

# Zato
from zato.common.api import WEB_SOCKET
from zato.common.typing_ import dataclass, from_dict
from zato.common.model.connector import ConnectorConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class WSXConnectorConfig(ConnectorConfig):
    host: 'str'
    port: 'int'
    needs_tls: 'bool'
    path: optional[str]
    needs_auth: optional[bool]
    sec_name: optional[str]
    sec_type: optional[str]
    data_format: str
    token_ttl: int
    new_token_wait_time: int
    max_len_messages_sent: optional[int]
    max_len_messages_received: optional[int]
    hook_service: optional[callable_]
    auth_func: callable_
    vault_conn_default_auth_method: optional[str]
    on_message_callback: callable_
    parallel_server: 'ParallelServer'
    pings_missed_threshold: optional[int] = WEB_SOCKET.DEFAULT.PINGS_MISSED_THRESHOLD
    ping_interval: optional[int] = WEB_SOCKET.DEFAULT.PING_INTERVAL
    is_audit_log_sent_active: optional[bool] = False
    is_audit_log_received_active: optional[bool] = False
    extra_properties: optional[str] = ''

    @staticmethod
    def from_dict(config_dict):
        # type: (dict) -> WSXConnectorConfig
        return from_dict(WSXConnectorConfig, config_dict)

# ################################################################################################################################
# ################################################################################################################################
