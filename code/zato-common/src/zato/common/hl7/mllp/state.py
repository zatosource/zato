# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Per-channel live state - the counters the MLLP server keeps and the channel dashboard reads.
# This is the live side of the split: counters are never polled from the audit database, history is.
# With an arbiter, the counters and the time of the last message are cells of the region of the server,
# one per worker, and a reader combines the cells of all the workers.

from __future__ import annotations

# stdlib
from collections import deque
from datetime import datetime, timezone
from logging import getLogger
from time import time

# Zato
from zato.common.hl7.mllp.region import get_mllp_binding, ModuleCtx as RegionCtx
from zato.common.monitoring.health import EndpointMetrics
from zato.common.util.api import utcnow

# Zato - Rust
from zato_ipc_core.zato_ipc_core import SharedRegionFull

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.hl7.mllp.region import MLLPBinding
    from zato.common.typing_ import floatnone, strintdict, stranydict
    MLLPBinding = MLLPBinding
    floatnone = floatnone
    strintdict = strintdict
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How many recent outcomes feed the rolling error rate
_window_max_entries = 500

# How far back the rolling error rate looks, in seconds
_window_seconds = 300.0

# The lifetime counters of a channel
Counter_Received = 'received'
Counter_Acked = 'acked'
Counter_Nacked = 'nacked'
Counter_Errored = 'errored'

Counter_Names = (Counter_Received, Counter_Acked, Counter_Nacked, Counter_Errored)

# The name of the value that holds the time of the last message within the key of its series
Last_Message_Time_Name = 'last_message_time'

# ################################################################################################################################
# ################################################################################################################################

def _get_series_key(channel_name:'str', value_name:'str') -> 'str':
    out = RegionCtx.Channel_Key_Separator.join((RegionCtx.Channel_Key_Prefix, channel_name, value_name))
    return out

# ################################################################################################################################
# ################################################################################################################################

class _LocalValues:
    """ The counters and the time of the last message of a channel, in the memory of the process.
    """

    def __init__(self) -> 'None':
        self._counts:'strintdict' = dict.fromkeys(Counter_Names, 0)
        self._last_message_time:'floatnone' = None

    def add(self, counter_name:'str') -> 'None':
        self._counts[counter_name] += 1

    def get_total(self, counter_name:'str') -> 'int':
        out = self._counts[counter_name]
        return out

    def set_last_message_time(self, value:'float') -> 'None':
        self._last_message_time = value

    def get_last_message_time(self) -> 'floatnone':
        out = self._last_message_time
        return out

# ################################################################################################################################
# ################################################################################################################################

class _RegionValues:
    """ The counters and the time of the last message of a channel, in the series table of the region of the server.
    Each worker writes the cells of its own slot, and a reader sums the counters and takes the latest time over all the slots.
    """

    def __init__(self, binding:'MLLPBinding', channel_name:'str') -> 'None':

        self._region = binding.region
        self._slot = binding.slot
        self._counter_indexes:'strintdict' = {}

        for counter_name in Counter_Names:
            key = _get_series_key(channel_name, counter_name)
            self._counter_indexes[counter_name] = self._region.series_register(RegionCtx.Kind_Channel_Counter, key)

        time_key = _get_series_key(channel_name, Last_Message_Time_Name)
        self._time_index = self._region.series_register(RegionCtx.Kind_Channel_Time, time_key)

    def add(self, counter_name:'str') -> 'None':
        index = self._counter_indexes[counter_name]
        self._region.series_add(self._slot, index, 1)

    def get_total(self, counter_name:'str') -> 'int':
        index = self._counter_indexes[counter_name]
        out = self._region.series_sum(index)
        return out

    def set_last_message_time(self, value:'float') -> 'None':
        self._region.series_set_float(self._slot, self._time_index, value)

    def get_last_message_time(self) -> 'floatnone':
        out = self._region.series_max_float(self._time_index)

        # A cell that no worker has written holds zero, which no arrival produces
        if not out:
            return None

        return out

# ################################################################################################################################
# ################################################################################################################################

def _new_values(channel_name:'str') -> '_LocalValues | _RegionValues':

    binding = get_mllp_binding()

    # A process that no arbiter bound keeps the values of its channels in its own memory
    if binding is None:
        return _LocalValues()

    try:
        out = _RegionValues(binding, channel_name)

    # With the series table full, the channel counts in the memory of this worker alone
    except SharedRegionFull:
        logger.error('Channel `%s` counts in the memory of this worker alone, the series table is full', channel_name)
        return _LocalValues()

    return out

# ################################################################################################################################
# ################################################################################################################################

