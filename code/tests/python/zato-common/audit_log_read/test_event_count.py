# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta
from random import Random

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from support import actual_counts, Base_Time, Connection_Names, count_filter_sets, drop_read_schema, expected_counts, \
    expected_open_ids, insert_rows, new_event_row, new_event_rows, new_filters, populate, random_time, \
    read_count_rows, read_event_ids, read_events, read_open_ids, reopen_database, run_blocking, search_windows, \
    Server_Name
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, \
    AuditSource, Env_Retention_Days
from zato.common.audit_log.common import event_count_table
from zato.common.audit_log.event_count import compact_event_counts
from zato.common.audit_log.listing import count_matching, event_conditions
from zato.common.audit_log.retention import Env_Archive_Dir, run_retention

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pytest import MonkeyPatch
    from zato.common.typing_ import any_, intlist

    any_ = any_
    intlist = intlist
    MonkeyPatch = MonkeyPatch

# ################################################################################################################################
# ################################################################################################################################

# How many days of events retention keeps, and how far past the start of the test events it runs,
# so that it deletes the events of the first ninety minutes.
_retention_days = 30
_retention_run_offset = timedelta(days=_retention_days, minutes=90)

# ################################################################################################################################
# ################################################################################################################################

def _assert_counts_exact() -> 'None':
    """ The event counts sum up to the number of events of each minute and key, and to nothing for any other one.
    """
    events = read_events()

    expected = expected_counts(events)
    actual = actual_counts()

    assert actual == expected

# ################################################################################################################################

def _assert_counts_compacted() -> 'None':
    """ After a compaction, each minute and key has exactly one row of the event counts, and none of them is zero.
    """
    _assert_counts_exact()

    events = read_events()
    expected = expected_counts(events)
    count_rows = read_count_rows()

    assert len(count_rows) == len(expected)

# ################################################################################################################################

def _update(ids:'intlist', **values:'any_') -> 'None':
    """ Updates the events of the ids given in place, in one statement.
    """
    engine = get_audit_engine()

    is_selected = event_table.c.id.in_(ids)
    statement = event_table.update().where(is_selected).values(**values)

    with engine.begin() as connection:
        _ = connection.execute(statement)

# ################################################################################################################################

def _delete(ids:'intlist') -> 'None':
    """ Deletes the events of the ids given, in one statement.
    """
    engine = get_audit_engine()

    is_selected = event_table.c.id.in_(ids)
    statement = event_table.delete().where(is_selected)

    with engine.begin() as connection:
        _ = connection.execute(statement)

# ################################################################################################################################
# ################################################################################################################################

def _direct_inserts() -> 'None':
    """ Inserts events many in one statement and one in each transaction.
    """
    rng = Random(20261031)

    rows = new_event_rows(rng, 3000, 0)
    insert_rows(rows)

    for index in range(5000, 5050):
        event_time = random_time(rng)
        row = new_event_row(rng, index, event_time)
        insert_rows([row])

    _assert_counts_exact()

# ################################################################################################################################

def _updates_in_place() -> 'None':
    """ Changes events in place, one by one and many at once, in counted columns and in the data alone.
    """
    rng = Random(20261101)

    rows = new_event_rows(rng, 2000, 0)
    insert_rows(rows)

    ids = read_event_ids()

    # The key columns of single events ..
    for event_id in rng.sample(ids, 100):
        _update([event_id], outcome=AuditOutcome.Error, status=None)

    _assert_counts_exact()

    # .. the moments of many events at once, into other minutes ..
    moved_ids = rng.sample(ids, 200)
    moved_time = random_time(rng)

    _update(moved_ids, event_time=moved_time)
    _assert_counts_exact()

    # .. the source and the object of many events at once ..
    changed_ids = rng.sample(ids, 200)

    _update(changed_ids, source=AuditSource.Scheduler, event_type=AuditEvent.Job_Executed, object_name=None)
    _assert_counts_exact()

    # .. and the data alone.
    data_ids = rng.sample(ids, 300)
    count_rows_before = read_count_rows()

    _update(data_ids, data='')
    _assert_counts_exact()

    count_rows_after = read_count_rows()
    assert count_rows_after == count_rows_before

# ################################################################################################################################

def _retention() -> 'None':
    """ Runs retention over events of which it deletes about half.
    """
    rng = Random(20261102)

    rows = new_event_rows(rng, 3000, 0)
    insert_rows(rows)

    engine = get_audit_engine()
    now = Base_Time + _retention_run_offset

    run_retention(engine, now)

    remaining_ids = read_event_ids()
    remaining_count = len(remaining_ids)

    assert 0 < remaining_count < 3000
    _assert_counts_exact()

# ################################################################################################################################

def _compaction() -> 'None':
    """ Compacts the counts of inserts, updates and deletes, then those of later changes, then nothing.
    """
    rng = Random(20261103)
    engine = get_audit_engine()

    # Counts of inserts, updates and deletes are compacted ..
    rows = new_event_rows(rng, 2000, 0)
    insert_rows(rows)

    ids = read_event_ids()
    changed_ids = rng.sample(ids, 300)
    deleted_ids = rng.sample(ids, 300)

    _update(changed_ids, outcome=AuditOutcome.Error)
    _delete(deleted_ids)

    compacted_up_to = compact_event_counts(engine, event_count_table, 0)
    _assert_counts_compacted()

    # .. as are those of the changes after that, from where the first compaction ended ..
    rows = new_event_rows(rng, 1000, 10000)
    insert_rows(rows)

    ids = read_event_ids()
    deleted_ids = rng.sample(ids, 500)
    _delete(deleted_ids)

    later_up_to = compact_event_counts(engine, event_count_table, compacted_up_to)

    assert later_up_to > compacted_up_to
    _assert_counts_compacted()

    # .. and a compaction with nothing new to compact changes nothing.
    count_rows_before = read_count_rows()
    final_up_to = compact_event_counts(engine, event_count_table, later_up_to)
    count_rows_after = read_count_rows()

    assert final_up_to == later_up_to
    assert count_rows_after == count_rows_before

