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
from zato.common.audit_log.common import event_count_table
from zato.common.audit_log.event_count import compact_event_counts
from zato.common.audit_log.retention import RetentionRun, run_retention
from zato.common.db_env.engine import call_database
from zato.common.util.api import utcnow
from zato.common.worker_slot import is_worker_process

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import anydict

    # Dummy assignments to satisfy type checkers
    anydict = anydict
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# How many chunks of rows one call of the database of a retention run writes
_chunks_per_call = 1

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

        # The thread starts with the first request ..
        self._is_started = False

        # .. and runs until it is stopped, after which the next request starts it again
        self._thread:'Thread | None' = None
        self._is_stopping = False

        # The highest id of the count table of each engine that its previous compaction left behind
        self._compacted_up_to:'anydict' = {}

# ################################################################################################################################

    def request(self, engine:'Engine') -> 'None':
        """ Requests a retention run on the database of an engine and returns at once.
        """
        with self._lock:

            if engine not in self._requested:
                self._requested.append(engine)

            if not self._is_started:
                self._is_started = True
                self._is_stopping = False
                self._thread = Thread(target=self._run, name='audit-log-retention', daemon=True)
                self._thread.start()

        self._wake_event.set()

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the thread after the call of the database in progress, if any, and waits for it to end. The requests
        not yet served are discarded, and the next request starts a new run.
        """
        with self._lock:
            thread = self._thread
            self._is_stopping = True
            self._requested = []

        if thread:
            self._wake_event.set()
            thread.join()

        with self._lock:
            self._thread = None
            self._is_started = False

# ################################################################################################################################

    def _run(self) -> 'None':
        """ Runs retention on each requested engine, one engine after another, whenever requests arrive.
        """
        while True:

            # Wait for a request ..
            _ = self._wake_event.wait()
            self._wake_event.clear()

            # .. take all the engines requested so far, unless the runner is stopping ..
            with self._lock:
                if self._is_stopping:
                    return
                engines = self._requested
                self._requested = []

            # .. and run retention on each of them.
            for engine in engines:

                now = utcnow()
                retention_start = monotonic()
                run = RetentionRun(now, _chunks_per_call)

                # Each call of the run writes one chunk, and the run continues until no work remains
                # or until the runner is stopping.
                try:
                    while run.has_remaining_work:
                        if self._is_stopping:
                            break
                        call_database(engine, run_retention, engine, now, run)
                except Exception:
                    logger.exception('Audit log retention could not be completed')

                retention_elapsed = monotonic() - retention_start
                retention_elapsed_ms = retention_elapsed * 1000

                logger.debug('Audit log retention completed in %.1f ms', retention_elapsed_ms)

                # The count rows that the writes and the retention above added are compacted next, unless the runner is stopping.
                if not self._is_stopping:
                    self._compact(engine)

# ################################################################################################################################

    def _compact(self, engine:'Engine') -> 'None':
        """ Compacts the count table of one engine's database, starting above the highest id its previous compaction saw.
        """
        if engine in self._compacted_up_to:
            compacted_up_to = self._compacted_up_to[engine]
        else:
            compacted_up_to = 0

        try:
            compacted_up_to = call_database(engine, compact_event_counts, engine, event_count_table, compacted_up_to)
        except Exception:
            logger.exception('Audit log event counts could not be compacted')
        else:
            self._compacted_up_to[engine] = compacted_up_to

# ################################################################################################################################
# ################################################################################################################################

# The one runner of the process, shared by all the writers of the audit log.
_runner = RetentionRunner()

# ################################################################################################################################

def request_retention(engine:'Engine') -> 'None':
    """ Requests a retention run on the database of an engine, without waiting for it. The worker runs retention
    and the config process does not, so that no two runs archive the same expired events.
    """
    if is_worker_process():
        _runner.request(engine)

# ################################################################################################################################

def stop_retention_runner() -> 'None':
    """ Stops the thread of the runner of this process and waits for it to end, if one is running.
    """
    _runner.stop()

# ################################################################################################################################
# ################################################################################################################################
