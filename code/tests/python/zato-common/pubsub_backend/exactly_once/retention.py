# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from common import get_message_rows
from exactly_once.harness import build, count_deliveries, count_messages, First_Output_Topic, FutureCleanup, Input_Sub_Key, \
    Input_Topic, lease, Milliseconds_Per_Day, Milliseconds_Per_Second, new_backend, publish_input
from zato.common.pubsub.sql.config import get_delivered_max_days
from zato.common.pubsub.sql.fenced_ack import PubSubAckConflict

# ################################################################################################################################
# ################################################################################################################################

# The message ID of the message whose trace marks the end of the deduplication window
_window_msg_id = 'exactly-once.backend.window'

# How long the message that the expiry sweep removes remains in the queue, in seconds
_short_expiration = 60

# How far ahead of the database the clock of the expiry sweep runs, in milliseconds
_expiry_offset_ms = 2 * _short_expiration * Milliseconds_Per_Second

# ################################################################################################################################
# ################################################################################################################################

def run_deduplication_window_scenario() -> 'None':
    """ The trace of a fully delivered message keeps its message ID taken, and once the cleanup removed the trace
    after the retention age, the same message ID is accepted as a new message.
    """
    backend = new_backend()

    # The message is published and fully delivered, which leaves only its trace ..
    _ = backend.publish(Input_Topic, 'payload', msg_id=_window_msg_id)

    removed_count = backend.ack_pulled(Input_Sub_Key, [_window_msg_id])
    assert removed_count == 1

    rows = get_message_rows(Input_Topic)
    trace = rows[0]

    assert trace.payload is None

    # .. a repeated publication stores nothing new ..
    _ = backend.publish(Input_Topic, 'payload', msg_id=_window_msg_id)

    assert count_messages(Input_Topic) == 1
    assert count_deliveries(Input_Sub_Key) == 0

    # .. the cleanup removes the trace once it is past the retention age ..
    max_days = get_delivered_max_days()
    retention_days = max_days + 1
    offset_ms = retention_days * Milliseconds_Per_Day

    cleanup = FutureCleanup(offset_ms)
    counts = cleanup.sweep_once()

    assert counts['aged'] == 1, counts
    assert count_messages(Input_Topic) == 0

    # .. and the same message ID is a new message after that.
    _ = backend.publish(Input_Topic, 'payload', msg_id=_window_msg_id)

    assert count_messages(Input_Topic) == 1
    assert count_deliveries(Input_Sub_Key) == 1

# ################################################################################################################################

def run_removed_by_expiry_scenario() -> 'None':
    """ A leased message that the expiry sweep removed rejects an acknowledgement with a new publication,
    and an acknowledgement without publications commits with no removed row.
    """
    backend = new_backend()
    msg_id = publish_input(backend, 'input', _short_expiration)

    now_ms = backend.clock.now_ms()
    attempts = lease(backend, now_ms)
    attempt = attempts[msg_id]

    # The expiry sweep removes the leased message ..
    cleanup = FutureCleanup(_expiry_offset_ms)
    counts = cleanup.sweep_once()

    assert counts['expired'] == 1, counts
    assert count_deliveries(Input_Sub_Key) == 0

    consumed = [(msg_id, attempt)]

    # .. so an acknowledgement that publishes something new is rejected ..
    output = build(backend, First_Output_Topic, 'output')

    with pytest.raises(PubSubAckConflict):
        _ = backend.ack_pulled_with_publications(Input_Sub_Key, consumed, [output])

    assert count_messages(First_Output_Topic) == 0

    # .. while one that publishes nothing commits with no removed row.
    result = backend.ack_pulled_with_publications(Input_Sub_Key, consumed, [])

    assert result.removed_count == 0
    assert result.published == []

# ################################################################################################################################
# ################################################################################################################################
