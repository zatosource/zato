from typing import Any

from errno import ENETUNREACH
from http.client import OK
from bunch import bunchify
from requests import get as requests_get
from requests.exceptions import ConnectionError
from zato.common.version import get_version
from zato.common.json_internal import loads
from zato.server.service import Service

class CheckUpdates(Service):
    def handle(self: Any) -> None: ...
    def _check(self: Any) -> None: ...
    def _check_notify(self: Any, _url_info: Any, self_major: Any, self_version: Any) -> None: ...
    def _get_current(self: Any, _url_info: Any, self_major: Any, self_version: Any) -> None: ...
