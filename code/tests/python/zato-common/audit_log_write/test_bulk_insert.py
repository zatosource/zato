# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy

# Zato
from support import Backend_PostgreSQL, Event_Time, insert_seed_event, new_batch, read_rows, record_statements, \
    Server_Name
from zato.common.audit_log.api import event_attr_table, event_body_table, event_link_table, event_table, \
    get_audit_engine, AuditLog

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.sql.schema import Table
    from zato.common.typing_ import anylist, intdict, stranydict, strtuple

    anylist = anylist
    intdict = intdict
    stranydict = stranydict
    strtuple = strtuple
    Table = Table

# ################################################################################################################################
# ################################################################################################################################

# How many events the batch of each test holds
_event_count = 50

# The columns that differ between two writes of the same events by design
_event_skipped_columns = ('id', 'commit_id')
_child_skipped_columns = ('id',)

# The statements that write one batch on each database, as their verbs and tables
_postgresql_statements = [
    ('INSERT', 'event'),
    ('COPY', 'event_attr'),
    ('COPY', 'event_body'),
    ('COPY', 'event_link'),
]

_sqlite_statements = [
    ('INSERT', 'event'),
    ('SELECT', 'event'),
    ('INSERT', 'event_attr'),
    ('INSERT', 'event_body'),
    ('INSERT', 'event_link'),
]

# ################################################################################################################################
# ################################################################################################################################

def _without(row:'stranydict', skipped:'strtuple') -> 'stranydict':
    """ Returns the values of a row without the columns given.
    """
    out:'stranydict' = {}

    for name, value in row.items():
        if name not in skipped:
            out[name] = value

    return out

# ################################################################################################################################

def _event_rows() -> 'anylist':
    """ The event rows of both writes, without the seed event and without the columns that differ by design.
    """
    out:'anylist' = []

    for row in read_rows(event_table):
        if row['cid'] != 'cid-seed':
            values = _without(row, _event_skipped_columns)
            out.append(values)

    return out

# ################################################################################################################################

def _child_rows(table:'Table', event_column:'str', positions:'intdict') -> 'anylist':
    """ The rows of a table that refers to events, with each event id replaced by the position of its event.
    """
    out:'anylist' = []

    for row in read_rows(table):
        values = _without(row, _child_skipped_columns)

        event_id = values[event_column]
        values[event_column] = positions[event_id]

        out.append(values)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_one_statement_per_table(audit_backend:'str') -> 'None':
    """ A batch of events is written with one statement per table, plus the select of the event ids on SQLite.
    """
    audit_log = AuditLog(Server_Name)
    seed_event_id = insert_seed_event(audit_log)

    batch = new_batch(audit_log, _event_count, seed_event_id)
    engine = get_audit_engine()

    with record_statements(engine) as recorder:
        last_event_id = audit_log._write_batch(batch)

    if audit_backend == Backend_PostgreSQL:
        expected = _postgresql_statements
    else:
        expected = _sqlite_statements

    assert recorder.statements == expected
    assert recorder.commit_count == 1

    # Each event received its own id, in the order of the batch ..
    event_ids:'anylist' = []

    for pending in batch:
        event_ids.append(pending.event_id)

    assert last_event_id == event_ids[-1]
    assert event_ids == sorted(event_ids)
    assert len(set(event_ids)) == _event_count

    # .. which is the id of the row with its own cid.
    for row in read_rows(event_table):
        if row['cid'] != 'cid-seed':
            index = event_ids.index(row['id'])
            assert row['cid'] == f'cid-{index}'

# ################################################################################################################################

def test_same_rows_as_single_event_batches(audit_backend:'str') -> 'None':
    """ The rows a batch writes are identical in every column to the rows of the same events written one at a time.
    """
    seed_audit_log = AuditLog(Server_Name)
    seed_event_id = insert_seed_event(seed_audit_log)

    # The same events, built by two writers with sequences of their own ..
    batch_audit_log = AuditLog(Server_Name)
    single_audit_log = AuditLog(Server_Name)

    batch = new_batch(batch_audit_log, _event_count, seed_event_id)
    singles = new_batch(single_audit_log, _event_count, seed_event_id)

    # .. are written in one batch and one at a time ..
    _ = batch_audit_log._write_batch(batch)

    for pending in singles:
        _ = single_audit_log._write_batch([pending])

    # .. and each event id stands for the position of its event within its write.
    positions:'intdict' = {seed_event_id: -1}

    for index, pending in enumerate(batch):
        positions[pending.event_id] = index

    for index, pending in enumerate(singles):
        positions[pending.event_id] = index

    # The event rows of the two writes are identical, the internal data included ..
    event_rows = _event_rows()

    batch_events = event_rows[:_event_count]
    single_events = event_rows[_event_count:]

    assert len(single_events) == _event_count
    assert batch_events == single_events
    assert batch_events[0]['internal_data'] == '{"digest": "sha256-0"}'
    assert batch_events[0]['event_time'] == Event_Time

    # .. and so are the rows of each table that refers to them.
    batch_ids:'anylist' = []

    for pending in batch:
        batch_ids.append(pending.event_id)

    for table, event_column in ((event_attr_table, 'event_id'), (event_body_table, 'event_id'),
        (event_link_table, 'child_event_id')):

        batch_rows:'anylist' = []
        single_rows:'anylist' = []

        for row in read_rows(table):
            if row[event_column] in batch_ids:
                batch_rows.append(row)
            else:
                single_rows.append(row)

        assert batch_rows
        assert len(batch_rows) == len(single_rows)

        batch_child_rows = _child_rows(table, event_column, positions)

        batch_values = batch_child_rows[:len(batch_rows)]
        single_values = batch_child_rows[len(batch_rows):]

        assert batch_values == single_values, table.name

# ################################################################################################################################

def test_batch_of_copies_is_written_once_each(audit_backend:'str') -> 'None':
    """ Events written in one batch never share an id, even when all their values are the same.
    """
    audit_log = AuditLog(Server_Name)
    seed_event_id = insert_seed_event(audit_log)

    template = new_batch(audit_log, 1, seed_event_id)
    first = template[0]

    batch = [first]

    for _ in range(_event_count - 1):
        copy = deepcopy(first)
        batch.append(copy)

    _ = audit_log._write_batch(batch)

    event_ids:'anylist' = []

    for pending in batch:
        event_ids.append(pending.event_id)

    assert len(set(event_ids)) == _event_count
    assert len(read_rows(event_table)) == _event_count + 1

# ################################################################################################################################
# ################################################################################################################################
