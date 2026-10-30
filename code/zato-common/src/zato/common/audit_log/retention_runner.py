# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from threading import Event, Lock, Thread
from time import monotonic

# Zato
from zato.common.audit_log.retention import run_retention
from zato.common.db_env.engine import call_database
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine

    # Dummy assignments to satisfy type checkers
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Type aliases
engine_list = list['Engine']

# ################################################################################################################################
# ################################################################################################################################

class RetentionRunner:
    """ Runs the retention of the audit log in a thread of its own, so that no write waits for it.
    Each request names the engine whose database the retention runs on, and the requests that arrive
    while a run is in progress are served by the run that follows it.
    """

    def __init__(self) -> 'None':

        # Guards the requested engines and the start of the thread
        self._lock = Lock()

        # The engines whose retention was requested and has not run yet, in the order of the requests
        self._requested:'engine_list' = []

        # Set when a request arrives
        self._wake_event = Event()

        # The thread starts with the first request
        self._is_started = False

# ################################################################################################################################

    def request(self, engine:'Engine') -> 'None':
        """ Requests a retention run on the database of an engine and returns at once.
        """
        with self._lock:

            if engine not in self._requested:
                self._requested.append(engine)

            if not self._is_started:
                self._is_started = True
                thread = Thread(target=self._run, name='audit-log-retention', daemon=True)
                thread.start()

        self._wake_event.set()

# ################################################################################################################################

    def _run(self) -> 'None':
        """ Runs retention on each requested engine, one engine after another, whenever requests arrive.
        """
        while True:

            # Wait for a request ..
            _ = self._wake_event.wait()
            self._wake_event.clear()

            # .. take all the engines requested so far ..
            with self._lock:
                engines = self._requested
                self._requested = []

            # .. and run retention on each of them.
            for engine in engines:

                now = utcnow()
                retention_start = monotonic()

                try:
                    call_database(engine, run_retention, engine, now)
                except Exception:
                    logger.exception('Audit log retention could not be completed')

                retention_elapsed = monotonic() - retention_start
                retention_elapsed_ms = retention_elapsed * 1000

                logger.debug('Audit log retention completed in %.1f ms', retention_elapsed_ms)

# ################################################################################################################################
# ################################################################################################################################

# The one runner of the process, shared by all the writers of the audit log.
_runner = RetentionRunner()

# ################################################################################################################################

def request_retention(engine:'Engine') -> 'None':
    """ Requests a retention run on the database of an engine, without waiting for it.
    """
    _runner.request(engine)

# ################################################################################################################################
# ################################################################################################################################
