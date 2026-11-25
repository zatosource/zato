# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The takeover of the Zato database while the previous server is frozen in a transaction that holds the row of the active
# server. The server of an active-standby node ends the session of the frozen server at once, because its node replaced
# that server before it started this one, while a server without a node waits for the frozen server first.

# stdlib
import json
import logging
import os
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass

# Zato
from zato.common.test.pubsub_database import connect, pubsub_db_env
from zato.common.test.takeover import ModuleCtx as TakeoverCtx, take_over_as_another_server
from zato.common.test.timing import Timer_Tolerance_Seconds

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.sql.backend import SQLPubSubBackend
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

timed_backend = tuple['SQLPubSubBackend', float]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The variable through which an active-standby node passes its generation to its server
    Env_HA_Generation = 'Zato_HA_Generation'

    # The server that holds the row of the active server in a transaction until its standard input is closed
    Holder_Path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'takeover_holder.py')

    # How long the holder may take to take the database over and to report its transaction
    Holder_Timeout = 60

    # How long the takeover of the server of a node may take while the previous server is frozen
    Node_Takeover_Limit = 1.0

    # How long a takeover without a node waits for the previous server before it ends its session,
    # and how much later than that it may complete
    Plain_Takeover_Wait = 5.0
    Plain_Takeover_Margin = 2.0

    # How far above the stored generation the nodes of each test begin
    Generation_Step = 10

    # The pool sizes that give each server of these tests an engine of its own, since engines are cached by their settings
    Pool_Size_Node_Holder = 2
    Pool_Size_Node        = 3
    Pool_Size_Plain_Holder = 4
    Pool_Size_Plain        = 5

    # The prefix of the directory of the generation file of each holder
    Holder_Dir_Prefix = 'zato_takeover_holder_'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class FrozenServer:
    """ A holder whose process is stopped while its transaction holds the row of the active server.
    """
    process: 'subprocess.Popen[str]'
    backend_pid: int

# ################################################################################################################################
# ################################################################################################################################

def _read_generation(database:'PubSubDatabase') -> 'int':
    """ Returns the generation of the active server as the database holds it.
    """
    connection = connect(database)

    try:
        cursor = connection.cursor()
        cursor.execute('select generation from zato_active where id = 1')
        row:'any_' = cursor.fetchone()
    finally:
        connection.close()

    out = row[0]
    return out

# ################################################################################################################################

def _is_session_present(database:'PubSubDatabase', backend_pid:'int') -> 'bool':
    """ Whether PostgreSQL still has the session of a process identifier.
    """
    connection = connect(database)

    try:
        cursor = connection.cursor()
        cursor.execute('select count(*) from pg_stat_activity where pid = %s', (backend_pid,))
        row:'any_' = cursor.fetchone()
    finally:
        connection.close()

    count = row[0]

    out = count == 1
    return out

# ################################################################################################################################

