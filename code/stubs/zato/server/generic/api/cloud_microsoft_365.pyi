from typing import Any, TYPE_CHECKING

from logging import getLogger
from traceback import format_exc
from zato.common.typing_ import cast_
from zato.server.connection.cloud.microsoft_365 import Microsoft365Client
from zato.server.connection.queue import Wrapper
from zato.common.typing_ import any_
from O365 import Account as Office365Account


class CloudMicrosoft365Wrapper(Wrapper):
    def __init__(self: Any, config: any_, server: any_) -> None: ...
    def add_client(self: Any) -> None: ...
    def ping(self: Any) -> None: ...
