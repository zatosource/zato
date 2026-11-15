# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# gevent
import gevent
import pytest

# Zato
from writer_common import new_message_values, run_in_child, Topic_Name
from zato.common.pubsub.sql.clock import get_database_clock
from zato.common.pubsub.sql.config import get_pubsub_engine, ModuleCtx
from zato.common.pubsub.sql.schema import topic_sub_table
from zato.common.pubsub.sql.writes import new_pending_ack, new_pending_publication, PubSubDuplicateMsgID, PubSubWriter
from zato.common.pubsub.writer_process.handlers import WriterHandlers
from zato.common.pubsub.writer_process.remote import lease, new_pubsub_writer, RemotePubSubWriter, start_writer_client, \
    stop_writer_client
from zato.common.pubsub.writer_process.server import new_listening_socket, WriterServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from pytest import MonkeyPatch

    MonkeyPatch = MonkeyPatch
    Path = Path

# ################################################################################################################################
# ################################################################################################################################

# How long a caller waits for a reply, in seconds
_deadline = 20.0

# How long a pull leases its rows, in milliseconds
_lease_ms = 30_000

# How many messages and bytes one pull receives at most
_max_messages = 10
_max_len = 1_000_000

_first_key = 'sk-1'
_second_key = 'sk-2'

# ################################################################################################################################
# ################################################################################################################################

def _ignore_reconnect() -> 'None':
    """ The test has no wake counters to increment after the writer accepts a new connection.
    """

# ################################################################################################################################

def _write_through_writer_process(tmp_dir:'str') -> 'None':

    # The topic has two subscribers ..
    engine = get_pubsub_engine()

    with engine.begin() as connection:
        _ = connection.execute(topic_sub_table.insert(), [
            {'sub_key': _first_key, 'topic_name': Topic_Name},
            {'sub_key': _second_key, 'topic_name': Topic_Name},
        ])

    # .. the writer serves the worker, which connects to it ..
    address = os.path.join(tmp_dir, 'writer.sock')
    listener = new_listening_socket(address)

    server = WriterServer(os.dup(listener.fileno()), WriterHandlers().get_handlers())
    server_greenlet = gevent.spawn(server.serve_forever)

    _ = start_writer_client(address, _deadline, _ignore_reconnect)
    writer = new_pubsub_writer()

    assert isinstance(writer, RemotePubSubWriter)

    # .. a publication returns the subscribers it was published to ..
    message_values = new_message_values('msg-1')

    pending = new_pending_publication(message_values)
    writer.publish(pending)

    assert sorted(pending.subscriber_keys) == [_first_key, _second_key]

    # .. the same publication again is repeated, with no subscribers to wake ..
    pending = new_pending_publication(message_values)
    writer.publish(pending)

    assert pending.subscriber_keys == []

    # .. a different message under the identifier fails its publisher, as in one process ..
    different_values = new_message_values('msg-1')
    different_values['payload_crc32'] = 2

    with pytest.raises(PubSubDuplicateMsgID):
        writer.publish(new_pending_publication(different_values))

    # .. a pull of the first subscriber leases the message for its first time ..
    now_ms = get_database_clock().now_ms()
    rows, attempts = lease(engine, _first_key, _max_messages, _max_len, now_ms, now_ms + _lease_ms)

    assert len(rows) == 1
    assert rows[0].msg_id == 'msg-1'
    assert rows[0].payload == 'payload'
    assert attempts == {rows[0].id: 1}

    # .. and the acknowledgements of both subscribers remove one row each, the last one delivering the message fully.
    first_ack = new_pending_ack(_first_key, ['msg-1'], None)
    writer.ack(first_ack)

    assert first_ack.removed_count == 1
    assert first_ack.fully_delivered_count == 0

    second_ack = new_pending_ack(_second_key, ['msg-1'], None)
    writer.ack(second_ack)

    assert second_ack.removed_count == 1
    assert second_ack.fully_delivered_count == 1

    # Without its connection to a writer process, the worker writes in its own process
    stop_writer_client()

    assert isinstance(new_pubsub_writer(), PubSubWriter)

    gevent.kill(server_greenlet)
    server.close()
    listener.close()

# ################################################################################################################################
# ################################################################################################################################

def test_the_items_of_a_worker_are_written_by_the_writer_process(tmp_path:'Path', monkeypatch:'MonkeyPatch') -> 'None':
    monkeypatch.setenv(ModuleCtx.Env_Path, str(tmp_path / 'pubsub.db'))

    run_in_child(_write_through_writer_process, (str(tmp_path),))

# ################################################################################################################################
# ################################################################################################################################
