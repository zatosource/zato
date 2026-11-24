# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The generation of the active server. One server is active at a time and its standby is a stopped container.
# A server that starts raises the generation in the single row of zato_active and writes a value unique
# to itself, its owner, in the same statement, and each transaction of the pub/sub database first confirms that
# the generation and the owner are still those of its server. A transaction that writes locks the row for share,
# so raising the generation waits for the writes of the previous server in progress and every write that begins
# after it finds the row changed. A server that was replaced therefore changes no row, whether it was stopped,
# frozen or cut off from the network, and also when a failover of the database to a replica without the last raise
# lets another server reach its generation again. A server that an active-standby node starts sets the generation
# of the node's referee record in place of raising it, unless the stored generation is higher, in which case
# the node was replaced before its server started and the server does no pub/sub work. A plain raise waits
# up to five seconds for the transactions of the previous server before it ends their sessions, while a server
# of a node ends them at once, as its node starts it only after the previous server was replaced.

# stdlib
from logging import getLogger
from threading import Thread
from time import monotonic

# SQLAlchemy
from sqlalchemy import text

# Zato
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, AuditSource, is_audit_log_enabled
from zato.common.audit_log.bulk_insert import insert_pending_events
from zato.common.crypto.api import CryptoManager
from zato.common.db_env.fence import GenerationGuard, write_generation_file
from zato.common.db_env.outage import call_until_available
from zato.common.db_env.write_path import Mechanism, write_path
from zato.common.ha.common import get_node_generation
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Callable
    from sqlalchemy.engine import Connection, Engine
    from zato.common.typing_ import anylist, intnone, strnone

    engine_factory = Callable[[], Engine]

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How long raising the generation waits for the transactions of the previous server before it ends their sessions.
_takeover_wait_seconds = 5

# How often the sessions that hold up raising the generation are looked up again once the wait is over.
_takeover_check_seconds = 1

# The same two for a server of an active-standby node, whose node starts it only after the lease of the previous
# active node went unrenewed for the takeover time, so every session that still holds the row belongs to a server
# that was already replaced.
_node_takeover_wait_seconds = 0
_node_takeover_check_seconds = 0.05

# What raises the generation.
_raise_query = text('UPDATE zato_active SET generation = generation + 1, owner = :owner WHERE id = 1 ' + \
    'RETURNING generation')

# What sets the generation of an active-standby node, unless the stored generation is higher.
_set_query = text('UPDATE zato_active SET generation = :generation, owner = :owner WHERE id = 1 ' + \
    'AND generation <= :generation RETURNING generation')

# The object of the audit event that records a takeover of the Zato database.
Takeover_Object_Name = 'pubsub-database'

# What ends the sessions that keep the generation from being raised.
_backend_pid_query = text('SELECT pg_backend_pid()')
_terminate_blockers_query = text('SELECT pid, pg_terminate_backend(pid) FROM unnest(pg_blocking_pids(:pid)) AS pid')

# ################################################################################################################################
# ################################################################################################################################

class _ForkTakeover:
    """ The guard of the takeover that the arbiter ran before it forked the worker and the config process,
    which each of them inherits and follows in place of raising the generation itself.
    """
    guard: 'GenerationGuard | None' = None

# ################################################################################################################################
# ################################################################################################################################

class _EngineRecorder:
    """ Builds the engine of a takeover and retains it, so that the caller of the takeover disposes it afterwards.
    """

    def __init__(self, new_engine:'engine_factory') -> 'None':
        self.new_engine = new_engine
        self.engine:'Engine | None' = None

    def get_engine(self) -> 'Engine':
        out = self.new_engine()
        self.engine = out
        return out

# ################################################################################################################################
# ################################################################################################################################

class _GenerationRaiser:
    """ Raises the generation on a connection of its own, in a thread that the caller waits for, or sets it
    to the generation of an active-standby node. The generation remains None if the stored one is higher.
    A server with a name records the takeover in the audit log in the same transaction.
    """

    def __init__(self, engine:'Engine', owner:'str', ha_generation:'intnone', server_name:'strnone') -> 'None':
        self.engine = engine
        self.owner = owner
        self.ha_generation = ha_generation
        self.server_name = server_name
        self.backend_pid = 0
        self.generation:'intnone' = None
        self.takeover_event_id:'intnone' = None
        self.exception:'BaseException | None' = None

        # Set once the session that raises the generation knows its own process identifier.
        self.has_pid = False

    def run(self) -> 'None':
        try:
            with write_path(Mechanism.Takeover), self.engine.begin() as connection:
                self.backend_pid = connection.execute(_backend_pid_query).scalar_one()
                self.has_pid = True

                # A server without an active-standby node raises the generation by one ..
                if self.ha_generation is None:
                    self.generation = connection.execute(_raise_query, {'owner': self.owner}).scalar_one()

                # .. and a server of a node sets the generation of the node, unless a later node set a higher one.
                else:
                    parameters = {'generation': self.ha_generation, 'owner': self.owner}
                    self.generation = connection.execute(_set_query, parameters).scalar_one_or_none()

                # Each generation is one higher than the one it replaces, which the audit log records with the takeover,
                # and a server that a later one replaced before its start took nothing over.
                if self.server_name and self.generation is not None:
                    self.takeover_event_id = _insert_takeover_event(connection, self.server_name, self.generation)

        except BaseException as e:
            self.exception = e
            self.has_pid = True

# ################################################################################################################################

