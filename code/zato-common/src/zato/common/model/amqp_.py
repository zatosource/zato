# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import Callable, Optional as optional

# Zato
from zato.common.dataclasses_ import dataclass, from_dict
from zato.common.model.connector import ConnectorConfig

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class AMQPConnectorConfig(ConnectorConfig):
    host: str
    queue: optional[str]
    ack_mode: optional[str]
    conn_url: optional[str]
    username: str
    vhost: str
    frame_max: int
    prefetch_count: optional[int]
    get_conn_class_func: optional[Callable]
    consumer_tag_prefix: optional[str]

    @staticmethod
    def from_dict(config_dict):
        # type: (dict) -> AMQPConnectorConfig
        return from_dict(AMQPConnectorConfig, config_dict)


# ################################################################################################################################
# ################################################################################################################################


