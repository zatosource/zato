# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# dacite
from dacite.core import from_dict

# Zato
from zato.common.typing_ import callnone, dataclass, intnone, stranydict, strnone
from zato.common.model.connector import ConnectorConfig

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class AMQPConnectorConfig(ConnectorConfig):
    host: str
    queue: strnone
    ack_mode: strnone
    conn_url: strnone
    username: str
    vhost: str
    frame_max: int
    prefetch_count: intnone
    get_conn_class_func: callnone
    consumer_tag_prefix: strnone

    @staticmethod
    def from_dict(config_dict:'stranydict') -> 'AMQPConnectorConfig':
        return from_dict(AMQPConnectorConfig, config_dict)

# ################################################################################################################################
# ################################################################################################################################
