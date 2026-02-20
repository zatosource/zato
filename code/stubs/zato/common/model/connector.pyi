from typing import Any, TYPE_CHECKING

from zato.common.typing_ import boolnone, dataclass, intnone, strnone
from zato.server.base.parallel import ParallelServer


class ConnectorConfig:
    id: int
    name: str
    port: intnone
    address: strnone
    is_active: boolnone
    pool_size: intnone
    def_name: strnone
    old_name: strnone
    password: strnone
    service_name: strnone
