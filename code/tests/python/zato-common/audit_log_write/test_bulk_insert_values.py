# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The values that the bulk insert of audit events writes to each table, column by column, for batches of every size
# that the insert paths of SQLite and PostgreSQL tell apart.

# stdlib
import zlib
from typing import NamedTuple

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import LargeBinary, select, String, Text, type_coerce

# Zato
from support import Attachment_Content, Backend_SQLite, Event_Minute, Event_Time, get_event_specs, insert_seed_event, \
    Long_Note, MLLP_Object_Name, new_value_batch, Payload_Non_ASCII, Pub_Time, read_rows, read_value_events, Server_Name, \
    Stored_Attr_Value_Length
from zato.common.audit_log.api import event_attr_table, event_body_table, event_link_table, event_table, AuditBody, \
    AuditEvent, AuditLink, AuditLog, AuditSource
from zato.common.audit_log.common import event_count_table, event_open_table, event_payload_table
from zato.common.audit_log.export.api import set_audit_export
from zato.common.audit_log.search import search_events
from zato.common.db_env.database import get_database_engine
from zato.common.test.audit_log_ import RecordingAuditExport

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from support import event_spec_list, EventSpec
    from zato.common.audit_log.pending import pending_event_list
    from zato.common.typing_ import any_, anydict, anylist, intlist, stranydict

    any_ = any_
    anydict = anydict
    anylist = anylist
    event_spec_list = event_spec_list
    EventSpec = EventSpec
    intlist = intlist
    pending_event_list = pending_event_list
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The batch sizes - a single event, the largest batch below the size from which PostgreSQL uses COPY, that size itself
# and a batch of many events
_batch_sizes = (1, 15, 16, 50)

# The batch size of the tests that do not depend on the insert path
_event_count = 16

# The zlib level that SQLite stores text with
_compression_level = 1

# The text of the body row of the attachment of an event
_attachment_data = '{"filename": "invoice.pdf", "content_type": "application/pdf", "size": 34, "is_content_kept": true}'

# The text form in which SQLite stores Event_Time and Pub_Time
_sqlite_event_time = '2026-10-29 12:00:00.123456'
_sqlite_pub_time   = '2026-10-29 11:59:30.654321'

# ################################################################################################################################
# ################################################################################################################################

class ValueWrite(NamedTuple):
    """ The specs of the value events of one batch, the events as written, and the id of the seed event.
    """
    specs: 'event_spec_list'
    batch: 'pending_event_list'
    seed_event_id: int

# ################################################################################################################################
# ################################################################################################################################

def _write_value_batch(event_count:'int') -> 'ValueWrite':
    """ Writes the value events of a batch of the given size, after the seed event they link to, in one call.
    """
    audit_log = AuditLog(Server_Name)
    seed_event_id = insert_seed_event(audit_log)

    specs = get_event_specs(event_count)
    batch = new_value_batch(audit_log, specs, seed_event_id)

    audit_log.write_pending(batch)

    out = ValueWrite(specs, batch, seed_event_id)
    return out

# ################################################################################################################################

def _payload_ids_by_digest() -> 'anydict':
    """ Returns the id of each stored payload by its digest.
    """
    out:'anydict' = {}

    for row in read_rows(event_payload_table):
        out[row['digest']] = row['id']

    return out

# ################################################################################################################################

def _event_ids(batch:'pending_event_list') -> 'intlist':
    """ Returns the ids the events of a batch received, in the order of the batch.
    """
    out:'intlist' = []

    for pending in batch:
        out.append(pending.event_id)

    return out

# ################################################################################################################################

def _expected_event_row(spec:'EventSpec', payload_ids:'anydict') -> 'stranydict':
    """ Returns every column, apart from the id, that the row of the event of a spec is expected to hold.
    """
    if spec.payload.digest:
        payload_id = payload_ids[spec.payload.digest]
    else:
        payload_id = None

    out:'stranydict' = {
        'cid': spec.cid,
        'cid_sequence': spec.cid_sequence,
        'source': spec.source,
        'event_type': spec.event_type,
        'object_name': spec.object_name,
        'msg_id': spec.msg_id,
        'correl_id': spec.correl_id,
        'ext_client_id': spec.ext_client_id,
        'pub_time': spec.pub_time,
        'event_time': Event_Time,
        'server_name': Server_Name,
        'endpoint': spec.endpoint,
        'sub_key': spec.sub_key,
        'size': spec.size,
        'priority': spec.priority,
        'outcome': spec.outcome,
        'application_outcome': spec.application_outcome,
        'classification': spec.classification,
        'status': spec.status,
        'duration_ms': spec.duration_ms,
        'payload_id': payload_id,
        'internal_data': spec.internal_data,
    }

    return out

