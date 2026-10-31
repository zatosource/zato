# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The generation of the active server. One server is active at a time and its standby is a stopped container.
# A server that starts on PostgreSQL raises the generation in the single row of pubsub_active, and each transaction
# of the pub/sub database first confirms that the generation is still the one its server raised it to. A transaction
# that writes locks the row for share, so raising the generation waits for the writes of the previous server in progress
# and every write that begins after it finds the generation changed. A server that was replaced therefore changes
# no row, whether it was stopped, frozen or cut off from the network.

# stdlib
import os
from logging import getLogger
from threading import Thread
from time import monotonic

# SQLAlchemy
from sqlalchemy import event, text

# Zato
from zato.common.db_env.outage import call_until_available
from zato.common.pubsub.sql.config import get_generation_file_path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, Engine
    from zato.common.typing_ import any_, anylist, callable_

    # Dummy assignments to satisfy type checkers
    any_ = any_
    anylist = anylist
    callable_ = callable_
    Connection = Connection
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How long raising the generation waits for the transactions of the previous server before it ends their sessions.
_takeover_wait_seconds = 5

# How often the sessions that hold up raising the generation are looked up again once the wait is over.
_takeover_check_seconds = 1

# The keys under which a pooled connection records how far its current transaction confirmed the generation.
_state_key = 'zato_pubsub_generation_state'
_state_checked = 'checked'
_state_locked = 'locked'

# The statements that a read begins with - everything else writes.
_read_prefix = 'SELECT'
_write_clause = 'FOR UPDATE'

# What a transaction runs before its first read and before its first write.
_check_query = 'SELECT 1 FROM pubsub_active WHERE id = 1 AND generation = %s'
_lock_query = 'SELECT 1 FROM pubsub_active WHERE id = 1 AND generation = %s FOR SHARE'

# What raises the generation.
_raise_query = text('UPDATE pubsub_active SET generation = generation + 1 WHERE id = 1 RETURNING generation')

# What ends the sessions that keep the generation from being raised.
_backend_pid_query = text('SELECT pg_backend_pid()')
_terminate_blockers_query = text('SELECT pid, pg_terminate_backend(pid) FROM unnest(pg_blocking_pids(:pid)) AS pid')

# ################################################################################################################################
# ################################################################################################################################

class PubSubReplaced(Exception):
    """ Raised by every pub/sub transaction of a server whose generation is no longer the current one.
    """

# ################################################################################################################################
# ################################################################################################################################

def _is_write(statement:'str') -> 'bool':
    """ Whether a statement changes rows or locks them.
    """
    stripped = statement.lstrip()
    prefix = stripped[:len(_read_prefix)]

    if prefix.upper() != _read_prefix:
        out = True
    else:
        out = _write_clause in statement

    return out

# ################################################################################################################################
# ################################################################################################################################

class GenerationGuard:
    """ Confirms the generation of this server in each transaction of one engine, before the first statement
    of the transaction runs. A read confirms it once, and the first write of a transaction also locks the row
    for share until the transaction ends.
    """

    def __init__(self, generation:'int') -> 'None':
        self.generation = generation

        # Once replaced, a server remains replaced, because generations only ever increase.
        self.is_replaced = False

# ################################################################################################################################

    def install(self, engine:'Engine') -> 'None':
        """ Attaches the guard to all the transactions of an engine.
        """
        event.listen(engine, 'before_cursor_execute', self.before_cursor_execute)
        event.listen(engine, 'commit', self.on_transaction_end)
        event.listen(engine, 'rollback', self.on_transaction_end)
        event.listen(engine, 'checkout', self.on_checkout)

# ################################################################################################################################

    def uninstall(self, engine:'Engine') -> 'None':
        """ Detaches the guard from an engine.
        """
        event.remove(engine, 'before_cursor_execute', self.before_cursor_execute)
        event.remove(engine, 'commit', self.on_transaction_end)
        event.remove(engine, 'rollback', self.on_transaction_end)
        event.remove(engine, 'checkout', self.on_checkout)

# ################################################################################################################################

    def _raise_replaced(self) -> 'None':
        message = f'This server was replaced by another one and its pub/sub generation {self.generation} is no longer current'
        raise PubSubReplaced(message)

# ################################################################################################################################

    def before_cursor_execute(
        self,
        connection:'Connection',
        cursor:'any_',
        statement:'str',
        parameters:'any_',
        context:'any_',
        executemany:'bool',
    ) -> 'None':
        """ Confirms the generation before the first read and before the first write of each transaction.
        """
        if self.is_replaced:
            self._raise_replaced()

        state = connection.info.get(_state_key)

        # The transaction holds the lock already ..
        if state == _state_locked:
            return

        is_write = _is_write(statement)

        # .. or it confirmed the generation and is still only reading ..
        if state == _state_checked and not is_write:
            return

        # .. otherwise, the generation is confirmed now, with the lock for a write.
        if is_write:
            query = _lock_query
            new_state = _state_locked
        else:
            query = _check_query
            new_state = _state_checked

        cursor.execute(query, (self.generation,))
        row = cursor.fetchone()

        if row is None:
            self.is_replaced = True
            logger.warning('Pub/sub generation %s was replaced, this server stops its pub/sub work', self.generation)
            self._raise_replaced()

        connection.info[_state_key] = new_state