# ################################################################################################################################

def _rebuild(backend:'str') -> 'None':
    """ Writes events into a database created before the event counts and the open exchanges, opens it again
    and writes more events after that.
    """
    rng = Random(20261104)

    rows = new_event_rows(rng, 1000, 0)
    insert_rows(rows)

    # The events written while the database had none of it are counted when it is opened again ..
    drop_read_schema(backend)

    rows = new_event_rows(rng, 2000, 10000)
    insert_rows(rows)

    ids = read_event_ids()
    deleted_ids = rng.sample(ids, 300)
    _delete(deleted_ids)

    reopen_database()

    _assert_counts_exact()

    events = read_events()
    expected_open = expected_open_ids(events)
    open_ids = read_open_ids()

    assert sorted(open_ids) == sorted(expected_open)

    # .. and the events written after that are counted as they are written.
    rows = new_event_rows(rng, 500, 20000)
    insert_rows(rows)

    _assert_counts_exact()

# ################################################################################################################################

def _count_matching_searches() -> 'None':
    """ Compares the number of events each search matches with the number of its matching events counted one by one.
    """
    rng = Random(20261105)
    populate(rng, 4500)

    engine = get_audit_engine()

    with engine.connect() as connection:
        dialect_name = connection.dialect.name

        for window in search_windows():
            for filter_set in count_filter_sets():

                filters = new_filters(window, filter_set)
                conditions = event_conditions(dialect_name, filters)

                statement = select(func.count())
                statement = statement.select_from(event_table)
                statement = statement.where(*conditions)

                expected = connection.execute(statement).scalar_one()
                actual = count_matching(connection, filters)

                assert actual == expected, (window, filter_set)

# ################################################################################################################################
# ################################################################################################################################

def test_counts_after_writes_through_the_api(audit_backend:'str') -> 'None':
    """ The events the audit log writes are counted, whether each is written in a transaction of its own or in batches.
    """
    rng = Random(20261030)

    # Each event in a transaction of its own ..
    audit_log = AuditLog(Server_Name, flush_max_size=1)

    for index in range(40):
        object_name = rng.choice(Connection_Names)
        outcome = rng.choice([AuditOutcome.OK, AuditOutcome.Error])
        _ = audit_log.insert(AuditSource.MLLP_Outgoing, AuditEvent.Message_Sent, object_name, cid=f'cid.api.{index}',
            msg_id=f'msg.{index}', outcome=outcome)

    # .. and in batches.
    buffered_log = AuditLog(Server_Name, flush_max_size=100, flush_max_wait_ms=60000)

    for index in range(400):
        object_name = rng.choice(Connection_Names)
        outcome = rng.choice([AuditOutcome.OK, AuditOutcome.Error])
        _ = buffered_log.insert(AuditSource.MLLP_Channel, AuditEvent.Message_Received, object_name,
            cid=f'cid.batch.{index}', msg_id=f'msg.{index}', outcome=outcome, status='closed')

    buffered_log.flush()

    _ = run_blocking(_assert_counts_exact)

# ################################################################################################################################

def test_counts_after_direct_inserts(audit_backend:'str') -> 'None':
    """ Events inserted many in one statement and one in each transaction are counted.
    """
    _ = run_blocking(_direct_inserts)

# ################################################################################################################################

def test_counts_after_updates_in_place(audit_backend:'str') -> 'None':
    """ Events changed in place move from the counts of their old minute and key to those of the new ones,
    while a change of no counted column leaves the counts as they are.
    """
    _ = run_blocking(_updates_in_place)

# ################################################################################################################################

def test_counts_after_retention(audit_backend:'str', monkeypatch:'MonkeyPatch') -> 'None':
    """ The events retention deletes are no longer counted.
    """
    monkeypatch.setenv(Env_Retention_Days, str(_retention_days))
    monkeypatch.delenv(Env_Archive_Dir, raising=False)

    _ = run_blocking(_retention)

# ################################################################################################################################

def test_counts_after_compaction(audit_backend:'str') -> 'None':
    """ A compaction leaves one row per minute and key with the same sums, and a later one compacts
    only what changed after the earlier one.
    """
    _ = run_blocking(_compaction)

# ################################################################################################################################

def test_counts_after_rebuild(audit_backend:'str') -> 'None':
    """ A database created before the event counts and the open exchanges existed has them created and filled
    from its events when it is opened, and kept from then on.
    """
    _ = run_blocking(_rebuild, audit_backend)

# ################################################################################################################################

def test_count_matching_at_windows_that_cut_minutes(audit_backend:'str') -> 'None':
    """ The number of events a search matches, read from the event counts and from the events at the edges
    of its time window, is the number of matching events counted one by one.
    """
    _ = run_blocking(_count_matching_searches)

# ################################################################################################################################
# ################################################################################################################################
