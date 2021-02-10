# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import Callable, Optional as optional

# Zato
from zato.common.dataclasses_ import dataclass
from zato.common.model.connector import ConnectorConfig

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class AMQPConnectorConfig(ConnectorConfig):
    host: str
    queue: str
    ack_mode: str
    conn_url: str
    username: str
    frame_max: int
    prefetch_count: int
    get_conn_class_func: Callable
    consumer_tag_prefix: optional[str]

# ################################################################################################################################
# ################################################################################################################################