# ################################################################################################################################

def _expected_attr(value:'any_') -> 'tuple[str, float | None]':
    """ Returns the text and the number that an attribute of the given value is expected to be stored with.
    """
    if value is True:
        out = ('True', None)

    elif value is False:
        out = ('False', None)

    elif isinstance(value, int):
        out = (f'{value}', float(value))

    elif isinstance(value, float):
        out = (f'{value}', value)

    elif value == Long_Note:
        out = (Long_Note[:Stored_Attr_Value_Length], None)

    # .. any other attribute of the specs is text that fits in a stored value.
    else:
        out = (value, None)

    return out

# ################################################################################################################################

def _rows_by_event(table:'any_', event_column:'str') -> 'anydict':
    """ Returns the rows of a table that refers to events, by the id of the event, each list in the order of the ids.
    """
    out:'anydict' = {}

    for row in read_rows(table):
        event_id = row[event_column]

        if event_id not in out:
            out[event_id] = []

        out[event_id].append(row)

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('event_count', _batch_sizes)
def test_event_rows(audit_backend:'str', event_count:'int') -> 'None':
    """ Each event row holds the values its event was created with, under the id the event received,
    in the order of the batch.
    """
    written = _write_value_batch(event_count)

    rows = read_value_events()
    payload_ids = _payload_ids_by_digest()
    event_ids = _event_ids(written.batch)

    assert len(rows) == event_count
    assert event_ids == sorted(event_ids)
    assert len(set(event_ids)) == event_count

    for spec, row, event_id in zip(written.specs, rows, event_ids):

        assert row['id'] == event_id, spec.index

        values = dict(row)
        del values['id']

        expected = _expected_event_row(spec, payload_ids)
        assert values == expected, spec.index

# ################################################################################################################################

@pytest.mark.parametrize('event_count', _batch_sizes)
def test_payload_rows(audit_backend:'str', event_count:'int') -> 'None':
    """ Each distinct payload of a batch is stored once, under its digest, with its text and its search text,
    and an empty payload is not stored.
    """
    written = _write_value_batch(event_count)

    # The seed event has a payload of its own ..
    seed_rows = read_rows(event_table)[0]
    seed_payload_id = seed_rows['payload_id']

    expected:'anylist' = []

    for spec in written.specs:
        if spec.payload.digest:
            item = (spec.payload.digest, spec.payload.text, spec.payload.search_text)
            if item not in expected:
                expected.append(item)

    # .. and the others are those of the value events.
    stored:'anylist' = []

    for row in read_rows(event_payload_table):
        if row['id'] != seed_payload_id:
            item = (row['digest'], row['data'], row['search_text'])
            stored.append(item)

    assert sorted(stored) == sorted(expected)

# ################################################################################################################################

def test_payloads_shared_across_batches(audit_backend:'str') -> 'None':
    """ The events of a later batch with the payloads of an earlier one refer to the payload rows of the earlier batch,
    and no payload is stored again.
    """
    first = _write_value_batch(_event_count)
    first_payload_rows = read_rows(event_payload_table)

    second_audit_log = AuditLog(Server_Name)
    second_batch = new_value_batch(second_audit_log, first.specs, first.seed_event_id)
    second_audit_log.write_pending(second_batch)

    assert read_rows(event_payload_table) == first_payload_rows

    rows = read_value_events()
    first_rows = rows[:_event_count]
    second_rows = rows[_event_count:]

    assert len(second_rows) == _event_count

    for first_row, second_row in zip(first_rows, second_rows):
        assert second_row['payload_id'] == first_row['payload_id']

# ################################################################################################################################

