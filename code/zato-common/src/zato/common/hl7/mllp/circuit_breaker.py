# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from collections import deque
from enum import Enum

# Zato
from zato.common.hl7.mllp.region import get_mllp_binding, get_now_us, seconds_to_us
from zato_ipc_core.zato_ipc_core import BREAKER_CLOSED, BREAKER_OPEN

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.hl7.mllp.region import MLLPBinding

    MLLPBinding = MLLPBinding

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

class SendingStopped(Exception):
    """ Raised by a send that the circuit breaker of its connection did not let through.
    """

# ################################################################################################################################
# ################################################################################################################################

class CircuitBreaker:
    """ A circuit breaker that tracks success/failure outcomes over a sliding time window.
    Transitions between closed, open, and half-open states based on the failure rate.
    In a worker that the arbiter bound to the shared region, the state and the opening time are kept in the region
    under the key of the outgoing connection, so the breaker opened by one worker stops the sends of every worker,
    and one worker of all sends the trial message. Each worker keeps the outcomes of its own sends.
    """

    def __init__(
        self,
        failure_threshold_percent:'int' = _Default_Failure_Threshold_Percent,
        window_seconds:'float' = _Default_Window_Seconds,
        reset_seconds:'float' = _Default_Reset_Seconds,
        key:'str' = '',
        ) -> 'None':

        self.failure_threshold_percent = failure_threshold_percent
        self.window_seconds = window_seconds
        self.reset_seconds  = reset_seconds
        self.key = key

        self.state = CircuitState.Closed

        # Whether this worker sends the trial message of the breaker in the shared region
        self.has_trial = False

        # Whether this worker found the breaker in the shared region other than closed since it last found it closed
        self.has_seen_open = False

        # Timestamp (monotonic) when the circuit was last opened
        self._opened_at = 0.0

        # Deque of (timestamp, is_failure) tuples within the sliding window
        self._outcomes:'deque[tuple[float, bool]]' = deque()

# ################################################################################################################################

    def record_success(self) -> 'None':
        """ Records a successful operation.
        """
        binding = get_mllp_binding()

        # The successful trial message of this worker closes the breaker of every worker
        if binding:
            if self.has_trial:
                self._end_trial(binding, True)
                return

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
        binding = get_mllp_binding()

        # The failed trial message of this worker opens the breaker of every worker for another reset period
        if binding:
            if self.has_trial:
                self._end_trial(binding, False)
                return

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
        In open state, checks if the reset time has elapsed to transition to half-open, which lets the one probe through.
        In half-open state, the probe is on the wire and nothing else is attempted until its outcome is recorded.
        """

        binding = get_mllp_binding()

        if binding:
            out = self._can_execute_in_region(binding)
            return out

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

        # Half-open: the one probe is on the wire, and its outcome decides what comes next
        if self.state == CircuitState.Half_Open:
            return False

        return False

# ################################################################################################################################

    def _transition_to_open(self, now:'float') -> 'None':
        """ Moves the circuit to the open state.
        """
        binding = get_mllp_binding()

        # The breaker of every worker opens, unless another worker opened it first
        if binding:
            _ = binding.region.breaker_open(self.key, get_now_us())
            self.has_seen_open = True
            return

        self.state = CircuitState.Open
        self._opened_at = now

# ################################################################################################################################

    def _can_execute_in_region(self, binding:'MLLPBinding') -> 'bool':
        """ Returns True if an operation should be attempted, according to the breaker in the shared region.
        """
        state, _opened_at_us = binding.region.breaker_state(self.key)

        # A breaker closed by the trial message of any worker starts the window of this worker anew,
        # as a successful trial in one process does
        if state == BREAKER_CLOSED:
            if self.has_seen_open:
                self.has_seen_open = False
                self._outcomes.clear()
            return True

        self.has_seen_open = True

        # Of the workers that find the reset period over, one moves the breaker to half-open and sends the trial message
        if state == BREAKER_OPEN:
            reset_us = seconds_to_us(self.reset_seconds)
            self.has_trial = binding.region.breaker_begin_trial(self.key, get_now_us(), reset_us)
            return self.has_trial

        # The trial message of another worker is on the wire
        return False

# ################################################################################################################################

    def _end_trial(self, binding:'MLLPBinding', is_success:'bool') -> 'None':
        """ Concludes the trial message that this worker sent.
        """
        _ = binding.region.breaker_end_trial(self.key, is_success, get_now_us())

        self.has_trial = False
        self._outcomes.clear()

# ################################################################################################################################

    def _evict_old_entries(self, now:'float') -> 'None':
        """ Removes entries that have fallen outside the sliding window.
        """

        cutoff = now - self.window_seconds

        while self._outcomes:
            entry_time = self._outcomes[0][0]

            if entry_time < cutoff:
                _ = self._outcomes.popleft()
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
