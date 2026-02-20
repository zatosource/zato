from typing import Any, TYPE_CHECKING

from dacite.core import from_dict
from zato.common.typing_ import callnone, dataclass, intnone, stranydict, strnone
from zato.common.model.connector import ConnectorConfig


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
    def from_dict(config_dict: stranydict) -> AMQPConnectorConfig: ...
