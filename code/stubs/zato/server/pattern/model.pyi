from typing import Any

from datetime import datetime
from typing import List as list_, Optional as optional
from zato.common.ext.dataclasses import dataclass

class Target:
    name: str
    payload: optional[object]

class ParallelCtx:
    cid: str
    req_ts_utc: datetime
    source_name: str
    target_list: list_[Target]
    on_target_list: optional[list]
    on_final_list: optional[list]

class CacheEntry:
    cid: str
    req_ts_utc: datetime
    len_targets: int
    remaining_targets: int
    target_responses: list
    final_responses: dict
    on_target_list: optional[list]
    on_final_list: optional[list]

class InvocationResponse:
    cid: str
    req_ts_utc: datetime
    resp_ts_utc: datetime
    response: optional[object]
    exception: optional[Exception]
    ok: bool
    source: str
    target: str
