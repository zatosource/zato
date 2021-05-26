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

    # A unique identifer assigned to this event by Zato
    id: str

    # A correlation ID assigned by Zato - multiple events may have the same CID
    cid: str

    # In reply to which previous event this one was generated (also assigned by Zato)
    in_reply_to: optional[str]

    # To what group the event belongs
    group_id: optional[int]

    # To what subgroup the event belongs
    sub_group_id: optional[int]

    # ID of this event as it was assigned by an external system
    ext_id: optional[str]

    # A correlation ID ID of this event as it was assigned by an external system
    ext_cid: optional[str]

    # What is ID that the external system is replying to (as understood by the system)
    ext_cid: optional[str]

    # A group ID this event belongs to, as it was assigned by an external system
    ext_group_id: optional[str]

    # What triggered this event, in broad terms, e.g. a Zato service
    source_type: int

    # What is the ID of the source
    source_id: str

    # A further restriction of the source type
    source_sub_type: optional[int]

    # What Zato user triggered the event
    user_id: optional[str]

    # Source system of the user_id attribute
    user_source: optional[str]

    # What external user triggered the event
    ext_user_id: optional[str]

    # Source system of the ext_user_id attribute
    ext_user_source: optional[str]

    # Timestamp of this event, as assigned by Zato, e.g.
    timestamp: str

    # Timestamp of this event, as assigned by an external system
    ext_timestamp: optional[str]

    # Year of this event, e.g. 2098
    year: int

    # Month of this event, e.g. 1 for January
    month: int

    # Day of month of this event, e.g. 29
    day: int

    # A concatenation of year and month, e.g. 2098-01 For January, 2098
    date_ym: str

    # A concatenation of year, month and day, e.g. 2098-01-30 For January the 30th, 2098
    date_ymd: str

    # An hour of day of this event, e.g. 1 for 1 AM or 13 for 13:00 (1 PM)
    hour: int

    # Day of calendar week of this event, from 1 to 7 where 1=Monday.
    day_of_week: int

    # Total time this event took
    total_time_ms: optional[int] # In milliseconds (lower precision than ns)

    # As above, in ns
    total_time_ns: optional[int] # In nanoseconds  (full precision, if possible)

    # What sort of an object this event is about
    object_type: optional[str]

    # Type of the object the event is about
    object_id: optional[str]

    # A further restriction of the object's type
    object_sub_type: optional[str]

    # What category this event belongs to
    cat_id: optional[int]

    # What subcategory this event belongs to
    sub_cat_id: optional[int]

    # What category this event belongs to (assigned by an external system)
    ext_cat_id: optional[str]

    # What subcategory this event belongs to (assigned by an external system)
    ext_sub_cat_id: optional[str]

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
