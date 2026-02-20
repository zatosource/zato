from typing import Any, TYPE_CHECKING

from datetime import datetime
from logging import getLogger
from zato.common import CHANNEL
from zato.common.util import spawn_greenlet
from zato.server.pattern.model import CacheEntry, InvocationResponse, ParallelCtx, Target
from zato.server.service import Service


class ParallelBase:
    call_channel: Any
    on_target_channel: Any
    on_final_channel: Any
    needs_on_final: Any
    source: Any
    cache: Any
    lock: Any
    cid: Any
    def __init__(self: Any, source: Any, cache: Any, lock: Any) -> None: ...
    def _invoke(self: Any, ctx: Any) -> None: ...
    def invoke(self: Any, targets: Any, on_final: Any, on_target: Any = ..., cid: Any = ..., _utcnow: Any = ...) -> None: ...
    def on_call_finished(self: Any, invoked_service: Any, response: Any, exception: Any, _utcnow: Any = ...) -> None: ...

class ParallelExec(ParallelBase):
    call_channel: Any
    on_target_channel: Any
    def invoke(self: Any, targets: Any, on_target: Any, cid: Any = ...) -> None: ...

class FanOut(ParallelBase):
    call_channel: Any
    on_target_channel: Any
    on_final_channel: Any
    needs_on_final: Any
