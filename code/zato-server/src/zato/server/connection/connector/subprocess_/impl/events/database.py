# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import datetime, timedelta
from typing import Optional as optional

# Humanize
from humanize import intcomma as int_to_comma

# Zato
from zato.common.api import Stats
from zato.common.ext.dataclasses import dataclass
from zato.common.in_ram import InRAMStore

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from logging import Logger
    from pandas import DataFrame

    DataFrame = DataFrame
    Logger = Logger

# ################################################################################################################################
# ################################################################################################################################

utcnow = datetime.utcnow

# ################################################################################################################################
# ################################################################################################################################

class OpCode:
    Push     = 'EventsDBPush'
    Tabulate = 'EventsDBTabulate'

    class Internal:
        SaveData    = 'InternalSaveData'
        SyncState   = 'InternalSyncState'
        GetFromRAM  = 'InternalGetFromRAM'
        ReadParqet  = 'InternalReadParqet'
        CreateNewDF = 'InternalCreateNewDF'
        CombineData = 'InternalCombineData'

_op_int_save_data     = OpCode.Internal.SaveData
_op_int_sync_state    = OpCode.Internal.SyncState
_op_int_get_from_ram  = OpCode.Internal.GetFromRAM
_op_int_read_parqet   = OpCode.Internal.ReadParqet
_op_int_create_new_df = OpCode.Internal.CreateNewDF
_op_int_combine_data  = OpCode.Internal.CombineData

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

class EventsDatabase(InRAMStore):

    def __init__(self, logger, fs_data_path, sync_threshold, sync_interval, max_retention=Stats.MaxRetention):
        super().__init__(sync_threshold, sync_interval)

        # Numpy
        import numpy as np

        # Pandas
        import pandas as pd

        # Our self.logger object
        self.logger = logger

        # Top-level directory to keep persistent data in
        self.fs_data_path = fs_data_path

        # Aggregated usage data is kept here
        self.fs_usage_path = os.path.join(self.fs_data_path, 'usage')

        # Aggregated response times are kept here
        self.fs_response_time_path = os.path.join(self.fs_data_path, 'response-time')

        # In-RAM database of events, saved to disk periodically in background
        self.in_ram_store = [] # type: list[Event]

        # Fow how long to keep statistics in persistent storage
        self.max_retention = max_retention # type: int

        # Configure our opcodes
        self.opcode_to_func[OpCode.Push] = self.push
        self.opcode_to_func[OpCode.Tabulate] = self.get_table

        # Reusable Panda groupers
        self.group_by = {}

        # Each aggregated result will have these columns
        self.agg_by = {
            'item_max':  pd.NamedAgg(column='total_time_ms', aggfunc='max'),
            'item_min':  pd.NamedAgg(column='total_time_ms', aggfunc='min'),
            'item_mean': pd.NamedAgg(column='total_time_ms', aggfunc='mean'),
            'item_total_time':  pd.NamedAgg(column='total_time_ms', aggfunc='sum'),
            'item_total_usage':  pd.NamedAgg(column='total_time_ms', aggfunc=np.count_nonzero),
        }

        # Configure our telemetry opcodes
        self.telemetry[_op_int_save_data]     = 0
        self.telemetry[_op_int_sync_state]    = 0
        self.telemetry[_op_int_get_from_ram]  = 0
        self.telemetry[_op_int_read_parqet]   = 0
        self.telemetry[_op_int_create_new_df] = 0
        self.telemetry[_op_int_combine_data]  = 0

        # Configure Panda objects
        self.set_up_group_by()

# ################################################################################################################################

    def set_up_group_by(self):
        # type: () -> None

        # Pandas
        import pandas as pd

        # This can be added manually
        self.group_by[Stats.TabulateAggr] = pd.Grouper(key=Stats.TabulateAggr)

        # Construct frequency aggregation configuration ..
        time_freq_aggr_group_by = [
            # This is used by default
            Stats.DefaultAggrTimeFreq,
        ]

        # .. and add groupers.
        for time_freq in time_freq_aggr_group_by:
            group_by = self.get_group_by(time_freq)
            self.group_by[time_freq] = group_by

# ################################################################################################################################

    def get_group_by(self, time_freq):
        # type: (str) -> list

        # Pandas
        import pandas as pd

        return [
            pd.Grouper(key='timestamp', freq=time_freq),
            pd.Grouper(key='object_id'),
        ]

# ################################################################################################################################

    def push(self, data):
        # type: (dict) -> None
        self.in_ram_store.append(data)

# ################################################################################################################################

    def load_data_from_storage(self):
        """ Reads existing data from persistent storage and returns it as a DataFrame.
        """

        # Pandas
        import pandas as pd

        # Let's check if we already have anything in storage ..
        if os.path.exists(self.fs_data_path):

            #  Let the users know what we are doing ..
            self.logger.info('Loading DF data from %s', self.fs_data_path)

            # .. load existing data from storage ..
            start = utcnow()
            existing = pd.read_parquet(self.fs_data_path) # type: pd.DataFrame

            # .. log the time it took to load the data ..
            self.logger.info('DF data read in %s; len_existing=%s', utcnow() - start, int_to_comma(len(existing)))

            # .. update counters ..
            self.telemetry[_op_int_read_parqet] += 1

        else:

            # .. create a new DF instead ..
            existing = pd.DataFrame()

            # .. update counters ..
            self.telemetry[_op_int_create_new_df] += 1

        # .. return the result, no matter where it came from.
        return existing

