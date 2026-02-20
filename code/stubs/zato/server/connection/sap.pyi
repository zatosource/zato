from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
from logging import getLogger
from traceback import format_exc
from zato.common.util.api import ping_sap
from zato.common.const import SECRETS
from zato.server.connection.queue import Wrapper
import pyrfc

class SAPWrapper(Wrapper):
    pyrfc: Any
    def __init__(self: Any, config: Any, server: Any) -> None: ...
    def add_client(self: Any) -> None: ...