def _insert_takeover_event(connection:'Connection', server_name:'str', generation:'int') -> 'intnone':
    """ Records a takeover in the audit log in the transaction of the connection and returns the id of its event,
    or None when the audit log is turned off.
    """
    if not is_audit_log_enabled():
        return None

    previous_generation = generation - 1

    attrs = {
        'previous_generation': f'{previous_generation}',
        'generation': f'{generation}',
    }

    audit_log = AuditLog(server_name)
    audit_event = audit_log.new_pending_event(AuditSource.PubSub, AuditEvent.Takeover, Takeover_Object_Name,
        outcome=AuditOutcome.OK, attrs=attrs)

    event_ids = insert_pending_events(connection, [audit_event])

    out = event_ids[0]
    return out

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

def _raise_generation(engine:'Engine', owner:'str', ha_generation:'intnone', server_name:'strnone') -> '_GenerationRaiser':
    """ Raises the generation once, or sets the generation of an active-standby node, and writes the owner.
    Returns the raiser, whose generation is None if the stored generation is higher than the one of the node.
    The transactions of the previous server that are still in progress are waited for up to _takeover_wait_seconds,
    after which the sessions that still hold them are ended, as a frozen or cut-off server would hold its row locks
    until PostgreSQL notices the lost client. A server of an active-standby node ends them without that wait,
    looking them up every _node_takeover_check_seconds, because its node replaced the previous server before it started
    this one. A session that is ended rolls back a transaction that was never acknowledged.
    """
    raiser = _GenerationRaiser(engine, owner, ha_generation, server_name)

    # A server without a node waits for the previous server to complete its transactions ..
    if ha_generation is None:
        wait_seconds = _takeover_wait_seconds
        check_seconds = _takeover_check_seconds

    # .. while the previous server of a node has been replaced already.
    else:
        wait_seconds = _node_takeover_wait_seconds
        check_seconds = _node_takeover_check_seconds

    thread = Thread(target=raiser.run, daemon=True)
    thread.start()

    started_at = monotonic()

    # Wait for the generation to be raised by itself first ..
    thread.join(wait_seconds)

    # .. and end the sessions that keep it from completing after that.
    while thread.is_alive():

        if raiser.has_pid:
            terminated = _terminate_blockers(engine, raiser.backend_pid)

            if terminated:
                elapsed = monotonic() - started_at
                logger.warning('Ended pub/sub sessions of a previous server -> pids:%s, waited:%.1fs', terminated, elapsed)

        thread.join(check_seconds)

    if raiser.exception is not None:
        raise raiser.exception

    return raiser

# ################################################################################################################################

def _connect_and_raise_generation(
    get_engine:'engine_factory',
    owner:'str',
    ha_generation:'intnone',
    server_name:'strnone',
    ) -> 'tuple[Engine, _GenerationRaiser]':
    """ Builds the engine, which creates the schema if needed, and raises the generation through it.
    """
    engine = get_engine()
    raiser = _raise_generation(engine, owner, ha_generation, server_name)

    out = engine, raiser
    return out

# ################################################################################################################################

def take_over(get_engine:'engine_factory', server_name:'strnone') -> 'GenerationGuard':
    """ Makes this server the active one - raises the generation, or sets the generation of its active-standby node,
    and writes an owner unique to this server, waiting for the database to become available if it is not, records both
    and guards every subsequent transaction of the engine with them. The engine is built within the wait as well,
    because building it already connects to the database. A raise that is run again after an error writes the same owner.
    A server with a name records the takeover in the audit log in the transaction that raises the generation.
    The sessions of the previous server that hold up the raise are ended after _takeover_wait_seconds,
    and at once for a server of an active-standby node.
    """
    owner = CryptoManager.generate_hex_string()
    ha_generation = get_node_generation()

    engine, raiser = call_until_available(
        'Pub/sub takeover', _connect_and_raise_generation, get_engine, owner, ha_generation, server_name)

    generation = raiser.generation

    # A node that a later node replaced before its server set the generation leaves the server replaced from its start ..
    if generation is None:
        generation = cast_('int', ha_generation)
        is_replaced = True
        logger.warning('Pub/sub generation %s is below the current one, this server does no pub/sub work', generation)

    # .. otherwise the server is the active one.
    else:
        is_replaced = False
        logger.info('Pub/sub generation raised -> %s, owner:%s', generation, owner)

    write_generation_file(generation, owner)

    out = GenerationGuard(generation, owner)
    out.is_replaced = is_replaced
    out.takeover_event_id = raiser.takeover_event_id
    out.install(engine)

    return out

# ################################################################################################################################

def take_over_before_fork(new_engine:'engine_factory', server_name:'str') -> 'GenerationGuard':
    """ Makes this server the active one once for the processes that its arbiter forks next, through an engine
    that is disposed before the fork, and retains the guard for those processes, each of which follows it on an engine of its own.
    The guard remains bound to the generation file of the server, so every engine that a forked process builds
    confirms the generation from the start of the process.
    """
    recorder = _EngineRecorder(new_engine)
    out = take_over(recorder.get_engine, server_name)

    engine = cast_('Engine', recorder.engine)
    engine.dispose()

    _ForkTakeover.guard = out

    return out

# ################################################################################################################################

def get_fork_takeover() -> 'GenerationGuard | None':
    """ Returns the guard of the takeover that the arbiter ran before the fork, or None in a process without an arbiter.
    """
    out = _ForkTakeover.guard
    return out

# ################################################################################################################################

def follow_takeover(engine:'Engine', fork_guard:'GenerationGuard') -> 'GenerationGuard':
    """ Guards every transaction of the engine of a process that an arbiter started with the generation and the owner
    that its arbiter recorded, without raising the generation, which would replace the arbiter and the other process.
    """
    out = GenerationGuard(fork_guard.generation, fork_guard.owner)
    out.is_replaced = fork_guard.is_replaced
    out.takeover_event_id = fork_guard.takeover_event_id
    out.install(engine)

    return out

# ################################################################################################################################
# ################################################################################################################################
