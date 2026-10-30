# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The checkpoints of the write-ahead log of a SQLite database, run in a thread of their own. A checkpoint copies
# the pages of the log into the database file and flushes both files to disk. When a commit leaves the log over
# the automatic checkpoint limit, that commit runs the checkpoint itself, which delays it by the time of the flushes.
# With the checkpoints run in the background, the log stays below the limit and commits only append to it.

# stdlib
from logging import getLogger
from threading import Event, Thread

# gevent
from gevent import get_hub
from gevent.monkey import is_module_patched

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import any_

    # Dummy assignments to satisfy type checkers
    any_ = any_
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How often the background checkpoint runs, in seconds.
Checkpoint_Interval_Seconds = 0.5

# How many pages the log may hold before a commit checkpoints it by itself, should the background checkpoints fall behind.
Autocheckpoint_Pages = 10_000

# A checkpoint that copies what it can without waiting for the readers or the writers of the database.
_checkpoint_statement = 'pragma wal_checkpoint(passive)'

# ################################################################################################################################
# ################################################################################################################################

def set_background_checkpoint_limit(dbapi_connection:'any_', connection_record:'any_') -> 'None':
    """ Raises the automatic checkpoint limit of a connection whose database is checkpointed in the background.
    """
    cursor = dbapi_connection.cursor()
    _ = cursor.execute(f'pragma wal_autocheckpoint={Autocheckpoint_Pages}')
    cursor.close()

# ################################################################################################################################
# ################################################################################################################################

class WALCheckpointer:
    """ Checkpoints the write-ahead log of a SQLite database at each interval, in a thread of its own.
    """

    def __init__(self, engine:'Engine', interval_seconds:'float'=Checkpoint_Interval_Seconds) -> 'None':
        self.engine = engine
        self.interval_seconds = interval_seconds
        self._stop_event = Event()
        self._thread = Thread(target=self._run, name='sqlite-wal-checkpoint', daemon=True)

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts checkpointing the log.
        """
        self._thread.start()

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops checkpointing the log after the checkpoint in progress, if any.
        """
        self._stop_event.set()

# ################################################################################################################################

    def checkpoint(self) -> 'None':
        """ Copies the pages of the log into the database file.
        """
        with self.engine.connect() as connection:
            _ = connection.exec_driver_sql(_checkpoint_statement)

# ################################################################################################################################

    def _checkpoint_off_loop(self) -> 'None':
        """ Runs one checkpoint, in the thread pool of the gevent hub under gevent, because the SQLite driver
        performs its calls in C without yielding to the event loop.
        """
        if is_module_patched('threading'):
            hub = get_hub()
            _ = hub.threadpool.apply(self.checkpoint)
        else:
            self.checkpoint()

# ################################################################################################################################

    def _run(self) -> 'None':
        """ Checkpoints the log at each interval, until the checkpointer is stopped.
        """
        while not self._stop_event.wait(self.interval_seconds):
            try:
                self._checkpoint_off_loop()
            except Exception:
                logger.exception('SQLite WAL checkpoint failed')

# ################################################################################################################################
# ################################################################################################################################
