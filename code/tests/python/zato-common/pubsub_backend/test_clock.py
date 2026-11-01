# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
from gevent import joinall, sleep, spawn

# Zato
from zato.common.pubsub.sql.clock import DatabaseClock
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.typing_ import any_

    strdatetimedict = dict[str, datetime]

# ################################################################################################################################
# ################################################################################################################################

# The time that the database reports, in milliseconds since the Unix epoch.
_database_ms = 1_793_000_000_000

# How long the reading of the time of the database takes, and how long after the first caller the second one arrives.
_reading_seconds = 0.2
_second_caller_delay = 0.05

# ################################################################################################################################
# ################################################################################################################################

class _Result:
    def scalar_one(self) -> 'int':
        return _database_ms

# ################################################################################################################################

class _Connection:
    """ A connection whose query takes a while, so that other greenlets run while the reading is under way.
    """

    def __init__(self, engine:'_Engine') -> 'None':
        self.engine = engine

    def __enter__(self) -> '_Connection':
        return self

    def __exit__(self, *args:'any_') -> 'bool':
        return False

    def execute(self, query:'any_') -> '_Result':
        self.engine.readings += 1
        sleep(_reading_seconds)
        out = _Result()
        return out

# ################################################################################################################################

class _Dialect:
    name = 'postgresql'

# ################################################################################################################################

class _Engine:
    dialect = _Dialect()

    def __init__(self) -> 'None':
        self.readings = 0

    def connect(self) -> '_Connection':
        out = _Connection(self)
        return out

# ################################################################################################################################
# ################################################################################################################################

def test_first_reading_in_progress() -> 'None':
    """ A caller that arrives while the first reading of the time of PostgreSQL is under way waits for that reading
    and receives the time of the database, not the monotonic time of the host added to an empty reading.
    """
    engine = _Engine()
    clock = DatabaseClock(cast_('any_', engine))

    results:'strdatetimedict' = {}

    def _first() -> 'None':
        results['first'] = clock.now()

    def _second() -> 'None':
        sleep(_second_caller_delay)
        results['second'] = clock.now()

    _ = joinall([spawn(_first), spawn(_second)], raise_error=True)

    first_year = results['first'].year
    second_year = results['second'].year

    assert second_year == first_year, results
    assert engine.readings == 1, engine.readings

# ################################################################################################################################
# ################################################################################################################################
