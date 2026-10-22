# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone
from typing import Protocol

# ################################################################################################################################
# ################################################################################################################################

class Clock(Protocol):
    """ The source of the current time for the B2B protocol layers.
    """

    def now(self) -> 'datetime':
        """ Returns the current time as an aware datetime in UTC.
        """
        ...

# ################################################################################################################################
# ################################################################################################################################

class SystemClock:
    """ A clock that reads the system time.
    """

    def now(self) -> 'datetime':
        out = datetime.now(timezone.utc)
        return out

# ################################################################################################################################
# ################################################################################################################################

class ManualClock:
    """ A clock that stands still until it is advanced explicitly.
    """

    def __init__(self, start:'datetime') -> 'None':
        self._now = start

# ################################################################################################################################

    def now(self) -> 'datetime':
        out = self._now
        return out

# ################################################################################################################################

    def advance(self, seconds:'float') -> 'None':
        """ Moves the clock forward by the given number of seconds.
        """
        delta = timedelta(seconds=seconds)
        self._now = self._now + delta

# ################################################################################################################################
# ################################################################################################################################
