# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import datetime
from logging import basicConfig, getLogger, INFO
from typing import Optional as optional

# gevent
from gevent import sleep, spawn_later
from gevent.lock import RLock

# Humanize
from humanize import intcomma as int_to_comma

# Pandas
import pandas as pd

# Zato
from zato.common.ext.dataclasses import dataclass
from zato.common.util import spawn_greenlet

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pandas import DataFrame
    DataFrame = DataFrame

# ################################################################################################################################
# ################################################################################################################################

basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

utcnow = datetime.utcnow

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

    # What the ID of the source is
    source_id: str

    # What the recipient of this event is, in broad terms, e.g. an external system
    recipient_type: int

    # What the ID of the recipient is
    recipient_id: str

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

class EventsDatabase:

    def __init__(self, fs_data_path, sync_threshold, sync_interval):
        # type: (self, int, int) -> None

        # Where to keep persistent data
        self.fs_data_path = fs_data_path

        # Sync to storage once in that many events ..
        self.sync_threshold = sync_threshold

        # .. or once in that many milliseconds
        self.sync_interval = sync_interval

        # In-RAM database of events, saved to disk periodically in background
        self.in_ram_store = [] # type: list[Event]

        # Total events received since startup
        self.total_events = 0

        # How many events we have received since the last synchronisation with persistent storage
        self.num_events_since_sync = 0

        # Reset each time we synchronise in-RAM state with the persistent storage
        self.last_sync_time = utcnow()

        # An update lock used while modifying the in-RAM database
        self.update_lock = RLock()

# ################################################################################################################################

    def should_sync(self):
        # type: () -> bool
        sync_by_threshold = self.num_events_since_sync % self.sync_threshold == 0
        sync_by_time = (utcnow() - self.last_sync_time).total_seconds() * 1000 >= self.sync_interval

        return sync_by_threshold or sync_by_time

# ################################################################################################################################

    def push(self, data):
        # type: (dict) -> None
        with self.update_lock:

            # Store in RAM ..
            self.in_ram_store.append(data)

            # .. update counters ..
            self.num_events_since_sync += 1
            self.total_events += 1

            # .. check if we should sync RAM with persistent storage ..
            if self.should_sync():

                # .. save in persistent storage ..
                self.sync_storage()

                # .. update metadata.
                self.num_events_since_sync = 0
                self.last_sync_time = utcnow()

# ################################################################################################################################

    def _get_data_from_storage(self):
        """ Reads existing data from persistent storage and returns it as a DataFrame.
        """
        # Let's check if we already have anything in storage ..
        if os.path.exists(self.fs_data_path):

            #  Let the users know what we are doing ..
            logger.info('Loading DF data from %s', self.fs_data_path)

            # .. load existing data from storage ..
            start = utcnow()
            existing = pd.read_parquet(self.fs_data_path) # type: pd.DataFrame

            # .. log the time it took to load the data ..
            logger.info('DF data loaded in %s; len_existing=%s', utcnow() - start, int_to_comma(existing.size))
        else:

            # .. create a new DF instead ..
            existing = pd.DataFrame()

        # .. return the result, no matter where it came from.
        return existing

# ################################################################################################################################

    def _get_data_from_ram(self):
        """ Turns data currently stored in RAM into a DataFrame.
        """
        # type: () -> None

        #  Let the users know what we are doing ..
        logger.info('Building DF out of len_current=%s', int_to_comma(len(self.in_ram_store)))

        # .. convert the data collected so far into a DataFrame ..
        start = utcnow()
        current = pd.DataFrame(self.in_ram_store)

        # .. log the time it took build the DataFrame ..
        logger.info('DF built in %s', utcnow() - start)

        return current

# ################################################################################################################################

    def _combine_data(self, existing, current):
        """ Combines on disk and in-RAM data.
        """
        # type: (DataFrame, DataFrame) -> DataFrame

        # Let the user know what we are doing ..
        logger.info('Combining existing and current data')

        # .. combine the existing and current data ..
        start = utcnow()
        combined = pd.concat([existing, current])

        # .. log the time it took to combine the DataFrames..
        logger.info('DF combined in %s', utcnow() - start)

        return combined

# ################################################################################################################################

    def _save_data(self, data):
        # type: (DataFrame) -> None

        # Let the user know what we are doing ..
        logger.info('Saving DF to %s', self.fs_data_path)

        # .. save the DF to persistent storage ..
        start = utcnow()
        data.to_parquet(self.fs_data_path)

        # .. log the time it took to save to storage ..
        logger.info('DF saved in %s', utcnow() - start)

# ################################################################################################################################

    def sync_storage(self, _utcnow=utcnow):

        with self.update_lock:

            # For later use
            now_total = _utcnow()

            # Begin with a header to indicate in logs when we start
            logger.info('********************************************************************************* ')
            logger.info('******************************** DF Sync storage ******************************** ')
            logger.info('********************************************************************************* ')

            # Get the existing data from storage
            existing = self._get_data_from_storage()

            # Get data that is currently in RAM
            current = self._get_data_from_ram()

            # Combine data from storage and RAM
            combined = self._combine_data(existing, current)

            # Save the combined result to storage
            self._save_data(combined)

            # Clear our current dataset
            self.in_ram_store[:] = []

            # Log the total processing time
            logger.info('DF total processing time %s', utcnow() - now_total)

# ################################################################################################################################

    def run(self):
        pass

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    fs_data_path = '/tmp/zzz-parquet'
    sync_threshold = 120_000
    sync_interval = 120_000

    container = EventsDatabase(fs_data_path, sync_threshold, sync_interval)
    container.run()

    n = 1000
    total = 0

    for x in range(1000):

        for idx in range(n):
            elem = str(idx)
            event = {

                'id': elem,
                'cid': 'cid.' + elem,
                'timestamp': '2021-05-12T07:07:01.4841' + elem,

                'source_type': 'zato.server' + elem,
                'source_id': 'server1' + elem,

                'object_type': elem,
                'object_id': elem,

                'source_type': elem,
                'source_id': elem,

                'recipient_type': elem,
                'recipient_id': elem,

                'total_time_ms': x,

            }
            container.push(event)
            total += 1
            print('TOTAL', total)

        #container.sync_storage()
        logger.info('-----------------------------------------')


        #os.remove(fs_data_path)

# ################################################################################################################################
# ################################################################################################################################
