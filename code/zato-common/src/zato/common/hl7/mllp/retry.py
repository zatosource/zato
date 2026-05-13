# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import random
import time

# Zato
from zato.common.hl7.mllp.ack import AckResult

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_Default_Max_Retries        = 5
_Default_Backoff_Base       = 1.0
_Default_Backoff_Multiplier = 2.0
_Default_Backoff_Cap        = 300.0
_Default_Jitter_Percent     = 10

# ################################################################################################################################
# ################################################################################################################################

class RetryResult:
    """ Outcome of a send-with-retry attempt.
    """

    def __init__(self) -> 'None':
        self.is_sent:     'bool' = False
        self.ack_result:  'AckResult | None' = None
        self.sent_to_dlq: 'bool' = False
        self.retry_count: 'int'  = 0
        self.last_error:  'str'  = ''

# ################################################################################################################################
# ################################################################################################################################

class RetryEngine:
    """ Wraps a send callable with retry logic, exponential backoff, and DLQ routing.
    The send callable receives (payload_bytes) and returns an AckResult.
    The dlq callable receives (payload_bytes, error_text, retry_count) for dead-letter handling.
    """

    def __init__(
        self,
        send_func:'callable_',
        dlq_func:'callable_',
        max_retries:'int'      = _Default_Max_Retries,
        backoff_base:'float'   = _Default_Backoff_Base,
        backoff_multiplier:'float' = _Default_Backoff_Multiplier,
        backoff_cap:'float'    = _Default_Backoff_Cap,
        jitter_percent:'int'   = _Default_Jitter_Percent,
        sleep_func:'callable_' = time.sleep,
        ) -> 'None':

        self.send_func  = send_func
        self.dlq_func   = dlq_func
        self.max_retries        = max_retries
        self.backoff_base       = backoff_base
        self.backoff_multiplier = backoff_multiplier
        self.backoff_cap        = backoff_cap
        self.jitter_percent     = jitter_percent
        self.sleep_func         = sleep_func

# ################################################################################################################################

    def send_with_retry(self, payload:'bytes') -> 'RetryResult':
        """ Sends the payload through the send callable, retrying on retryable outcomes.
        """

        # Our response to produce
        out = RetryResult()

        attempt = 0

        while True:

            # Try sending the message ..
            try:
                ack_result = self.send_func(payload)
            except Exception as exception:

                # .. treat exceptions as retryable (network errors, timeouts) ..
                ack_result = AckResult()
                ack_result.should_retry = True
                ack_result.error_text = str(exception)

            out.ack_result = ack_result
            out.retry_count = attempt

            # .. if accepted, we are done ..
            if ack_result.is_accepted:
                out.is_sent = True
                return out

            # .. if the remote says do not retry (AE/CE), route to DLQ immediately ..
            if not ack_result.should_retry:
                self._route_to_dlq(payload, ack_result.error_text, attempt, out)
                return out

            # .. we should retry, but check if we have retries left ..
            attempt += 1

            if attempt > self.max_retries:
                self._route_to_dlq(payload, ack_result.error_text, attempt, out)
                return out

            # .. wait with exponential backoff before the next attempt.
            delay = self._compute_delay(attempt)
            logger.info('MLLP retry attempt %d/%d, sleeping %.2fs', attempt, self.max_retries, delay)
            self.sleep_func(delay)

# ################################################################################################################################

    def _compute_delay(self, attempt:'int') -> 'float':
        """ Computes the backoff delay for the given attempt number,
        capped at backoff_cap with random jitter applied.
        """

        # Base * multiplier^(attempt-1), capped ..
        raw_delay = self.backoff_base * (self.backoff_multiplier ** (attempt - 1))

        capped_delay = min(raw_delay, self.backoff_cap)

        # .. apply jitter ..
        jitter_fraction = self.jitter_percent / 100.0
        jitter_range = capped_delay * jitter_fraction
        jitter = random.uniform(-jitter_range, jitter_range)

        out = max(0.0, capped_delay + jitter)
        return out

# ################################################################################################################################

    def _route_to_dlq(self, payload:'bytes', error_text:'str', retry_count:'int', result:'RetryResult') -> 'None':
        """ Sends the failed message to the dead-letter queue.
        """
        self.dlq_func(payload, error_text, retry_count)
        result.sent_to_dlq = True

# ################################################################################################################################
# ################################################################################################################################
