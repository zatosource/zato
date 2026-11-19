# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from math import inf
from threading import Lock
from time import monotonic
from weakref import WeakKeyDictionary

# SQLAlchemy
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError

# Zato
from zato.common.common_db.schema import shared_object_table
from zato.common.common_db.store import SharedObjectStore
from zato.common.db_env.common import Type_PostgreSQL
from zato.common.db_env.database import get_database_engine
from zato.common.db_env.write_path import get_write_path
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

# The shared object that holds the floor of the time of the database on SQLite, which no time issued falls below,
# and the key of the floor in its document, in milliseconds since the Unix epoch.
Floor_Object_Type = 'zato.database.clock'
Floor_Object_Name = 'floor'
Floor_Key = 'floor_ms'

# The floor of a database that holds none yet.
_no_floor_ms = 0

# How far ahead of the time issued the floor is persisted, and how close the time issued may come
# to the floor before the floor is persisted again, in milliseconds.
_floor_lead_ms = 5000
_floor_renewal_ms = 2500

# The document of the floor.
_floor_query = select(shared_object_table.c.data)
_floor_query = _floor_query.where(shared_object_table.c.object_type == Floor_Object_Type)
_floor_query = _floor_query.where(shared_object_table.c.name == Floor_Object_Name)

# The clock of each engine of the pub/sub database.
_clocks:'clockdict' = WeakKeyDictionary()

# ################################################################################################################################
# ################################################################################################################################

class DatabaseClock:
    """ The time that the expirations, the leases and the retention of pub/sub are measured against. On PostgreSQL,
    it is the time of the database server, read once per synchronization interval, and on SQLite, it is the time
    of the host when the clock is created. Between two readings, the monotonic clock of the host advances the time,
    so that a change of the time of the host moves no expiration, no lease and no retention. On SQLite, the clock
    persists a floor ahead of the time it issues, and a clock created later starts from the floor if the time
    of its host is behind it, so that the time of the database never moves backwards across a restart or a takeover
    by a host whose clock is behind.
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

        # What the callers that arrive during the first reading wait on.
        self._first_reading_lock = Lock()

        # The floor that the clock persisted on SQLite, and whether a caller is persisting a new one.
        self._floor_store = SharedObjectStore(engine)
        self._floor_ms = _no_floor_ms
        self._is_renewing_floor = False

        # PostgreSQL is read on first use, whereas the time of the host is read once, now,
        # and a time behind the floor that an earlier clock persisted is replaced by the floor.
        if not self.is_postgresql:
            now = utcnow()
            now_ms = int(datetime_to_ms(now))

            self._floor_ms = self._read_floor()

            self._anchor_ms = max(now_ms, self._floor_ms)
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

    def _read_floor(self) -> 'int':
        """ Returns the floor of the time of the database on SQLite, read without the write lock of the file.
        """
        with self.engine.connect() as connection:
            data = connection.execute(_floor_query).scalar_one_or_none()

        if data is None:
            out = _no_floor_ms
        else:
            out = data[Floor_Key]

        return out

# ################################################################################################################################

    def _write_floor(self, floor_ms:'int') -> 'int':
        """ Persists a floor of the time of the database on SQLite unless another clock persisted a higher one,
        and returns the floor that is persisted.
        """
        store = self._floor_store
        data = {Floor_Key: floor_ms}

        # Each write is a compare-and-set, so a clock of another process that wrote in the meantime makes this one read again.
        while True:
            current = store.get(Floor_Object_Type, Floor_Object_Name)

            if current is None:
                if store.compare_and_set(Floor_Object_Type, Floor_Object_Name, data, None):
                    out = floor_ms
                    break

            else:
                current_floor_ms = current.data[Floor_Key]

                if current_floor_ms >= floor_ms:
                    out = current_floor_ms
                    break

                if store.compare_and_set(Floor_Object_Type, Floor_Object_Name, data, current.version):
                    out = floor_ms
                    break

        return out

# ################################################################################################################################

    def _renew_floor(self, now_ms:'int') -> 'None':
        """ Persists the floor ahead of the time issued on SQLite.
        """

        # One caller persists the floor at a time, and never from within the work of a mechanism,
        # whose write lock of the file the write of the floor would wait for ..
        if self._is_renewing_floor or get_write_path():
            return

        self._is_renewing_floor = True

        try:
            self._floor_ms = self._write_floor(now_ms + _floor_lead_ms)

        # .. and a floor that could not be persisted is persisted by the next caller.
        except DBAPIError:
            logger.warning('The floor of the time of the pub/sub database could not be persisted')

        finally:
            self._is_renewing_floor = False

# ################################################################################################################################

    def _read_first(self) -> 'None':
        """ Takes the first reading of the time of PostgreSQL, unless another caller took it while this one waited.
        """
        with self._first_reading_lock:
            if not self._is_synchronized:
                current = monotonic()
                self._synchronize(current)

# ################################################################################################################################

    def now_ms(self) -> 'int':
        """ The time of the database in milliseconds since the Unix epoch.
        """
        current = monotonic()

        # The first reading is taken once, and the callers that arrive while it is under way wait for it,
        # because until it completes, there is no time to advance ..
        if not self._is_synchronized:
            self._read_first()
            current = monotonic()

        # .. after which a reading that is due is taken first ..
        elif current >= self._next_synchronization:
            self._synchronize(current)
            current = monotonic()

        # .. and the monotonic clock advances the time from the last reading.
        elapsed = current - self._anchor_monotonic
        elapsed_ms = int(elapsed * _ms_per_second)

        out = self._anchor_ms + elapsed_ms

        # On SQLite, the floor stays ahead of every time issued, so that the next clock starts above it.
        if not self.is_postgresql:
            if out + _floor_renewal_ms >= self._floor_ms:
                self._renew_floor(out)

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

def get_engine_clock(engine:'Engine') -> 'DatabaseClock':
    """ The clock of the pub/sub database of one engine.
    """
    if clock := _clocks.get(engine):
        out = clock
    else:
        out = DatabaseClock(engine)
        _clocks[engine] = out

    return out

# ################################################################################################################################

def get_database_clock() -> 'DatabaseClock':
    """ The clock of the Zato database that the Zato_Database_* variables select.
    """
    engine = get_database_engine()

    out = get_engine_clock(engine)
    return out

# ################################################################################################################################
# ################################################################################################################################
