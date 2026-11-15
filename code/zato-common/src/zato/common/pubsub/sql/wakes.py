# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The wake-ups of subscribers across the workers of one server. A publication committed through one worker increments
# the wake counter of each of its subscription keys in the shared region and makes the descriptor of every worker
# readable. Each worker then reads its descriptor, compares the counters of its subscription keys with the values
# it acted upon last and sets the local events of the keys whose counters changed, which wakes the push delivery loop
# of the owning worker and the blocking pulls served by any worker.

# gevent
from gevent import spawn
from gevent.socket import wait_read

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent import Greenlet
    from zato.common.typing_ import callable_, dict_, strlist
    from zato_ipc_core.zato_ipc_core import SharedRegion

    callable_ = callable_
    Greenlet = Greenlet
    SharedRegion = SharedRegion
    strlist = strlist

    strintdict = dict_[str, int]

# ################################################################################################################################
# ################################################################################################################################

class CrossWorkerWakes:
    """ Sends the wake-ups of committed publications to every worker and receives those of the other workers.
    """

    def __init__(self, region:'SharedRegion', slot:'int', on_changed:'callable_') -> 'None':
        self.region = region
        self.slot = slot

        # Called with the subscription keys whose counters changed
        self.on_changed = on_changed

        # The value of the counter of each subscription key of this worker that the worker acted upon last
        self.observed:'strintdict' = {}

# ################################################################################################################################

    def observe(self, sub_key:'str') -> 'None':
        """ Starts comparing the counter of a subscription key, from its current value. A caller observes a key
        before it reads the queue of the key, so a publication committed after that read changes the counter.
        """
        self.observed[sub_key] = self.region.wake_value(sub_key)

# ################################################################################################################################

    def publish(self, sub_keys:'strlist') -> 'None':
        """ Wakes every worker for the subscription keys of a committed publication.
        """
        for sub_key in sub_keys:
            self.region.wake_increment(sub_key)

        for slot in range(self.region.slot_count):
            self.region.wake_slot(slot)

# ################################################################################################################################

    def receive(self) -> 'strlist':
        """ Reads the descriptor of this worker and returns the subscription keys whose counters changed.
        """
        # The descriptor is read before the counters are compared, because a read after the comparison
        # would discard the wake-up of a publication committed between the two ..
        _ = self.region.drain_slot(self.slot)

        # .. and each changed counter is acted upon once.
        out:'strlist' = []

        for sub_key, observed in self.observed.items():
            value = self.region.wake_value(sub_key)

            if value != observed:
                self.observed[sub_key] = value
                out.append(sub_key)

        return out

# ################################################################################################################################

    def run(self) -> 'None':
        """ Wakes the subscribers of this worker whenever its descriptor becomes readable.
        """
        wake_fd = self.region.wake_fd(self.slot)

        while True:
            wait_read(wake_fd)
            sub_keys = self.receive()

            if sub_keys:
                self.on_changed(sub_keys)

# ################################################################################################################################

    def start(self) -> 'Greenlet':
        out = spawn(self.run)
        return out

# ################################################################################################################################
# ################################################################################################################################
