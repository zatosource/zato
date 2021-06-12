# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime

# ################################################################################################################################
# ################################################################################################################################

utcnow = datetime.utcnow

# ################################################################################################################################
# ################################################################################################################################

class InRAMStore:
    """ Base class for stores keeping data in RAM, optionally synchronising it to persistent storage.
    """
    def __init__(self, sync_threshold, sync_interval):
        # type: (int, int) -> None

        # Sync to storage once in that many events ..
        self.sync_threshold = sync_threshold

        # .. or once in that many milliseconds.
        self.sync_interval = sync_interval

        # Total events received since startup
        self.total_events = 0

        # How many events we have received since the last synchronisation with persistent storage
        self.num_events_since_sync = 0

        # Reset each time we synchronise in-RAM state with the persistent storage
        self.last_sync_time = utcnow()

        # Maps action opcodes to actual methods so that the latter do not have to be looked up in runtime
        self.opcode_to_func = {}

        # An update lock used while modifying the in-RAM database
        self.update_lock = RLock()

# ################################################################################################################################

    def should_sync(self):
        # type: () -> bool
        sync_by_threshold = self.num_events_since_sync % self.sync_threshold == 0
        sync_by_time = (utcnow() - self.last_sync_time).total_seconds() * 1000 >= self.sync_interval

        return sync_by_threshold or sync_by_time

# ################################################################################################################################

    def sync_storage(self):
        raise NotImplementedError('InRAMStore.sync_storage')

# ################################################################################################################################

    def modify_state(self, opcode, data):
        # type: (str, object) -> None
        with self.update_lock:

            # Maps the incoming upcode to an actual function to handle data ..
            func = self.opcode_to_func[opcode]

            # .. store in RAM ..
            func(data)

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
# ################################################################################################################################
