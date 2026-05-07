# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from collections import deque
from enum import Enum

# ################################################################################################################################
# ################################################################################################################################

class CircuitState(str, Enum):
    Closed    = 'closed'
    Open      = 'open'
    Half_Open = 'half-open'

# ################################################################################################################################
# ################################################################################################################################

_Default_Failure_Threshold_Percent = 50
_Default_Window_Seconds            = 60.0
_Default_Reset_Seconds             = 60.0

# ################################################################################################################################
# ################################################################################################################################

class CircuitBreaker:
    """ A circuit breaker that tracks success/failure outcomes over a sliding time window.
    Transitions between closed, open, and half-open states based on the failure rate.
    """

    def __init__(
        self,
        failure_threshold_percent:'int' = _Default_Failure_Threshold_Percent,
        window_seconds:'float' = _Default_Window_Seconds,
        reset_seconds:'float' = _Default_Reset_Seconds,
        ) -> 'None':

        self.failure_threshold_percent = failure_threshold_percent
        self.window_seconds = window_seconds
        self.reset_seconds  = reset_seconds

        self.state = CircuitState.Closed

        # Timestamp (monotonic) when the circuit was last opened
        self._opened_at = 0.0

        # Deque of (timestamp, is_failure) tuples within the sliding window
        self._outcomes:'deque[tuple[float, bool]]' = deque()

# ################################################################################################################################

    def record_success(self) -> 'None':
        """ Records a successful operation.
        """

        now = time.monotonic()

        if self.state == CircuitState.Half_Open:
            # Successful probe closes the circuit
            self.state = CircuitState.Closed
            self._outcomes.clear()
            return

        self._evict_old_entries(now)
        self._outcomes.append((now, False))

# ################################################################################################################################

    def record_failure(self) -> 'None':
        """ Records a failed operation and transitions to open if the threshold is exceeded.
        """

        now = time.monotonic()

        if self.state == CircuitState.Half_Open:
            # Failed probe re-opens the circuit
            self.state = CircuitState.Closed
            self._outcomes.clear()
            self._transition_to_open(now)
            return

        self._evict_old_entries(now)
        self._outcomes.append((now, True))

        # Check if we should open the circuit
        self._check_threshold(now)

# ################################################################################################################################

    def can_execute(self) -> 'bool':
        """ Returns True if an operation should be attempted.
        In closed state, always True.
        In open state, checks if the reset time has elapsed to transition to half-open.
        In half-open state, allows exactly one probe.
        """

        now = time.monotonic()

        if self.state == CircuitState.Closed:
            return True

        if self.state == CircuitState.Open:

            # Check if the reset period has elapsed ..
            elapsed = now - self._opened_at

            if elapsed >= self.reset_seconds:
                # .. transition to half-open for a single probe.
                self.state = CircuitState.Half_Open
                return True

            return False

        # Half-open: allow one probe
        if self.state == CircuitState.Half_Open:
            return True

        return False

# ################################################################################################################################

    def _transition_to_open(self, now:'float') -> 'None':
        """ Moves the circuit to the open state.
        """
        self.state = CircuitState.Open
        self._opened_at = now

# ################################################################################################################################

    def _evict_old_entries(self, now:'float') -> 'None':
        """ Removes entries that have fallen outside the sliding window.
        """

        cutoff = now - self.window_seconds

        while self._outcomes:
            entry_time = self._outcomes[0][0]

            if entry_time < cutoff:
                self._outcomes.popleft()
            else:
                break

# ################################################################################################################################

    def _check_threshold(self, now:'float') -> 'None':
        """ Checks the failure rate and opens the circuit if it exceeds the threshold.
        """

        total_count = len(self._outcomes)

        if total_count == 0:
            return

        failure_count = 0

        for _timestamp, is_failure in self._outcomes:
            if is_failure:
                failure_count += 1

        failure_percent = (failure_count * 100) // total_count

        if failure_percent >= self.failure_threshold_percent:
            self._transition_to_open(now)

# ################################################################################################################################
# ################################################################################################################################