class ChannelState:
    """ The live state of one channel - message counters, the listener's condition
    and a rolling window of recent outcomes the error rate is computed over.
    """

    def __init__(self, name:'str') -> 'None':

        self.name = name

        # Lifetime counters and when the last message arrived - what dead-feed detection watches
        self._values = _new_values(name)

        # Consecutive negative acknowledgments - a streak signals a degraded feed
        # even when the lifetime error rate still looks healthy
        self.nack_streak = 0

        # The listener's condition
        self.is_listening = False
        self.listening_since_iso = ''

        # Recent outcomes as (timestamp, is_error) pairs, bounded so memory never grows
        self._window:'deque' = deque(maxlen=_window_max_entries)

# ################################################################################################################################

    @property
    def received(self) -> 'int':
        out = self._values.get_total(Counter_Received)
        return out

    @property
    def acked(self) -> 'int':
        out = self._values.get_total(Counter_Acked)
        return out

    @property
    def nacked(self) -> 'int':
        out = self._values.get_total(Counter_Nacked)
        return out

    @property
    def errored(self) -> 'int':
        out = self._values.get_total(Counter_Errored)
        return out

    @property
    def last_message_time(self) -> 'floatnone':
        """ The time of the last message is kept as the number the arrival already produced, and the text of it
        is written when read, because every message sets it and only a dashboard poll ever looks at it.
        """
        out = self._values.get_last_message_time()
        return out

# ################################################################################################################################

    def on_listener_up(self) -> 'None':
        self.is_listening = True
        self.listening_since_iso = utcnow().isoformat()

# ################################################################################################################################

    def on_listener_down(self) -> 'None':
        self.is_listening = False

# ################################################################################################################################

    def on_message_received(self) -> 'None':
        self._values.add(Counter_Received)
        self._values.set_last_message_time(time())

# ################################################################################################################################

    def on_ack_sent(self) -> 'None':
        self._values.add(Counter_Acked)

        # A positive acknowledgment ends any streak of negative ones
        self.nack_streak = 0

        self._window.append((time(), False))

# ################################################################################################################################

    def on_nack_sent(self) -> 'None':
        self._values.add(Counter_Nacked)
        self.nack_streak += 1
        self._window.append((time(), True))

# ################################################################################################################################

    def on_error(self) -> 'None':
        """ A failure below the acknowledgment level - a broken frame, a lost connection -
        which produced no ACK at all.
        """
        self._values.add(Counter_Errored)
        self._window.append((time(), True))

# ################################################################################################################################

    def get_error_rate(self, now:'floatnone'=None) -> 'float':
        """ Returns the share of failures among the outcomes of the last few minutes -
        0.0 when the window is empty.
        """
        if now is None:
            now = time()

        cutoff = now - _window_seconds

        total = 0
        errors = 0

        for timestamp, is_error in self._window:

            # Older entries fell out of the window
            if timestamp < cutoff:
                continue

            total += 1
            if is_error:
                errors += 1

        if not total:
            return 0.0

        out = errors / total
        return out

# ################################################################################################################################

    def get_silence_seconds(self, now:'floatnone'=None) -> 'float':
        """ Returns how long ago the last message arrived - 0.0 for a channel
        that has not received anything yet, because a feed that never started
        is a configuration matter, not a dead feed.
        """
        if now is None:
            now = time()

        last_message_time = self.last_message_time

        if last_message_time is None:
            return 0.0

        out = now - last_message_time
        return out

# ################################################################################################################################

    def get_last_message_time_iso(self) -> 'str':
        """ Returns when the last message arrived, as text, or an empty string for a channel
        that has not received anything yet.
        """
        last_message_time = self.last_message_time

        if last_message_time is None:
            return ''

        out = datetime.fromtimestamp(last_message_time, timezone.utc).isoformat()
        return out

# ################################################################################################################################

    def get_metrics(self, now:'floatnone'=None) -> 'EndpointMetrics':
        """ Returns this channel's state in the endpoint-generic shape health derivation runs over.
        """
        out = EndpointMetrics()

        out.is_connected = self.is_listening
        out.error_rate = self.get_error_rate(now)
        out.silence_seconds = self.get_silence_seconds(now)
        out.nack_streak = self.nack_streak

        return out

# ################################################################################################################################

    def get_state(self, now:'floatnone'=None) -> 'stranydict':
        """ Returns the full state contract of this channel - what the get-current-state
        service aggregates across servers and the dashboard renders.
        """
        out = {
            'name': self.name,
            'is_listening': self.is_listening,
            'listening_since_iso': self.listening_since_iso,
            'received': self.received,
            'acked': self.acked,
            'nacked': self.nacked,
            'errored': self.errored,
            'nack_streak': self.nack_streak,
            'last_message_time_iso': self.get_last_message_time_iso(),
            'silence_seconds': self.get_silence_seconds(now),
            'error_rate': self.get_error_rate(now),
        }

        return out

# ################################################################################################################################
# ################################################################################################################################