def test_stored_form(audit_backend:'str') -> 'None':
    """ SQLite stores the text of payloads and bodies compressed with zlib at its fastest level, and the times
    as text, while PostgreSQL stores the text as it is given.
    """
    written = _write_value_batch(_event_count)
    engine = get_database_engine()

    is_sqlite = audit_backend == Backend_SQLite

    stored_type:'any_'

    if is_sqlite:
        stored_type = LargeBinary
    else:
        stored_type = Text

    payload_query = select(event_payload_table.c.digest, type_coerce(event_payload_table.c.data, stored_type))
    body_query = select(event_body_table.c.event_id, event_body_table.c.kind, type_coerce(event_body_table.c.data, stored_type))
    body_query = body_query.where(event_body_table.c.kind != AuditBody.Attachment)

    time_query = select(event_table.c.id, type_coerce(event_table.c.event_time, String),
        type_coerce(event_table.c.pub_time, String))

    with engine.connect() as connection:
        stored_payloads = connection.execute(payload_query).all()
        stored_bodies = connection.execute(body_query).all()
        stored_times = connection.execute(time_query).all()

    # The text of each payload and of each body ..
    texts_by_digest:'anydict' = {}

    for spec in written.specs:
        texts_by_digest[spec.payload.digest] = spec.payload.text

    bodies_by_key:'anydict' = {}

    for spec, pending in zip(written.specs, written.batch):
        for kind, body_data in spec.bodies.items():
            bodies_by_key[pending.event_id, kind] = body_data

    assert stored_bodies

    # .. is stored compressed on SQLite and as it is on PostgreSQL.
    for digest, stored in stored_payloads:
        if digest in texts_by_digest:
            text = texts_by_digest[digest]

            if is_sqlite:
                assert stored == zlib.compress(text.encode('utf8'), _compression_level), digest
            else:
                assert stored == text, digest

    for event_id, kind, stored in stored_bodies:
        text = bodies_by_key[event_id, kind]

        if is_sqlite:
            assert stored == zlib.compress(text.encode('utf8'), _compression_level), (event_id, kind)
        else:
            assert stored == text, (event_id, kind)

    # The times of the value events are stored by SQLite in the text form of SQLAlchemy.
    if is_sqlite:
        pub_times:'anydict' = {}

        for spec, pending in zip(written.specs, written.batch):
            if spec.pub_time == Pub_Time:
                pub_times[pending.event_id] = _sqlite_pub_time
            else:
                pub_times[pending.event_id] = None

        for event_id, event_time, pub_time in stored_times:
            if event_id in pub_times:
                assert event_time == _sqlite_event_time, event_id
                assert pub_time == pub_times[event_id], event_id

# ################################################################################################################################

@pytest.mark.parametrize('event_count', _batch_sizes)
def test_attr_rows(audit_backend:'str', event_count:'int') -> 'None':
    """ Each attribute is stored as text, cut to the length of a stored value, and a number also as a number,
    while a boolean is stored as text alone.
    """
    written = _write_value_batch(event_count)
    attr_rows = _rows_by_event(event_attr_table, 'event_id')

    for spec, pending in zip(written.specs, written.batch):

        expected:'anydict' = {}

        for name, value in spec.attrs.items():
            expected[name] = _expected_attr(value)

        stored:'anydict' = {}

        if pending.event_id in attr_rows:
            for row in attr_rows[pending.event_id]:
                stored[row['name']] = (row['value'], row['value_number'])

        assert stored == expected, spec.index

# ################################################################################################################################

@pytest.mark.parametrize('event_count', _batch_sizes)
def test_body_rows(audit_backend:'str', event_count:'int') -> 'None':
    """ Each body and each attachment of an event is a body row stamped with the time of its event,
    with the metadata of an attachment as its text and the bytes of the attachment as its content.
    """
    written = _write_value_batch(event_count)
    body_rows = _rows_by_event(event_body_table, 'event_id')

    for spec, pending in zip(written.specs, written.batch):

        expected:'anylist' = []

        for kind, body_data in spec.bodies.items():
            expected.append((kind, Event_Time, body_data, None))

        if spec.has_attachment:
            expected.append((AuditBody.Attachment, Event_Time, _attachment_data, Attachment_Content))

        stored:'anylist' = []

        if pending.event_id in body_rows:
            for row in body_rows[pending.event_id]:
                stored.append((row['kind'], row['event_time'], row['data'], row['content']))

        assert sorted(stored) == sorted(expected), spec.index

# ################################################################################################################################

@pytest.mark.parametrize('event_count', _batch_sizes)
def test_link_rows(audit_backend:'str', event_count:'int') -> 'None':
    """ Each link of an event to its parent is a link row of the type the event was created with.
    """
    written = _write_value_batch(event_count)
    link_rows = _rows_by_event(event_link_table, 'child_event_id')

    for spec, pending in zip(written.specs, written.batch):

        expected:'anylist' = []

        if spec.has_parent:
            expected.append((written.seed_event_id, AuditLink.Batch_Item_Of))

        stored:'anylist' = []

        if pending.event_id in link_rows:
            for row in link_rows[pending.event_id]:
                stored.append((row['parent_event_id'], row['link_type']))

        assert stored == expected, spec.index

