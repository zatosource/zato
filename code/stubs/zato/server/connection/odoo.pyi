from typing import Any

from logging import getLogger
from zato.common.const import SECRETS
from zato.common.util.api import ping_odoo
from zato.server.connection.queue import ConnectionQueue
from six import PY2
import openerplib as client_lib
import odoolib as client_lib

class OdooWrapper:
    def __init__(self: Any, config: Any, server: Any) -> None: ...
    def build_queue(self: Any) -> None: ...
    def add_client(self: Any) -> None: ...
