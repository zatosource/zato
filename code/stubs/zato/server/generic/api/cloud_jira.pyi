from typing import Any, TYPE_CHECKING

from logging import getLogger
from traceback import format_exc
from zato.common.typing_ import cast_
from zato.server.connection.jira_ import JiraClient
from zato.server.connection.queue import Wrapper
from bunch import Bunch
from requests import Response
from zato.common.typing_ import any_, stranydict, strnone
from zato.server.base.parallel import ParallelServer


class _JiraClient(JiraClient):
    def __init__(self: Any, config: stranydict) -> None: ...
    def ping(self: Any) -> None: ...

class CloudJiraWrapper(Wrapper):
    def __init__(self: Any, config: Bunch, server: ParallelServer) -> None: ...
    def add_client(self: Any) -> None: ...
    def ping(self: Any) -> None: ...
    def delete(self: Any, ignored_reason: strnone = ...) -> None: ...
