# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import Callable as callable_, Optional as optional

# Zato
from zato.common.typing_ import dataclass, from_dict
from zato.common.model.connector import ConnectorConfig

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class WSXConnectorConfig(ConnectorConfig):
    path: optional[str]
    needs_auth: optional[bool]
    sec_name: optional[str]
    sec_type: optional[str]
    data_format: optional[str]
    token_ttl: optional[int]
    new_token_wait_time: int
    max_len_messages_sent: optional[int]
    max_len_messages_received: optional[int]
    hook_service: optional[callable_]
    auth_func: optional[callable_]
    vault_conn_default_auth_method: optional[str]
    on_message_callback: optional[callable_]
    parallel_server: optional[object] = None
    pings_missed_threshold: optional[int] = 5
    is_audit_log_sent_active: optional[bool] = False
    is_audit_log_received_active: optional[bool] = False

    @staticmethod
    def from_dict(config_dict):
        # type: (dict) -> WSXConnectorConfig
        return from_dict(WSXConnectorConfig, config_dict)

# ################################################################################################################################
# ################################################################################################################################
