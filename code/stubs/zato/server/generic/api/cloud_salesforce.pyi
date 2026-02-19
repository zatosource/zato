from typing import Any

from logging import getLogger
from traceback import format_exc
from zato.common.typing_ import cast_
from zato.server.connection.salesforce import SalesforceClient
from zato.server.connection.queue import Wrapper
from zato.common.typing_ import stranydict

class _SalesforceClient:
    def __init__(self: Any, config: stranydict) -> None: ...

class CloudSalesforceWrapper(Wrapper):
    def __init__(self: Any, config: stranydict, server: Any) -> None: ...
    def add_client(self: Any) -> None: ...
    def ping(self: Any) -> None: ...