# ################################################################################################################################

    def get_data_from_ram(self):
        """ Turns data currently stored in RAM into a DataFrame.
        """
        # type: () -> None

        # Pandas
        import pandas as pd

        #  Let the users know what we are doing ..
        self.logger.info('Building DF out of len_current=%s', int_to_comma(len(self.in_ram_store)))

        # .. convert the data collected so far into a DataFrame ..
        start = utcnow()
        current = pd.DataFrame(self.in_ram_store)

        # .. log the time it took build the DataFrame ..
        self.logger.info('DF built in %s', utcnow() - start)

        # .. update counters ..
        self.telemetry[_op_int_get_from_ram] += 1

        return current

# ################################################################################################################################

    def aggregate(self, data, time_freq=Stats.DefaultAggrTimeFreq):

        # Pandas
        import pandas as pd

        # Check if we have had this particular frequency before ..
        group_by = self.group_by.get(time_freq)

        # .. if not, set it up now.
        if not group_by:
            self.group_by[time_freq] = self.get_group_by(time_freq)
            group_by = self.group_by[time_freq]

        data = data.set_index(pd.DatetimeIndex(data['timestamp']))
        data.index.name = 'idx_timestamp'

        aggregated = data.\
            groupby(group_by).\
            agg(**self.agg_by)

        return aggregated

# ################################################################################################################################

    def combine_data(self, existing, current):
        """ Combines on disk and in-RAM data.
        """
        # type: (DataFrame, DataFrame) -> DataFrame

        # Pandas
        import pandas as pd

        # Let the user know what we are doing ..
        self.logger.info('Combining existing and current data')

        # .. combine the existing and current data ..
        start = utcnow()
        combined = pd.concat([existing, current])

        # .. log the time it took to combine the DataFrames..
        self.logger.info('DF combined in %s', utcnow() - start)

        # .. update counters ..
        self.telemetry[_op_int_combine_data] += 1

        return combined

# ################################################################################################################################

    def trim(self, data, utcnow=utcnow, timedelta=timedelta):

        if len(data):

            # Check how many of the past events to leave, i.e. events older than this will be discarded
            max_retained = utcnow() - timedelta(milliseconds=self.max_retention)
            max_retained = max_retained.isoformat()

            # .. construct a new dataframe, containing only the events that are younger than max_retained ..
            data = data[data['timestamp'] > max_retained]

        # .. and return it to our caller.
        return data

# ################################################################################################################################

    def save_data(self, data):
        # type: (DataFrame) -> None

        # Let the user know what we are doing ..
        self.logger.info('Saving DF to %s', self.fs_data_path)

        # .. save the DF to persistent storage ..
        start = utcnow()
        data.to_parquet(self.fs_data_path)

        # .. log the time it took to save to storage ..
        self.logger.info('DF saved in %s', utcnow() - start)

        # .. update counters ..
        self.telemetry[_op_int_save_data] += 1

# ################################################################################################################################

    def _sync_state(self, _utcnow=utcnow):

        # For later use
        now_total = _utcnow()

        # Begin with a header to indicate in logs when we start
        self.logger.info('********************************************************************************* ')
        self.logger.info('*********************** DataFrame (DF) Sync storage ***************************** ')
        self.logger.info('********************************************************************************* ')

        # Get the existing data from storage
        existing = self.load_data_from_storage()

        # Get data that is currently in RAM
        current = self.get_data_from_ram()

        # Combine data from storage and RAM
        combined = self.combine_data(existing, current)

        # Trim the data to the retention threshold
        trimmed = self.trim(combined)

        # Save the combined result to storage
        self.save_data(trimmed)

        # Clear our current dataset
        self.in_ram_store[:] = []

        # Log the total processing time
        self.logger.info('DF total processing time %s', utcnow() - now_total)

        # update counters
        self.telemetry[_op_int_sync_state] += 1

# ################################################################################################################################

    def sync_state(self):
        with self.update_lock:
            self._sync_state()

# ################################################################################################################################

    def get_table(self):

        # Prepare configuration ..
        group_by = self.group_by[Stats.TabulateAggr]

        with self.update_lock:

            # .. make sure we have access to the latest data ..
            self._sync_state()

            # .. read our input data from persistent storage ..
            data = self.load_data_from_storage()

        # .. tabulate all the statistics found ..
        tabulated = data.\
            groupby(group_by).\
            agg(**self.agg_by)

        # .. convert rows to columns which is what our callers expect ..
        tabulated = tabulated.transpose()

        # .. finally, return the result.
        return tabulated

# ################################################################################################################################

    def run(self):
        pass

# ################################################################################################################################
# ################################################################################################################################
