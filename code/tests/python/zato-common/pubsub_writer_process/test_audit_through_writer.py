# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from json import loads

# gevent
import gevent

# SQLAlchemy
from sqlalchemy import select

# Zato
from writer_common import run_in_child
from zato.common.audit_log.api import AuditLog, event_attr_table, event_body_table, event_table, get_audit_engine
from zato.common.audit_log.attachment import build_attachment
from zato.common.audit_log.common import AuditBody
from zato.common.pubsub.writer_process.frames import ItemKind
from zato.common.pubsub.writer_process.handlers import WriterHandlers
from zato.common.pubsub.writer_process.remote import start_writer_client, stop_writer_client
from zato.common.pubsub.writer_process.server import new_listening_socket, WriterServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from pytest import MonkeyPatch
    from zato.common.typing_ import any_, anydict, anylist, intlist

    any_ = any_
    anydict = anydict
    anylist = anylist
    intlist = intlist
    MonkeyPatch = MonkeyPatch
    Path = Path

# ################################################################################################################################
# ################################################################################################################################

# The variable that holds the path of the SQLite audit database
_env_db_name = 'Zato_Audit_Log_DB_Name'

# How long a caller waits for a reply, in seconds
_deadline = 20.0

# How many workers write their events at the same time
_concurrent_writers = 8

_server_name = 'server1'
_source = 'test'
_event_type = 'request'
_attachment_content = b'\x00\x01attachment bytes\xff'

# ################################################################################################################################
# ################################################################################################################################

def _ignore_reconnect() -> 'None':
    """ The test has no wake counters to increment after the writer accepts a new connection.
    """

# ################################################################################################################################

def _write_through_writer_process(tmp_dir:'str') -> 'None':

    # The writer serves the workers, and each audit item it receives is counted ..
    handlers = WriterHandlers()
    handler_map = handlers.get_handlers()

    received:'intlist' = []

    def _count_audit(body:'anydict') -> 'anydict':
        received.append(len(body['events']))
        out = handlers.audit(body)
        return out

    handler_map[ItemKind.Audit] = _count_audit

    address = os.path.join(tmp_dir, 'writer.sock')
    listener = new_listening_socket(address)

    server = WriterServer(os.dup(listener.fileno()), handler_map)
    server_greenlet = gevent.spawn(server.serve_forever)

    _ = start_writer_client(address, _deadline, _ignore_reconnect)

    audit_log = AuditLog(_server_name, flush_max_size=1)

    # .. an event with attributes of several types, a body and an attachment is written through the writer ..
    attachment = build_attachment('report.bin', 'application/octet-stream', _attachment_content)

    first_id = audit_log.insert(_source, _event_type, 'object-1', cid='cid-1', attrs={'count': 3, 'flag': True, 'name': 'abc'},
        bodies={AuditBody.Request: 'request body'}, attachments=[attachment])

    assert first_id
    assert received == [1]

    # .. an event that links to the first one is written too, with its parent ..
    second_id = audit_log.insert(_source, _event_type, 'object-2', parents=[first_id])

    assert second_id
    assert second_id != first_id

    # .. concurrent workers each receive the ID of their own event ..
    returned:'intlist' = []

    def _insert(index:'int') -> 'None':
        event_id = audit_log.insert(_source, _event_type, f'concurrent-{index}')
        assert event_id
        returned.append(event_id)

    greenlets:'anylist' = []

    for index in range(_concurrent_writers):
        greenlets.append(gevent.spawn(_insert, index))

    _ = gevent.joinall(greenlets, raise_error=True)

    assert len(set(returned)) == _concurrent_writers

    # .. and the database holds every event, with the values that the workers built.
    engine = get_audit_engine()

    with engine.connect() as connection:

        rows = connection.execute(select(event_table.c.id, event_table.c.object_name, event_table.c.server_name,
            event_table.c.cid, event_table.c.event_time)).all()

        by_id:'anydict' = {}

        for row in rows:
            by_id[row.id] = row

        assert by_id[first_id].object_name == 'object-1'
        assert by_id[first_id].server_name == _server_name
        assert by_id[first_id].cid == 'cid-1'
        assert by_id[first_id].event_time is not None

        for event_id in returned:
            assert event_id in by_id

        attr_rows = connection.execute(select(event_attr_table.c.name, event_attr_table.c.value,
            event_attr_table.c.value_number).where(event_attr_table.c.event_id == first_id)).all()

        attrs:'anydict' = {}

        for row in attr_rows:
            attrs[row.name] = (row.value, row.value_number)

        assert attrs['count'] == ('3', 3)
        assert attrs['flag'] == ('True', None)
        assert attrs['name'] == ('abc', None)

        body_rows = connection.execute(select(event_body_table.c.kind, event_body_table.c.data,
            event_body_table.c.content).where(event_body_table.c.event_id == first_id)).all()

        bodies:'anydict' = {}

        for row in body_rows:
            bodies[row.kind] = row

        assert bodies[AuditBody.Request].data == 'request body'
        assert bodies[AuditBody.Attachment].content == _attachment_content
        assert loads(bodies[AuditBody.Attachment].data)['filename'] == 'report.bin'

    # Without its connection to a writer process, the worker writes in its own process
    stop_writer_client()

    count_before = len(received)
    local_id = audit_log.insert(_source, _event_type, 'object-local')

    assert local_id
    assert len(received) == count_before

    gevent.kill(server_greenlet)
    server.close()
    listener.close()

# ################################################################################################################################
# ################################################################################################################################

def test_the_audit_events_of_workers_are_written_by_the_writer_process(tmp_path:'Path', monkeypatch:'MonkeyPatch') -> 'None':
    monkeypatch.setenv(_env_db_name, str(tmp_path / 'audit.db'))

    run_in_child(_write_through_writer_process, (str(tmp_path),))

# ################################################################################################################################
# ################################################################################################################################