# ################################################################################################################################

@pytest.mark.parametrize('event_count', _batch_sizes)
def test_trigger_rows(audit_backend:'str', event_count:'int') -> 'None':
    """ The triggers count the events of the minute of Event_Time by their key columns, and each message sent
    over MLLP is an open exchange until the acknowledgment of its message arrives.
    """
    written = _write_value_batch(event_count)

    # Each event adds one to the count of its key ..
    expected_counts:'anydict' = {}

    for spec in written.specs:
        key = (spec.source, spec.object_name, spec.event_type, spec.outcome, spec.status)

        if key not in expected_counts:
            expected_counts[key] = 0

        expected_counts[key] += 1

    # .. which the rows of the minute add up to, whether the database writes one row per event or per statement ..
    stored_counts:'anydict' = {}

    for row in read_rows(event_count_table):
        if row['period_start'] == Event_Minute:
            key = (row['source'], row['object_name'], row['event_type'], row['outcome'], row['status'])

            if key not in stored_counts:
                stored_counts[key] = 0

            stored_counts[key] += row['event_count']

    assert stored_counts == expected_counts

    # .. and the messages sent are open, apart from the first one in a batch that acknowledges it.
    expected_open:'anylist' = []

    for spec, pending in zip(written.specs, written.batch):
        if spec.event_type == AuditEvent.Message_Sent:
            if spec.index > 0 or event_count == 1:
                expected_open.append((pending.event_id, AuditSource.MLLP_Outgoing, spec.msg_id, MLLP_Object_Name))

    stored_open:'anylist' = []

    for row in read_rows(event_open_table):
        stored_open.append((row['event_id'], row['source'], row['msg_id'], row['object_name']))

    assert sorted(stored_open) == sorted(expected_open)

# ################################################################################################################################

def test_search(audit_backend:'str') -> 'None':
    """ The free-text search finds the events by a word of their payload and by the value of an attribute
    of their source, the latter with every event that shares the cid of the event of that value.
    """
    written = _write_value_batch(_event_count)
    engine = get_database_engine()

    ids_by_index:'anydict' = {}

    for spec, pending in zip(written.specs, written.batch):
        ids_by_index[spec.index] = pending.event_id

    # A word of a payload finds the events of the source that have that payload ..
    expected_by_payload:'anylist' = []

    for spec in written.specs:
        if spec.source == AuditSource.MLLP_Outgoing:
            if spec.payload == Payload_Non_ASCII:
                expected_by_payload.append(ids_by_index[spec.index])

    found = search_events(engine, source=AuditSource.MLLP_Outgoing, query='zamówienie', page_size=100)

    found_ids:'anylist' = []

    for row in found:
        found_ids.append(row['id'])

    assert sorted(found_ids) == sorted(expected_by_payload)
    assert len(found_ids) == 3

    # .. and the value of an attribute finds the event that has it.
    found = search_events(engine, source=AuditSource.MLLP_Outgoing, query='MRN-0004', page_size=100)

    found_ids = []

    for row in found:
        found_ids.append(row['id'])

    assert found_ids == [ids_by_index[4]]

# ################################################################################################################################

@pytest.mark.parametrize('event_count', _batch_sizes)
def test_export(audit_backend:'str', event_count:'int') -> 'None':
    """ After the commit, the export receives every event of the batch with the id it received, its values
    and whether its payload leaves the process.
    """
    export = RecordingAuditExport()
    set_audit_export(export)

    try:
        written = _write_value_batch(event_count)
    finally:
        set_audit_export(None)

    # The seed event is the first one the export received ..
    value_events = export.events[1:]

    assert len(value_events) == event_count

    # .. and the value events follow it, in the order of the batch.
    for spec, pending, event in zip(written.specs, written.batch, value_events):
        assert event.event_id == pending.event_id, spec.index
        assert event.is_export_payload_active == spec.is_export_payload_active, spec.index
        assert event.values['msg_id'] == spec.msg_id, spec.index
        assert event.values['cid_sequence'] == spec.cid_sequence, spec.index
        assert event.values['data'] == spec.payload.text, spec.index
        assert event.values['event_time'] == Event_Time, spec.index

# ################################################################################################################################
# ################################################################################################################################
