# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The gate in the config process between the changes to configuration and the workers that load configuration.
# A change runs only while no worker loads, and a worker begins to load only between two changes, so every worker
# loads either all of a change or none of it, and the events of a change it loaded none of reach it after its load.

# gevent
from gevent.event import Event
from gevent.lock import RLock

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_

    any_ = any_
    callable_ = callable_

# ################################################################################################################################
# ################################################################################################################################

class ChangeGate:
    """ Lets a change to configuration run only while no worker loads configuration.
    """
    def __init__(self, send_mark:'callable_') -> 'None':

        # Sends to a worker the mark from which it loads configuration
        self.send_mark = send_mark

        # Held by a change for its duration and by the sending of a mark
        self.lock = RLock()

        # Set while no worker loads configuration
        self.idle = Event()
        self.idle.set()

        # Workers that load configuration, slot to the correlation ID of their load
        self.loading:'dict[int, str]' = {}

        # Workers that asked to load configuration and have no mark yet, slot to the correlation ID of their request
        self.pending:'dict[int, str]' = {}

# ################################################################################################################################

    def _update_idle(self) -> 'None':
        if self.loading:
            self.idle.clear()
        else:
            self.idle.set()

# ################################################################################################################################

    def run(self, func:'callable_', *args:'any_') -> 'any_':
        """ Runs a change to configuration once no worker loads configuration.
        """
        with self.lock:
            _ = self.idle.wait()
            return func(*args)

# ################################################################################################################################

    def request_load(self, slot:'int', cid:'str') -> 'None':
        """ Sends a worker its mark as soon as no change to configuration runs.
        """
        self.pending[slot] = cid

        with self.lock:

            # The worker exited, or asked again, while a change ran, so this request has no worker to answer.
            if self.pending.get(slot) != cid:
                return

            del self.pending[slot]
            self.loading[slot] = cid
            self._update_idle()

            self.send_mark(slot, cid)

# ################################################################################################################################

    def on_load_done(self, slot:'int', cid:'str') -> 'None':
        """ Records that a worker loaded its configuration.
        """
        # A load that the worker no longer reports for, after a newer request of its own, changes nothing.
        if self.loading.get(slot) == cid:
            del self.loading[slot]
            self._update_idle()

# ################################################################################################################################

    def on_worker_gone(self, slot:'int') -> 'None':
        """ Forgets a worker that exited.
        """
        _ = self.pending.pop(slot, None)
        _ = self.loading.pop(slot, None)
        self._update_idle()

# ################################################################################################################################

    def set_loading(self, loading:'dict[int, str]') -> 'None':
        """ Takes over the workers that loaded configuration when the previous config process exited.
        """
        self.loading.update(loading)
        self._update_idle()

# ################################################################################################################################
# ################################################################################################################################
