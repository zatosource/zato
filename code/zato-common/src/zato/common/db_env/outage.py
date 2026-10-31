# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from time import monotonic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import floatnone

    # Dummy assignments to satisfy type checkers
    floatnone = floatnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

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
