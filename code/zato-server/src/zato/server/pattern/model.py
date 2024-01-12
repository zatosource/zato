# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from typing import List as list_, Optional as optional

# Zato
from zato.common.ext.dataclasses import dataclass

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Target:
    name: str
    payload: optional[object] = None

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ParallelCtx:
    cid: str
    req_ts_utc: datetime
    source_name: str
    target_list: list_[Target]
    on_target_list: optional[list] = None
    on_final_list: optional[list] = None

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CacheEntry:
    cid: str
    req_ts_utc: datetime
    len_targets: int
    remaining_targets: int
    target_responses: list
    final_responses: dict
    on_target_list: optional[list] = None
    on_final_list: optional[list] = None

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class InvocationResponse:
    cid: str
    req_ts_utc: datetime
    resp_ts_utc: datetime
    response: optional[object]
    exception: optional[Exception]
    ok: bool
    source: str
    target: str

# ################################################################################################################################
# ################################################################################################################################
