from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
from arrow import utcnow
from bunch import Bunch
from zato.common.json_internal import loads
from zato.server.service import Service
from zato.server.pattern.invoke_retry import RetryFailed, retry_failed_msg, retry_limit_reached_msg


class InvokeRetry(Service):
    def _retry(self: Any, remaining: Any) -> None: ...
    def _notify_callback(self: Any, is_ok: Any, response: Any) -> None: ...
    def _on_retry_finished(self: Any, g: Any) -> None: ...
    def handle(self: Any) -> None: ...
