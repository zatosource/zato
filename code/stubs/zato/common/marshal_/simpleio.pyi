from typing import Any

from logging import getLogger
from traceback import format_exc
from orjson import loads
from zato.common import DATA_FORMAT
from zato.common.marshal_.api import Model
from dataclasses import Field
from zato.common.typing_ import any_
from zato.cy.simpleio import SIOServerConfig
from zato.server.base.parallel import ParallelServer
from zato.server.service import Service

class DataClassSimpleIO:
    service_class: Service
    is_dataclass: Any
    server: Any
    server_config: Any
    user_declaration: Any
    def __init__(self: Any, server: Any, server_config: Any, user_declaration: Any) -> None: ...
    @staticmethod
    def attach_sio(server: Any, server_config: Any, class_: Any) -> None: ...
    def parse_input(self: Any, data: Any, data_format: Any, service: Any, extra: Any) -> any_: ...
