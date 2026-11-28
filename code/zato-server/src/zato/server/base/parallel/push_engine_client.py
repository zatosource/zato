# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from itertools import count
from logging import getLogger

# gevent
from gevent import spawn
from gevent.event import AsyncResult
from gevent.socket import wait_read

# Zato
from zato.common.typing_ import cast_

# Zato - Rust
from zato_server_core.zato_server_core import PushEngine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent import Greenlet
    from zato.common.typing_ import anylist, anytuple, strnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The outcome of one job - the description of the internal error that ended it, or None, and the outcome of each request sent
job_outcome = tuple['strnone', 'anylist']

# ################################################################################################################################
# ################################################################################################################################

class PushEngineStopped(Exception):
    """ The push engine stopped before a job completed, so its messages are delivered again later.
    """

# ################################################################################################################################
# ################################################################################################################################

class PushEngineClient:
    """ Submits the push jobs of the delivery greenlets to the Rust push engine and returns their outcomes.
    One greenlet waits on the eventfd of the engine and hands each completed job to the greenlet that submitted it.
    The engine starts with the first job, so a process that delivers nothing starts no threads.
    """

    def __init__(self, thread_count:'int', pool_size:'int', stop_timeout:'float') -> 'None':
        self.thread_count = thread_count
        self.pool_size = pool_size
        self.stop_timeout = stop_timeout

        self._engine:'PushEngine | None' = None
        self._reader:'Greenlet | None' = None
        self._results:'dict[int, AsyncResult]' = {}
        self._job_ids = count(1)
        self._is_stopped = False

# ################################################################################################################################

    def _get_engine(self) -> 'PushEngine':
        """ Returns the engine, starting it and its reader greenlet on the first call.
        """
        if self._is_stopped:
            raise PushEngineStopped('The push engine is stopped')

        if self._engine is None:
            self._engine = PushEngine(self.thread_count, self.pool_size)
            self._reader = spawn(self._read_completed, self._engine)
            logger.info('Push engine started with %s threads', self.thread_count)

        return self._engine

# ################################################################################################################################

    def run(self, requests:'anylist', timeout:'float | None', tls:'anytuple') -> 'job_outcome':
        """ Runs one job - the ordered requests of one subscriber - and returns its outcome. A greenlet killed
        while it waits discards the outcome, and the messages it did not acknowledge are delivered again.
        """
        engine = self._get_engine()

        job_id = next(self._job_ids)
        result = AsyncResult()
        self._results[job_id] = result

        try:
            engine.submit(job_id, requests, timeout, tls)
            out = cast_('job_outcome', result.get())
        finally:
            del self._results[job_id]

        return out

# ################################################################################################################################

    def _set_completed(self, engine:'PushEngine') -> 'None':
        """ Hands the outcome of each job completed since the previous call to the greenlet waiting for it.
        """
        for job_id, internal_error, outcomes in engine.take_completed():

            # The greenlet of a job may have been killed while it waited, and nothing waits for its outcome then
            if job_id in self._results:
                self._results[job_id].set((internal_error, outcomes))

# ################################################################################################################################

    def _read_completed(self, engine:'PushEngine') -> 'None':
        """ Waits for the eventfd of the engine and hands out the outcomes of the completed jobs, until the engine stops.
        """
        fileno = engine.fileno()

        while True:
            wait_read(fileno)
            self._set_completed(engine)

# ################################################################################################################################

    def stop(self) -> 'bool':
        """ Stops the engine. The jobs in flight complete within the stop timeout, and their outcomes are handed out.
        The jobs not yet started fail with PushEngineStopped. Returns whether all the threads of the engine exited.
        """
        self._is_stopped = True

        if self._engine is None:
            return True

        if self._reader is not None:
            self._reader.kill()

        is_stopped = self._engine.stop(self.stop_timeout)

        # The jobs that completed while the engine stopped are handed out ..
        self._set_completed(self._engine)

        # .. and the greenlets of the jobs that never ran stop waiting.
        for result in self._results.values():
            if not result.ready():
                result.set_exception(PushEngineStopped('The push engine stopped before the push was sent'))

        if is_stopped:
            logger.info('Push engine stopped')
        else:
            logger.warning('Push engine threads did not stop within %s s', self.stop_timeout)

        return is_stopped

# ################################################################################################################################
# ################################################################################################################################