# ################################################################################################################################

    def on_transaction_end(self, connection:'Connection') -> 'None':
        """ A transaction that ended releases its lock, so the next one confirms the generation again.
        """
        # A lost connection is replaced together with its info, and reading the info of the lost one
        # would raise in place of the error that the connection was lost with.
        if connection.invalidated:
            return

        _ = connection.info.pop(_state_key, None)

# ################################################################################################################################

    def on_checkout(self, dbapi_connection:'any_', connection_record:'any_', connection_proxy:'any_') -> 'None':
        """ A connection taken out of the pool begins with no transaction.
        """
        _ = connection_record.info.pop(_state_key, None)

# ################################################################################################################################
# ################################################################################################################################

class _GenerationRaiser:
    """ Raises the generation on a connection of its own, in a thread that the caller waits for.
    """

    def __init__(self, engine:'Engine') -> 'None':
        self.engine = engine
        self.backend_pid = 0
        self.generation = 0
        self.exception:'BaseException | None' = None

        # Set once the session that raises the generation knows its own process identifier.
        self.has_pid = False

    def run(self) -> 'None':
        try:
            with self.engine.begin() as connection:
                self.backend_pid = connection.execute(_backend_pid_query).scalar_one()
                self.has_pid = True
                self.generation = connection.execute(_raise_query).scalar_one()
        except BaseException as e:
            self.exception = e
            self.has_pid = True

# ################################################################################################################################

def _terminate_blockers(engine:'Engine', backend_pid:'int') -> 'anylist':
    """ Ends the sessions that keep the given backend from raising the generation and returns their process identifiers.
    """
    out:'anylist' = []

    with engine.begin() as connection:
        for row in connection.execute(_terminate_blockers_query, {'pid': backend_pid}):
            out.append(row.pid)

    return out

# ################################################################################################################################

def _raise_generation(engine:'Engine') -> 'int':
    """ Raises the generation once. The transactions of the previous server that are still in progress are waited for
    up to a fixed time, after which the sessions that still hold them are ended, as a frozen or cut-off server
    would hold its row locks until PostgreSQL notices the lost client.
    """
    raiser = _GenerationRaiser(engine)

    thread = Thread(target=raiser.run, daemon=True)
    thread.start()

    started_at = monotonic()

    # Wait for the generation to be raised by itself first ..
    thread.join(_takeover_wait_seconds)

    # .. and end the sessions that keep it from completing after that.
    while thread.is_alive():

        if raiser.has_pid:
            terminated = _terminate_blockers(engine, raiser.backend_pid)

            if terminated:
                elapsed = monotonic() - started_at
                logger.warning('Ended pub/sub sessions of a previous server -> pids:%s, waited:%.1fs', terminated, elapsed)

        thread.join(_takeover_check_seconds)

    if raiser.exception is not None:
        raise raiser.exception

    out = raiser.generation
    return out

# ################################################################################################################################

def write_generation_file(generation:'int') -> 'None':
    """ Records the generation of this server for the cleanup process that the server's environment runs.
    """
    path = get_generation_file_path()
    temp_path = f'{path}.tmp'

    with open(temp_path, 'w') as generation_file:
        _ = generation_file.write(str(generation))

    os.replace(temp_path, path)

# ################################################################################################################################

def read_generation_file() -> 'int':
    """ Returns the generation that the server of this environment recorded.
    """
    path = get_generation_file_path()

    with open(path) as generation_file:
        value = generation_file.read()

    out = int(value)
    return out

# ################################################################################################################################

def _connect_and_raise_generation(get_engine:'callable_') -> 'tuple[Engine, int]':
    """ Builds the engine, which creates the schema if needed, and raises the generation through it.
    """
    engine = get_engine()
    generation = _raise_generation(engine)

    out = engine, generation
    return out

# ################################################################################################################################

def take_over(get_engine:'callable_') -> 'GenerationGuard':
    """ Makes this server the active one - raises the generation, waiting for the database to become available
    if it is not, records the new generation and guards every subsequent transaction of the engine with it.
    The engine is built within the wait as well, because building it already connects to the database.
    """
    engine, generation = call_until_available('Pub/sub takeover', _connect_and_raise_generation, get_engine)

    write_generation_file(generation)

    out = GenerationGuard(generation)
    out.install(engine)

    logger.info('Pub/sub generation raised -> %s', generation)

    return out

# ################################################################################################################################
# ################################################################################################################################
