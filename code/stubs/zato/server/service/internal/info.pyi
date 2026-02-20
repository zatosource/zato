from typing import Any, TYPE_CHECKING

from base64 import b64decode
from contextlib import closing
from zato.client import AnyServiceInvoker
from zato.common.api import INFO_FORMAT, MISC, SERVER_JOIN_STATUS, SERVER_UP_STATUS
from zato.common.component_info import format_info, get_info, get_worker_pids
from zato.common.const import ServiceConst
from zato.common.json_internal import dumps, loads
from zato.common.odb.query import server_list
from zato.common.util.config import get_url_protocol_from_config_item
from zato.server.service import List, Service
from zato.common.typing_ import any_


class GetInfo(Service):
    def handle(self: Any) -> None: ...

class GetServerInfo(Service):
    def handle(self: Any) -> None: ...

class GetWorkerPids(Service):
    output: any_
    def handle(self: Any) -> None: ...
