# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import traceback
from json import dumps, loads
from multiprocessing import get_context

# gevent
import gevent

# Zato
from writer_common import new_message_values
from zato.common.pubsub.sql.clock import get_database_clock
from zato.common.pubsub.sql.config import get_pubsub_engine, ModuleCtx as ConfigCtx
from zato.common.pubsub.sql.schema import topic_sub_table
from zato.common.pubsub.sql.writes import new_pending_publication, PubSubWriter
from zato.common.pubsub.writer_process.handlers import WriterHandlers
from zato.common.pubsub.writer_process.remote import lease, start_writer_client
from zato.common.pubsub.writer_process.server import new_listening_socket, WriterServer
from zato.common.test.pubsub_database import pubsub_db_env, PubSubDBMode, start_pubsub_database, stop_pubsub_database

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.synchronize import Barrier
    from pathlib import Path
    from pytest import MonkeyPatch
    from zato.common.typing_ import any_, strlist

    any_ = any_
    Barrier = Barrier
    MonkeyPatch = MonkeyPatch
    Path = Path
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The workers are forked, as the arbiter forks them
    Context = get_context('fork')

    Sub_Key = 'sk-pull'
    Topic_Name = 'pull.test.topic'

    # How many messages the topic holds, and how many of them one pull leases at most
    Message_Count = 60
    Max_Messages = 3
    Max_Len = 1_000_000

    # How long a pull leases its rows, in milliseconds, which outlasts the test
    Lease_Ms = 600_000

    # How many workers pull at the same time
    Worker_Count = 2

    # How long a caller waits for the reply of the writer, and how long the test waits for a process, in seconds
    Deadline = 20.0
    Join_Timeout = 60.0

# ################################################################################################################################
# ################################################################################################################################

def _run_in_process(func:'any_', *args:'any_') -> 'None':
    """ Runs a function in a forked process, which reports an exception on its output and exits with status 1.
    """
    exit_code = 1

    try:
        gevent.reinit()

        func(*args)
        exit_code = 0

    except BaseException:
        traceback.print_exc()

    finally:
        os._exit(exit_code)

# ################################################################################################################################

def _start_process(func:'any_', *args:'any_') -> 'any_':
    out = ModuleCtx.Context.Process(target=_run_in_process, args=(func, *args))
    out.start()
    return out

# ################################################################################################################################

def _publish() -> 'None':
    """ Subscribes the key to the topic and publishes the messages, each from its own transaction.
    """
    engine = get_pubsub_engine()

    with engine.begin() as connection:
        _ = connection.execute(topic_sub_table.insert(), {'sub_key': ModuleCtx.Sub_Key, 'topic_name': ModuleCtx.Topic_Name})

    writer = PubSubWriter()

    for index in range(ModuleCtx.Message_Count):
        message_values = new_message_values(f'msg-{index}')
        message_values['topic_name'] = ModuleCtx.Topic_Name

        writer.publish(new_pending_publication(message_values))

# ################################################################################################################################

def _ignore_reconnect() -> 'None':
    """ The test has no wake counters to increment after the writer accepts a new connection.
    """

# ################################################################################################################################

def _pull(barrier:'Barrier', writer_address:'str', output_path:'str') -> 'None':
    """ Pulls the messages of the key until a pull returns none, and writes the identifiers it received.
    """
    engine = get_pubsub_engine()
    clock = get_database_clock()

    # A worker of a server with a writer process leases through it, a worker on PostgreSQL leases in its own process
    if writer_address:
        _ = start_writer_client(writer_address, ModuleCtx.Deadline, _ignore_reconnect)

    msg_ids:'strlist' = []

    # The workers pull at the same time ..
    _ = barrier.wait(ModuleCtx.Join_Timeout)

    while True:
        now_ms = clock.now_ms()
        leased_until_ms = now_ms + ModuleCtx.Lease_Ms

        rows, _ = lease(engine, ModuleCtx.Sub_Key, ModuleCtx.Max_Messages, ModuleCtx.Max_Len, now_ms, leased_until_ms)

        # .. until every message is leased to one of them.
        if not rows:
            break

        for row in rows:
            msg_ids.append(row.msg_id)

    with open(output_path, 'w') as output:
        _ = output.write(dumps(msg_ids))

# ################################################################################################################################

def _serve_writer(listen_fd:'int') -> 'None':
    server = WriterServer(listen_fd, WriterHandlers().get_handlers())
    server.serve_forever()

# ################################################################################################################################
# ################################################################################################################################

def _run_pulls(tmp_path:'Path', writer_address:'str') -> 'None':
    """ Publishes the messages of the key, lets two workers pull the key at the same time, and confirms that each message
    is leased to exactly one of them.
    """
    # The topic holds the messages of the key ..
    process = _start_process(_publish)
    process.join(ModuleCtx.Join_Timeout)

    assert process.exitcode == 0

    # .. two workers pull the key at the same time ..
    barrier = ModuleCtx.Context.Barrier(ModuleCtx.Worker_Count)
    output_paths:'strlist' = []
    processes = []

    for index in range(ModuleCtx.Worker_Count):
        output_path = str(tmp_path / f'pulled-{index}.json')
        output_paths.append(output_path)

        process = _start_process(_pull, barrier, writer_address, output_path)
        processes.append(process)

    for process in processes:
        process.join(ModuleCtx.Join_Timeout)
        assert process.exitcode == 0

    # .. and each message is leased to exactly one of them.
    pulled:'list[strlist]' = []

    for output_path in output_paths:
        with open(output_path) as output:
            msg_ids = loads(output.read())
            pulled.append(msg_ids)

    first, second = pulled
    expected:'strlist' = []

    for index in range(ModuleCtx.Message_Count):
        expected.append(f'msg-{index}')

    assert set(first).isdisjoint(second)
    assert sorted(first + second) == sorted(expected)

    # Both workers received messages, so their pulls ran at the same time
    assert first
    assert second

# ################################################################################################################################

def test_concurrent_pulls_of_one_key_receive_disjoint_messages_on_sqlite(
    tmp_path:'Path',
    monkeypatch:'MonkeyPatch',
    ) -> 'None':

    monkeypatch.setenv(ConfigCtx.Env_Path, str(tmp_path / 'pubsub.db'))

    # A server of several workers on SQLite serves their leases from its writer process
    writer_address = str(tmp_path / 'writer.sock')
    listener = new_listening_socket(writer_address)

    writer_process = _start_process(_serve_writer, listener.fileno())
    listener.close()

    _run_pulls(tmp_path, writer_address)

    writer_process.kill()
    writer_process.join(ModuleCtx.Join_Timeout)

# ################################################################################################################################

def test_concurrent_pulls_of_one_key_receive_disjoint_messages_on_postgresql(tmp_path:'Path') -> 'None':

    # A server on PostgreSQL runs no writer process, so each worker leases in its own process
    database = start_pubsub_database('pull', PubSubDBMode.PostgreSQL)

    try:
        with pubsub_db_env(database.env):
            _run_pulls(tmp_path, '')

    finally:
        stop_pubsub_database(database)

# ################################################################################################################################
# ################################################################################################################################
