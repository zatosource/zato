# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta
from random import Random

# SQLAlchemy
from sqlalchemy import select

# Zato
from support import Base_Time, Connection_Names, expected_open_ids, insert_rows, new_event_row, new_event_rows, \
    random_time, read_event_ids, read_events, read_open_ids, run_blocking, Server_Name
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, \
    AuditSource, Env_Retention_Days
from zato.common.audit_log.common import Status_Outstanding
from zato.common.audit_log.listing import event_conditions, new_search_filters
from zato.common.audit_log.retention import Env_Archive_Dir, run_retention

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from pytest import MonkeyPatch
    from zato.common.typing_ import any_, anylist, intlist, intset

    any_ = any_
    anylist = anylist
    datetime = datetime
    intlist = intlist
    intset = intset
    MonkeyPatch = MonkeyPatch

# ################################################################################################################################
# ################################################################################################################################

# How many days of events retention keeps, and how far past the start of the test events it runs,
# so that it deletes the events of the first ninety minutes.
_retention_days = 30
_retention_run_offset = timedelta(days=_retention_days, minutes=90)

# ################################################################################################################################
# ################################################################################################################################

def _outstanding_ids() -> 'intset':
    """ The ids of the events the outstanding filter of the outgoing MLLP source finds.
    """
    engine = get_audit_engine()

    filters = new_search_filters(
        sources=[AuditSource.MLLP_Outgoing],
        object_names=[],
        outcomes=[],
        event_types=[],
        sources_excluded=[],
        object_names_excluded=[],
        statuses_excluded=[],
        query='',
        status=Status_Outstanding,
        time_from=None,
        time_to=None,
    )

    out:'intset' = set()

    with engine.connect() as connection:

        dialect_name = connection.dialect.name
        conditions = event_conditions(dialect_name, filters)

        statement = select(event_table.c.id)
        statement = statement.where(*conditions)

        for event_id in connection.execute(statement).scalars():
            out.add(event_id)

    return out

# ################################################################################################################################

def _assert_open_exact() -> 'None':
    """ The open exchanges are the messages no acknowledgment answers, each of them once,
    and the outstanding filter finds exactly these.
    """
    events = read_events()

    expected = expected_open_ids(events)
    open_ids = read_open_ids()
    outstanding_ids = _outstanding_ids()

    assert sorted(open_ids) == sorted(expected)
    assert outstanding_ids == expected

# ################################################################################################################################

def _exchange_rows(
    rng:'Random',
    count:'int',
    first_index:'int',
    send_time:'datetime | None' = None,
    ack_time:'datetime | None' = None,
    ) -> 'anylist':
    """ The rows of a number of messages and of their acknowledgments, every second acknowledgment before its message.
    The moments are random unless they are given.
    """
    out:'anylist' = []

    for index in range(count):

        if send_time is None:
            this_send_time = random_time(rng)
        else:
            this_send_time = send_time

        if ack_time is None:
            this_ack_time = random_time(rng)
        else:
            this_ack_time = ack_time

        send_index = first_index + index * 2
        ack_index = send_index + 1

        send = new_event_row(rng, send_index, this_send_time, AuditSource.MLLP_Outgoing, AuditEvent.Message_Sent)
        ack = new_event_row(rng, ack_index, this_ack_time, AuditSource.MLLP_Outgoing, AuditEvent.Ack_Received)

        ack['msg_id'] = send['msg_id']
        ack['object_name'] = send['object_name']

        if index % 2 == 0:
            out.append(send)
            out.append(ack)
        else:
            out.append(ack)
            out.append(send)

    return out

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
# ################################################################################################################################

def _sends_and_acks_in_one_statement() -> 'None':
    """ Writes messages and their acknowledgments in one statement, and other events after them.
    """
    rng = Random(20261108)

    rows = _exchange_rows(rng, 250, 0)
    insert_rows(rows)

    rows = new_event_rows(rng, 1000, 10000)
    insert_rows(rows)

    _assert_open_exact()

# ################################################################################################################################

def _sends_and_acks_in_separate_transactions() -> 'None':
    """ Writes messages and their acknowledgments each in a transaction of its own.
    """
    rng = Random(20261109)

    rows = _exchange_rows(rng, 60, 0)

    for row in rows:
        insert_rows([row])

    _assert_open_exact()

# ################################################################################################################################

