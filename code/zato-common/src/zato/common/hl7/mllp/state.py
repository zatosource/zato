# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Per-channel live state - the counters the MLLP server keeps in-process
# and the channel dashboard reads. This is the live side of the split:
# counters are never polled from the audit database, history is.

from __future__ import annotations

# stdlib
from collections import deque
from time import time

# Zato
from zato.common.monitoring.health import EndpointMetrics
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import floatnone, stranydict
    floatnone = floatnone
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# How many recent outcomes feed the rolling error rate
_window_max_entries = 500

# How far back the rolling error rate looks, in seconds
_window_seconds = 300.0

# ################################################################################################################################
# ################################################################################################################################

class ChannelState:
    """ The live state of one channel - message counters, the listener's condition
    and a rolling window of recent outcomes the error rate is computed over.
    """

    def __init__(self, name:'str') -> 'None':

        self.name = name

        # Lifetime counters
        self.received = 0
        self.acked = 0
        self.nacked = 0
        self.errored = 0

        # Consecutive negative acknowledgments - a streak signals a degraded feed
        # even when the lifetime error rate still looks healthy
        self.nack_streak = 0

        # When the last message arrived - what dead-feed detection watches
        self.last_message_time:'floatnone' = None
        self.last_message_time_iso = ''

        # The listener's condition
        self.is_listening = False
        self.listening_since_iso = ''

        # Recent outcomes as (timestamp, is_error) pairs, bounded so memory never grows
        self._window:'deque' = deque(maxlen=_window_max_entries)

# ################################################################################################################################

    def on_listener_up(self) -> 'None':
        self.is_listening = True
        self.listening_since_iso = utcnow().isoformat()

# ################################################################################################################################

    def on_listener_down(self) -> 'None':
        self.is_listening = False

# ################################################################################################################################

    def on_message_received(self) -> 'None':
        self.received += 1
        self.last_message_time = time()
        self.last_message_time_iso = utcnow().isoformat()

# ################################################################################################################################

    def on_ack_sent(self) -> 'None':
        self.acked += 1

        # A positive acknowledgment ends any streak of negative ones
        self.nack_streak = 0

        self._window.append((time(), False))

# ################################################################################################################################

    def on_nack_sent(self) -> 'None':
        self.nacked += 1
        self.nack_streak += 1
        self._window.append((time(), True))

# ################################################################################################################################

    def on_error(self) -> 'None':
        """ A failure below the acknowledgment level - a broken frame, a lost connection -
        which produced no ACK at all.
        """
        self.errored += 1
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

        if self.last_message_time is None:
            return 0.0

        out = now - self.last_message_time
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
            'last_message_time_iso': self.last_message_time_iso,
            'silence_seconds': self.get_silence_seconds(now),
            'error_rate': self.get_error_rate(now),
        }

        return out

# ################################################################################################################################
# ################################################################################################################################
