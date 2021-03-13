# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from typing import List as list_, Optional as optional

# Zato
from zato.common.ext.dataclasses import dataclass

@dataclass(init=False)
class Target:
    target_name: str
    payload: optional[object] = None

@dataclass(init=False)
class ParallelCtx:
    cid: str
    req_ts_utc: datetime
    source_name: str
    target_list: list_[Target]
    on_target_list: optional[list] = None
    on_final_list: optional[list] = None