def _updates() -> 'None':
    """ Changes the event types, the message ids, the connections and the sources of events in place.
    """
    rng = Random(20261111)

    rows = _exchange_rows(rng, 300, 0)
    insert_rows(rows)

    rows = new_event_rows(rng, 600, 10000)
    insert_rows(rows)

    ids = read_event_ids()

    # Events turned into acknowledgments ..
    acked_ids = rng.sample(ids, 100)
    _update(acked_ids, source=AuditSource.MLLP_Outgoing, event_type=AuditEvent.Ack_Received)

    _assert_open_exact()

    # .. events turned into messages ..
    sent_ids = rng.sample(ids, 100)
    _update(sent_ids, source=AuditSource.MLLP_Outgoing, event_type=AuditEvent.Message_Sent)

    _assert_open_exact()

    # .. events moved to another message id, one by one ..
    for event_id in rng.sample(ids, 50):
        _update([event_id], msg_id='msg.moved')

    _assert_open_exact()

    # .. events moved to no connection at all ..
    unnamed_ids = rng.sample(ids, 50)
    _update(unnamed_ids, object_name=None)

    _assert_open_exact()

    # .. and events moved to another source.
    moved_ids = rng.sample(ids, 50)
    _update(moved_ids, source=AuditSource.MLLP_Channel)

    _assert_open_exact()

# ################################################################################################################################

def _retention() -> 'None':
    """ Writes exchanges of which retention deletes the acknowledgments only, the messages only, or both, and runs it.
    """
    rng = Random(20261112)

    early_time = Base_Time + timedelta(minutes=10)
    late_time = Base_Time + timedelta(hours=2)

    # Acknowledgments older than their messages, which retention deletes while the messages remain ..
    rows = _exchange_rows(rng, 100, 0, send_time=late_time, ack_time=early_time)
    insert_rows(rows)

    # .. messages older than their acknowledgments ..
    rows = _exchange_rows(rng, 100, 1000, send_time=early_time, ack_time=late_time)
    insert_rows(rows)

    # .. and exchanges at random moments.
    rows = _exchange_rows(rng, 200, 2000)
    insert_rows(rows)

    _assert_open_exact()

    engine = get_audit_engine()
    now = Base_Time + _retention_run_offset

    run_retention(engine, now)

    _assert_open_exact()

# ################################################################################################################################
# ################################################################################################################################

def test_sends_and_acks_in_one_statement(audit_backend:'str') -> 'None':
    """ Messages and their acknowledgments written in one statement, in either order, close each other,
    and messages without one stay open.
    """
    _ = run_blocking(_sends_and_acks_in_one_statement)

# ################################################################################################################################

def test_sends_and_acks_in_separate_transactions(audit_backend:'str') -> 'None':
    """ Messages and their acknowledgments written each in a transaction of its own, in either order, close each other.
    """
    _ = run_blocking(_sends_and_acks_in_separate_transactions)

# ################################################################################################################################

def test_sends_and_acks_through_the_api(audit_backend:'str') -> 'None':
    """ Messages and acknowledgments the audit log writes in batches close each other.
    """
    rng = Random(20261110)

    buffered_log = AuditLog(Server_Name, flush_max_size=100, flush_max_wait_ms=60000)

    for index in range(600):
        event_type = rng.choice([AuditEvent.Message_Sent, AuditEvent.Ack_Received])
        object_name = rng.choice(Connection_Names[:2])
        msg_number = rng.randrange(200)

        _ = buffered_log.insert(AuditSource.MLLP_Outgoing, event_type, object_name, cid=f'cid.api.{index}',
            msg_id=f'msg.{msg_number}', outcome=AuditOutcome.OK)

    buffered_log.flush()

    _ = run_blocking(_assert_open_exact)

# ################################################################################################################################

def test_open_exchanges_after_updates(audit_backend:'str') -> 'None':
    """ Messages turned into acknowledgments, and messages and acknowledgments moved to other message ids
    or connections, open and close exchanges accordingly.
    """
    _ = run_blocking(_updates)

# ################################################################################################################################

def test_open_exchanges_after_retention(audit_backend:'str', monkeypatch:'MonkeyPatch') -> 'None':
    """ A message whose acknowledgment retention deletes is open again, and the messages retention deletes
    are no longer open.
    """
    monkeypatch.setenv(Env_Retention_Days, str(_retention_days))
    monkeypatch.delenv(Env_Archive_Dir, raising=False)

    _ = run_blocking(_retention)

# ################################################################################################################################
# ################################################################################################################################
