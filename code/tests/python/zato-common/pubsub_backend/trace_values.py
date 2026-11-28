# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The delivered-message traces and the released payloads that the statements updating the message rows maintain -
# the drop of the payloads on acknowledgement, a new payload of a message that dropped its own, and the rename of a topic.

# SQLAlchemy
from sqlalchemy import select

# Zato
from common import delete_all_rows, delete_audit_rows, get_message_rows, get_trace_rows
from zato.common.db_env.database import get_database_engine
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.pending import new_pending_ack
from zato.common.pubsub.sql.schema import released_payload_table
from zato.common.test.audit_log_ import new_test_audit_log

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The topics and the subscriber of the scenario
_topic_name    = 'pubsub.backend.test.trace-values.orders'
_topic_renamed = 'pubsub.backend.test.trace-values.orders-renamed'

_sub_key = 'zpsk.test.trace-values.billing'

# The payload of each message published, and the one that replaces it
_data         = 'Invoice INV-7781 for John Smith'
_data_updated = 'Invoice INV-7781 for John Smith, amended'

# ################################################################################################################################
# ################################################################################################################################

def _new_backend() -> 'SQLPubSubBackend':
    """ Returns a backend with an audit log of its own, starting from empty tables, with one subscriber of the topic.
    """
    delete_all_rows()
    delete_audit_rows()

    out = SQLPubSubBackend(audit_log=new_test_audit_log())
    out.subscribe(_sub_key, _topic_name)

    return out

# ################################################################################################################################

def _publish(backend:'SQLPubSubBackend', count:'int') -> 'strlist':
    """ Publishes the given number of messages to the topic and returns their identifiers.
    """
    out:'strlist' = []

    for _ in range(count):
        result = backend.publish(_topic_name, _data)
        out.append(result.msg_id)

    return out

# ################################################################################################################################

def _ack(backend:'SQLPubSubBackend', msg_ids:'strlist') -> 'None':
    """ Acknowledges the given messages in a commit of its own, which makes each of them fully delivered.
    """
    pending = new_pending_ack(_sub_key, msg_ids, None)
    backend._writer.ack(pending)

    assert pending.exception is None, pending.exception
    assert pending.fully_delivered_count == len(msg_ids), pending.fully_delivered_count

# ################################################################################################################################

def _get_message_row(topic_name:'str', msg_id:'str') -> 'any_':
    """ Returns the message row of one message identifier.
    """
    for row in get_message_rows(topic_name):
        if row.msg_id == msg_id:
            out = row
            break
    else:
        raise Exception(f'No message row for {msg_id}')

    return out

# ################################################################################################################################

def _get_released_payload_ids() -> 'anylist':
    """ Returns the payloads listed for the cleanup sweep, in the order they were released.
    """
    engine = get_database_engine()

    query = select(released_payload_table.c.payload_id)
    query = query.order_by(released_payload_table.c.id)

    with engine.connect() as connection:
        out = connection.execute(query).scalars().all()

    return out

# ################################################################################################################################

def _run_ack(backend:'SQLPubSubBackend') -> 'None':
    """ The acknowledgement that drops the payloads of messages adds each of them to the traces and releases its payload,
    in the statement that drops it, and leaves the other messages alone.
    """
    first, second, third = _publish(backend, 3)

    first_row = _get_message_row(_topic_name, first)
    third_row = _get_message_row(_topic_name, third)

    _ack(backend, [first, third])

    # The acknowledged messages are traces, with the topic and the publication time of their message rows ..
    traces = get_trace_rows(_topic_name)
    trace_values = [(row.message_id, row.topic_name, row.pub_time_ms) for row in traces]

    assert trace_values == [
        (first_row.id, _topic_name, first_row.pub_time_ms),
        (third_row.id, _topic_name, third_row.pub_time_ms),
    ], trace_values

    # .. their payloads are released ..
    released = _get_released_payload_ids()
    assert sorted(released) == sorted([first_row.payload_id, third_row.payload_id]), released

    # .. and the message still awaiting its subscriber keeps its payload.
    second_row = _get_message_row(_topic_name, second)
    assert not second_row.payload_dropped
    assert second_row.payload == _data

# ################################################################################################################################

def _run_new_payload(backend:'SQLPubSubBackend') -> 'None':
    """ A new payload of a message that dropped its own removes the message from the traces and releases nothing more.
    """
    first, second = _publish(backend, 2)
    _ack(backend, [first, second])

    assert len(get_trace_rows(_topic_name)) == 2
    released = _get_released_payload_ids()

    # The edited message has a payload again and is no longer a trace ..
    is_updated = backend.update_message(_topic_name, first, _data_updated)
    assert is_updated

    first_row = _get_message_row(_topic_name, first)
    second_row = _get_message_row(_topic_name, second)

    assert not first_row.payload_dropped
    assert first_row.payload == _data_updated

    traces = get_trace_rows(_topic_name)
    trace_ids = [row.message_id for row in traces]
    assert trace_ids == [second_row.id], trace_ids

    # .. and the payload it dropped earlier is not released a second time.
    assert _get_released_payload_ids() == released

# ################################################################################################################################

def _run_rename(backend:'SQLPubSubBackend') -> 'None':
    """ The rename of a topic renames the traces of its messages along with the messages.
    """
    first, second = _publish(backend, 2)
    _ack(backend, [first])

    first_row = _get_message_row(_topic_name, first)

    backend.rename_topic(_topic_name, _topic_renamed)

    # No trace is left under the old name ..
    assert get_trace_rows(_topic_name) == []

    # .. and the trace of the acknowledged message moved to the new one.
    traces = get_trace_rows(_topic_renamed)
    trace_values = [(row.message_id, row.topic_name) for row in traces]
    assert trace_values == [(first_row.id, _topic_renamed)], trace_values

    second_row = _get_message_row(_topic_renamed, second)
    assert not second_row.payload_dropped

# ################################################################################################################################

def run_trace_values_scenario() -> 'None':
    """ The traces and the released payloads that the updates of the message rows maintain,
    each part starting from empty tables.
    """
    _run_ack(_new_backend())
    _run_new_payload(_new_backend())
    _run_rename(_new_backend())

# ################################################################################################################################
# ################################################################################################################################
