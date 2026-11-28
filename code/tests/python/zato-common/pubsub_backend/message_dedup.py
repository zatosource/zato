# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The dedup records of the message IDs of publications under faults - a publication that fails after its dedup record
# is written, a dedup record that expired while its message remains, and a dedup record that a publication renews
# while the dedup sweep runs.

# stdlib
from zlib import crc32

# gevent
import gevent

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import and_, event, select
from sqlalchemy.exc import DBAPIError

# Zato
from common import delete_all_rows, env_value, get_delivery_rows, get_message_rows
from zato.common.common_db.message_dedup import Kind
from zato.common.common_db.schema import message_dedup_table
from zato.common.db_env.database import get_database_engine
from zato.common.db_env.outage import logger as outage_logger
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.cleanup import PubSubCleanup
from zato.common.pubsub.sql.config import ModuleCtx
from zato.common.pubsub.sql.dedup import Dedup_Scope, get_fingerprint
from zato.common.pubsub.sql.errors import PubSubDuplicateMsgID
from zato.common.pubsub.sql.publication import build_publication
from zato.common.test.audit_log_ import new_test_audit_log
from zato.common.test.expected_records import expected_records

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

    any_ = any_
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# The topic and the subscriber of the scenarios
_topic = 'pubsub.backend.test.message-dedup'
_sub_key = 'zpsk.test.message-dedup'

# The message IDs of the scenarios
_msg_id_failed = 'zpsm.test.message-dedup.failed'
_msg_id_conflict = 'zpsm.test.message-dedup.conflict'
_msg_id_renewed = 'zpsm.test.message-dedup.renewed'

# The payloads published under those message IDs
_data_original = 'Invoice INV-7781 for John Smith'
_data_different = 'Shipment SHP-1203 for Jane Doe'

# The dedup window of a publication whose dedup record expires the moment it is written
_no_dedup_window_days = '0'

# The beginning of the statement of the dedup sweep that selects the expired dedup records
_expired_select_prefix = 'SELECT zato_message_dedup.kind'

# ################################################################################################################################
# ################################################################################################################################

def _new_backend() -> 'SQLPubSubBackend':
    """ Returns a backend over empty tables, with one subscriber of the topic of the scenarios.
    """
    delete_all_rows()

    out = SQLPubSubBackend(audit_log=new_test_audit_log())
    out.subscribe(_sub_key, _topic)

    return out

# ################################################################################################################################

def _get_dedup_records(msg_id:'str') -> 'anylist':
    """ Returns the dedup records of one message ID of a publication.
    """
    query = select(message_dedup_table)
    query = query.where(and_(
        message_dedup_table.c.kind == Kind.Pubsub,
        message_dedup_table.c.scope == Dedup_Scope,
        message_dedup_table.c.message_id == msg_id,
    ))

    with get_database_engine().connect() as connection:
        out = connection.execute(query).all()

    return out

# ################################################################################################################################

def _get_expected_fingerprint(data:'str') -> 'str':
    """ Returns the fingerprint of a publication of the given payload to the topic of the scenarios.
    """
    payload_crc32 = crc32(data.encode('utf8'))

    out = get_fingerprint(_topic, payload_crc32)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _run_failure_after_dedup_record() -> 'None':
    """ A publication whose message insert fails after its dedup record was written leaves no dedup record behind,
    and its retry is stored as a new message.
    """
    backend = _new_backend()

    # The message row of the publication lacks a value that its column requires, so its insert fails ..
    failed = build_publication(backend, _topic, _data_original, msg_id=_msg_id_failed)
    failed.pending.message_values['recv_time_iso'] = None

    with expected_records(outage_logger.name), pytest.raises(DBAPIError):
        backend._writer.publish(failed.pending)

    # .. which rolls back its dedup record with it ..
    assert _get_dedup_records(_msg_id_failed) == []
    assert get_message_rows(_topic) == []

    # .. so its retry is a new message with one delivery and one dedup record.
    retried = build_publication(backend, _topic, _data_original, msg_id=_msg_id_failed)
    backend._writer.publish(retried.pending)

    assert not retried.pending.is_repeat
    assert len(get_message_rows(_topic)) == 1
    assert len(get_delivery_rows(_sub_key)) == 1
    assert len(_get_dedup_records(_msg_id_failed)) == 1

