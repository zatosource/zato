# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from time import monotonic, sleep

# SQLAlchemy
from sqlalchemy.exc import DBAPIError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_, floatnone

    # Dummy assignments to satisfy type checkers
    any_ = any_
    callable_ = callable_
    floatnone = floatnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How long the first pause before a database operation is run again lasts, and how long the longest one lasts,
# in seconds - each pause doubles the previous one.
_retry_initial_seconds = 1
_retry_max_seconds = 30

# ################################################################################################################################
# ################################################################################################################################

def call_until_available(component:'str', func:'callable_', *args:'any_') -> 'any_':
    """ Runs a database operation and runs it again after each database error, with pauses that grow up to a limit,
    until it completes, and returns its result. The operation is run again as a whole, so it is one that may run
    any number of times, e.g. a step of a startup that waits for a database through an outage or a failover.
    """
    outage = OutageTracker(component)
    retry_seconds = _retry_initial_seconds

    while True:
        try:
            out = func(*args)
            break
        except DBAPIError as e:
            logger.warning('%s waiting for the database, retry in %ss -> %s', component, retry_seconds, e)
            outage.on_failure()
            sleep(retry_seconds)
            retry_seconds = min(retry_seconds * 2, _retry_max_seconds)

    outage.on_success()

    return out

# ################################################################################################################################
# ################################################################################################################################

class OutageTracker:
    """ Measures how long a component that uses the database was unable to complete its operations, from its first
    failure to its next success, and logs that time when the component succeeds again.
    """

    def __init__(self, component:'str') -> 'None':

        # What the log entries name
        self.component = component

        # When the current run of failures began, or None while the component succeeds
        self.failed_at:'floatnone' = None

# ################################################################################################################################

    def on_failure(self) -> 'None':
        """ Records an operation that failed, the first one of a run of failures marking its beginning.
        """
        if self.failed_at is None:
            self.failed_at = monotonic()

# ################################################################################################################################

    def on_success(self) -> 'None':
        """ Records an operation that succeeded, logging how long the component took to resume if it was failing.
        """
        if self.failed_at is None:
            return

        elapsed = monotonic() - self.failed_at
        self.failed_at = None

        logger.info('%s resumed -> after:%.3fs', self.component, elapsed)

# ################################################################################################################################
# ################################################################################################################################