def _freeze_holder(database:'PubSubDatabase', pool_size:'int', ha_generation:'int | None') -> 'FrozenServer':
    """ Starts a holder that takes the database over, at the generation of a node if one is given,
    and stops its process once its transaction holds the row of the active server.
    """
    work_dir = tempfile.mkdtemp(prefix=ModuleCtx.Holder_Dir_Prefix)

    env = dict(os.environ)
    env.update(database.env)
    env[TakeoverCtx.Env_Generation_File] = os.path.join(work_dir, TakeoverCtx.Generation_File_Name)
    env[TakeoverCtx.Env_Pool_Size] = f'{pool_size}'

    if ha_generation is not None:
        env[ModuleCtx.Env_HA_Generation] = f'{ha_generation}'

    command = [sys.executable, ModuleCtx.Holder_Path]
    process = subprocess.Popen(command, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

    # The holder reports its transaction once the row is locked ..
    stdout:'any_' = process.stdout
    line = stdout.readline()

    if not line:
        _ = process.wait(ModuleCtx.Holder_Timeout)
        raise Exception(f'Holder exited with {process.returncode} before it reported its transaction')

    report = json.loads(line)

    # .. and its process is stopped, as a server whose host froze is, with the transaction left open.
    os.kill(process.pid, signal.SIGSTOP)

    out = FrozenServer()
    out.process = process
    out.backend_pid = report['backend_pid']

    return out

# ################################################################################################################################

def _release_holder(holder:'FrozenServer') -> 'None':
    """ Ends the process of a holder, whether it is stopped or not.
    """
    holder.process.kill()
    _ = holder.process.wait(ModuleCtx.Holder_Timeout)

    stdin:'any_' = holder.process.stdin
    stdin.close()

    stdout:'any_' = holder.process.stdout
    stdout.close()

# ################################################################################################################################

def _timed_takeover(database:'PubSubDatabase', pool_size:'int', ha_generation:'int | None') -> 'timed_backend':
    """ Takes the database over as another server, at the generation of a node if one is given,
    and returns its backend and how long the takeover took, in seconds.
    """
    env:'strstrdict' = dict(database.env)

    if ha_generation is not None:
        env[ModuleCtx.Env_HA_Generation] = f'{ha_generation}'

    started_at = time.monotonic()
    backend = take_over_as_another_server(env, pool_size)
    elapsed = time.monotonic() - started_at

    out = backend, elapsed
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_node_takeover_ends_the_frozen_server_at_once(pubsub_database:'PubSubDatabase') -> 'None':
    """ The server of a node takes the database over within Node_Takeover_Limit while the server of the previous
    generation is frozen in a transaction that holds the row of the active server, and the session of that server is ended.
    """
    stored_generation = _read_generation(pubsub_database)
    previous_generation = stored_generation + ModuleCtx.Generation_Step
    generation = previous_generation + 1

    # The server of the previous node takes over and is frozen in its transaction ..
    holder = _freeze_holder(pubsub_database, ModuleCtx.Pool_Size_Node_Holder, previous_generation)

    try:
        assert _is_session_present(pubsub_database, holder.backend_pid)

        # .. the server of the next node takes over ..
        backend, elapsed = _timed_takeover(pubsub_database, ModuleCtx.Pool_Size_Node, generation)
        logger.info('Takeover under a node -> %.3fs', elapsed)

        # .. without waiting for the frozen server, whose session is gone ..
        guard = backend.generation_guard
        assert guard is not None
        assert guard.generation == generation
        assert elapsed < ModuleCtx.Node_Takeover_Limit, elapsed
        assert not _is_session_present(pubsub_database, holder.backend_pid)

        # .. and the database names the server of the next node.
        assert _read_generation(pubsub_database) == generation

        with pubsub_db_env(pubsub_database.env):
            guard.uninstall(backend.engine)

    finally:
        _release_holder(holder)

# ################################################################################################################################

def test_plain_takeover_waits_for_the_frozen_server(pubsub_database:'PubSubDatabase') -> 'None':
    """ A server without a node waits Plain_Takeover_Wait for the frozen server of the previous generation
    before it ends its session and takes the database over.
    """
    stored_generation = _read_generation(pubsub_database)

    # The previous server takes over and is frozen in its transaction ..
    holder = _freeze_holder(pubsub_database, ModuleCtx.Pool_Size_Plain_Holder, None)

    try:
        assert _is_session_present(pubsub_database, holder.backend_pid)

        # .. the next server takes over ..
        backend, elapsed = _timed_takeover(pubsub_database, ModuleCtx.Pool_Size_Plain, None)
        logger.info('Takeover without a node -> %.3fs', elapsed)

        # .. only after the wait, once the session of the frozen server was ended ..
        guard = backend.generation_guard
        assert guard is not None
        assert guard.generation == stored_generation + 2
        assert elapsed >= ModuleCtx.Plain_Takeover_Wait - Timer_Tolerance_Seconds, elapsed
        assert elapsed < ModuleCtx.Plain_Takeover_Wait + ModuleCtx.Plain_Takeover_Margin, elapsed
        assert not _is_session_present(pubsub_database, holder.backend_pid)

        with pubsub_db_env(pubsub_database.env):
            guard.uninstall(backend.engine)

    finally:
        _release_holder(holder)

# ################################################################################################################################
# ################################################################################################################################
