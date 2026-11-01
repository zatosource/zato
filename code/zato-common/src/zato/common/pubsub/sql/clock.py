# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from math import inf
from time import monotonic
from weakref import WeakKeyDictionary

# SQLAlchemy
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

# Zato
from zato.common.db_env.common import Type_PostgreSQL
from zato.common.pubsub.sql.config import get_pubsub_engine
from zato.common.typing_ import cast_
from zato.common.util.time_ import datetime_from_ms, datetime_to_ms, utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Engine

    clockdict = WeakKeyDictionary[Engine, 'DatabaseClock']

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How often the time of PostgreSQL is read again, in seconds.
_synchronization_interval_seconds = 60

_ms_per_second = 1000

# The time of the PostgreSQL server in milliseconds since the Unix epoch.
_database_now_query = text('select (extract(epoch from clock_timestamp()) * 1000)::bigint')

# The clock of each engine of the pub/sub database.
_clocks:'clockdict' = WeakKeyDictionary()

# ################################################################################################################################
# ################################################################################################################################

class DatabaseClock:
    """ The time that the expirations, the leases and the retention of pub/sub are measured against. On PostgreSQL,
    it is the time of the database server, read once per synchronization interval, and on SQLite, it is the time
    of the host when the clock is created. Between two readings, the monotonic clock of the host advances the time,
    so that a change of the time of the host moves no expiration, no lease and no retention.
    """

    def __init__(self, engine:'Engine') -> 'None':
        self.engine = engine
        self.is_postgresql = engine.dialect.name == Type_PostgreSQL

        # The time of the last reading, in milliseconds since the Unix epoch, and the monotonic time it was taken at.
        self._anchor_ms = 0
        self._anchor_monotonic = 0.0

        # When the time is read next and whether it was read at all.
        self._next_synchronization = 0.0
        self._is_synchronized = False

        # PostgreSQL is read on first use, whereas the time of the host is read once, now.
        if not self.is_postgresql:
            now = utcnow()
            now_ms = datetime_to_ms(now)

            self._anchor_ms = int(now_ms)
            self._anchor_monotonic = monotonic()
            self._next_synchronization = inf
            self._is_synchronized = True

# ################################################################################################################################

    def _synchronize(self, current:'float') -> 'None':
        """ Reads the time of PostgreSQL.
        """

        # The next reading is due one interval from now, including when this one fails ..
        self._next_synchronization = current + _synchronization_interval_seconds

        try:
            with self.engine.connect() as connection:
                started = monotonic()
                database_ms = connection.execute(_database_now_query).scalar_one()
                finished = monotonic()

        # .. in which case the previous reading remains in use, unless there is none yet ..
        except DBAPIError:
            if not self._is_synchronized:
                raise
            logger.warning('The time of the pub/sub database could not be read, the previous reading remains in use')
            return

        # .. and the reading belongs to the middle of its round trip.
        round_trip_sum = started + finished

        self._anchor_ms = database_ms
        self._anchor_monotonic = round_trip_sum / 2
        self._is_synchronized = True

# ################################################################################################################################

    def now_ms(self) -> 'int':
        """ The time of the database in milliseconds since the Unix epoch.
        """
        current = monotonic()

        # A reading that is due is taken first ..
        if current >= self._next_synchronization:
            self._synchronize(current)
            current = monotonic()

        # .. and the monotonic clock advances the time from the last reading.
        elapsed = current - self._anchor_monotonic
        elapsed_ms = int(elapsed * _ms_per_second)

        out = self._anchor_ms + elapsed_ms
        return out

# ################################################################################################################################

    def now(self) -> 'datetime':
        """ The time of the database as a datetime in UTC.
        """
        now_ms = self.now_ms()
        now = datetime_from_ms(now_ms, isoformat=False)

        out = cast_('datetime', now)
        return out

# ################################################################################################################################
# ################################################################################################################################

def get_database_clock() -> 'DatabaseClock':
    """ The clock of the pub/sub database that the Zato_PubSub_DB_* variables select.
    """
    engine = get_pubsub_engine()

    if clock := _clocks.get(engine):
        out = clock
    else:
        out = DatabaseClock(engine)
        _clocks[engine] = out

    return out

# ################################################################################################################################
# ################################################################################################################################
