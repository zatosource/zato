# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from threading import RLock
from time import monotonic
from traceback import format_exc

# gevent
from gevent import sleep, spawn

# redis
from redis import Redis

# Zato
from zato.common.rule_engine.changes import ModuleCtx as ChangesCtx
from zato.common.rule_engine.invocation import RulesetInvoker
from zato.common.rule_engine.sql import RuleSQLBackend
from zato.common.rule_engine.sql.constants import Default_DB_URL, Env_DB_URL
from zato.common.rule_engine.sql.database import create_database_engine
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist
    from zato.server.base.parallel import ParallelServer
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How often a still-failing change listener reminds about itself in the logs.
_listener_error_log_interval = 60.0

# ################################################################################################################################
# ################################################################################################################################

# The one backend and invoker of this process, shared by every request - the invoker owns
# the non-blocking decision writer and the RAM caches the change listener keeps correct.
_backend:'RuleSQLBackend | None' = None
_invoker:'RulesetInvoker | None' = None
_lock = RLock()

# ################################################################################################################################

def _build_backend() -> 'RuleSQLBackend':
    """ Builds the SQL facade over the rule engine's own database.
    """
    # The URL is the same one the rule engine dashboard reads ..
    database_url = os.environ.get(Env_DB_URL)

    if not database_url:
        database_url = Default_DB_URL

    # .. an SQLite connection has to be shareable with the writer thread ..
    if database_url.startswith('sqlite'):
        connection_options = {'check_same_thread': False}
        engine = create_database_engine(database_url, connect_args=connection_options)
    else:
        engine = create_database_engine(database_url)

    out = RuleSQLBackend.from_engine(engine)
    return out

# ################################################################################################################################

def get_backend() -> 'RuleSQLBackend':
    """ Returns the process-wide rule engine SQL facade, building it on first use.
    """
    global _backend

    with _lock:
        if _backend is None:
            _backend = _build_backend()

    out = _backend
    return out

# ################################################################################################################################

def get_invoker() -> 'RulesetInvoker':
    """ Returns the process-wide invoker, building it on the first request.
    """
    global _invoker

    with _lock:
        if _invoker is None:
            backend = get_backend()

            # The writer accepts decisions without blocking the requests that produce them.
            writer = backend.decision_writer()
            writer.start()

            _invoker = RulesetInvoker(backend, writer)

    out = _invoker
    return out

# ################################################################################################################################
# ################################################################################################################################

def _apply_change(fields:'anydict') -> 'None':
    """ Applies one announced change to the process-wide invoker's caches.
    An invoker that was never built has nothing cached, so there is nothing to evict either.
    """
    with _lock:
        invoker = _invoker

    if invoker is None:
        return

    definition_id = int(fields['definition_id'])
    invoker.apply_change(definition_id, fields['name'], fields['object_type'])

    logger.info('Rule engine cache evicted after `%s` of `%s` (id=%s)',
        fields['kind'], fields['name'], definition_id)

# ################################################################################################################################

def _evict_all() -> 'None':
    """ Drops every mutable cache entry of the process-wide invoker, if one exists.
    """
    with _lock:
        invoker = _invoker

    if invoker is not None:
        invoker.evict_all()

# ################################################################################################################################

def start_rule_engine_change_listener(server:'ParallelServer') -> 'None':
    """ Starts a greenlet that keeps this process's rule engine caches correct - it consumes
    the change stream the dashboard announces every committed write on and evicts exactly
    what each write invalidated.

    Every server process tails the whole stream with a plain XREAD - unlike request streams,
    where one server should take each message, an eviction has to reach all of them.
    """
    redis_config = server.fs_server_config.redis
    redis_password = redis_config.password if redis_config.password else None

    redis_conn = Redis(
        host=redis_config.host,
        port=redis_config.port,
        db=redis_config.db,
        password=redis_password,
        decode_responses=True,
    )

    def _listener_loop() -> 'None':

        # Only messages newer than the moment the listener starts matter - anything older
        # predates every cache entry this process could possibly hold.
        last_id = '$'

        error_since = 0.0
        last_logged = 0.0

        while True:
            try:
                result = redis_conn.xread({ChangesCtx.Changes_Stream: last_id}, count=100, block=1000)

                # A synchronous Redis client always returns a list here, never an awaitable
                result = cast_('anylist', result)

                # Reading works again after an error - announcements may have been missed in between,
                # so everything cached is dropped once and the next requests re-read the database.
                if error_since:
                    logger.info('Rule engine change listener recovered, evicting all caches')
                    _evict_all()
                    error_since = 0.0

                if not result:
                    continue

                for _stream_name, messages in result:
                    for msg_id, fields in messages:

                        # The next read continues right past this message.
                        last_id = msg_id

                        _apply_change(fields)

            except Exception as exc:

                # Log when the condition starts with the full traceback ..
                now = monotonic()

                if not error_since:
                    error_since = now
                    last_logged = now
                    logger.warning('Error in rule engine change listener: %s', format_exc())

                # .. and only a one-line reminder at most once a minute afterwards.
                elif now - last_logged >= _listener_error_log_interval:
                    last_logged = now
                    elapsed = int(now - error_since)
                    logger.warning('Rule engine change listener still failing after %ss: %s', elapsed, exc)

                # Messages published while the connection was down are gone for this listener,
                # which is fine - recovery above evicts everything cached.
                last_id = '$'
                sleep(1)

    _ = spawn(_listener_loop)

    logger.info('Rule engine change listener greenlet started')

# ################################################################################################################################
# ################################################################################################################################