# ################################################################################################################################

def _run_conflict_of_message_insert() -> 'None':
    """ A dedup record that expired while its undelivered message remains is replaced by the next publication
    of its message ID and then given the fingerprint of the message, so that a publication with the original
    content is a repeat.
    """
    backend = _new_backend()

    # The original message remains in the queue, while its dedup record expires the moment it is written ..
    with env_value(ModuleCtx.Env_Dedup_Window_Days, _no_dedup_window_days):
        original = build_publication(backend, _topic, _data_original, msg_id=_msg_id_conflict)

    backend._writer.publish(original.pending)

    # .. a different message under the same ID replaces the expired dedup record and meets the original message ..
    different = build_publication(backend, _topic, _data_different, msg_id=_msg_id_conflict)

    with pytest.raises(PubSubDuplicateMsgID):
        backend._writer.publish(different.pending)

    # .. which gives the dedup record the fingerprint of the original message ..
    records = _get_dedup_records(_msg_id_conflict)
    assert len(records) == 1

    record = records[0]
    assert record.fingerprint == _get_expected_fingerprint(_data_original)
    assert record.expires_ms == different.pending.dedup_expires_ms

    # .. so a repeat of the original is a repeat within the dedup window that writes nothing.
    repeated = build_publication(backend, _topic, _data_original, msg_id=_msg_id_conflict)
    backend._writer.publish(repeated.pending)

    assert repeated.pending.is_repeat
    assert repeated.pending.exception is None
    assert len(get_message_rows(_topic)) == 1
    assert len(get_delivery_rows(_sub_key)) == 1

# ################################################################################################################################

def _run_sweep_against_renewed_record() -> 'None':
    """ A dedup record that a publication renews while the dedup sweep runs remains with the window of the renewal.
    The sweep holds the lock of the expired dedup record, so the renewal waits for the sweep and writes the dedup record
    again.
    """
    backend = _new_backend()

    # The original dedup record expires the moment it is written ..
    with env_value(ModuleCtx.Env_Dedup_Window_Days, _no_dedup_window_days):
        original = build_publication(backend, _topic, _data_original, msg_id=_msg_id_renewed)

    backend._writer.publish(original.pending)

    renewal = build_publication(backend, _topic, _data_original, msg_id=_msg_id_renewed)
    renewals:'anylist' = []

    # .. and a repeat of its message renews it once the sweep has selected it.
    def _on_expired_select(*args:'any_') -> 'None':
        statement = args[2]

        if renewals or not statement.startswith(_expired_select_prefix):
            return

        greenlet = gevent.spawn(backend._writer.publish, renewal.pending)
        renewals.append(greenlet)

    engine = get_database_engine()
    event.listen(engine, 'after_cursor_execute', _on_expired_select)

    try:
        counts = PubSubCleanup().sweep_once()
    finally:
        event.remove(engine, 'after_cursor_execute', _on_expired_select)

    _ = gevent.joinall(renewals, raise_error=True)

    assert counts['dedup'] == 1, counts

    # The dedup record remains with the window of the renewal, which repeats the stored message.
    records = _get_dedup_records(_msg_id_renewed)
    assert len(records) == 1

    record = records[0]
    assert record.expires_ms == renewal.pending.dedup_expires_ms
    assert record.fingerprint == _get_expected_fingerprint(_data_original)

    assert renewal.pending.is_repeat
    assert len(get_message_rows(_topic)) == 1

# ################################################################################################################################

def run_message_dedup_scenario() -> 'None':
    """ The dedup records of publications under faults.
    """
    _run_failure_after_dedup_record()
    _run_conflict_of_message_insert()
    _run_sweep_against_renewed_record()

# ################################################################################################################################
# ################################################################################################################################
