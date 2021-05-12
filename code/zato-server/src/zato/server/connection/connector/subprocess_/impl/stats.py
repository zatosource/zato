# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import Optional as optional

# gevent
from gevent.lock import RLock

# Pandas
import pandas as pd

# Zato
from zato.common.ext.dataclasses import dataclass

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Event:

    id: str
    cid: str

    in_reply_to: optional[str]
    group_id: optional[str]
    sub_group_id: optional[str]

    source_type: str
    source_id: str

    timestamp: str

    total_time_ms: optional[int] # In milliseconds (lower precision than ns)
    total_time_ns: optional[int] # In nanoseconds  (full precision, if possible)

    object_type: str
    object_id: str
    object_sub_type: optional[str]

    cat_id: optional[str]
    sub_cat_id: optional[str]

# ################################################################################################################################
# ################################################################################################################################

class StatsContainer:

    def __init__(self):

        # In-RAM database of events, saved to disk periodically in background
        self.in_ram_store = [] # type: list[Event]

        # An update lock used while modifying the in-RAM database
        self.update_lock = RLock()

        # We will save data to disk once in data many seconds
        self.storage_sync_interval = 30

# ################################################################################################################################

    def push(self, data):
        # type: (dict) -> None
        with self.update_lock:
            self.in_ram_store.append(data)

# ################################################################################################################################

    def sync_storage(self):
        with self.update_lock:
            f = pd.DataFrame(self.in_ram_store)

            print(111, f.memory_usage())

# ################################################################################################################################

    def run(self):
        pass

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    container = StatsContainer()
    container.run()

    event = {
        'id': 'abc',
        'cid': 'cid.1',
        'source_type': 'zato.server',
        'source_id': 'server1',
        'timestamp': '2021-05-12T07:07:01.4841',
        'object_type': 'zato.service',
        'object_id': '123',
    }

    n = 100_000

    for x in range(n):
        container.push(event)

    container.sync_storage()

# ################################################################################################################################
# ################################################################################################################################
