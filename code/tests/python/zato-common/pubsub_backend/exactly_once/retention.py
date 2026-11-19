# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from common import env_value, get_message_rows
from exactly_once.harness import build, count_deliveries, count_messages, First_Output_Topic, FutureCleanup, Input_Sub_Key, \
    Input_Topic, lease, Milliseconds_Per_Day, Milliseconds_Per_Second, new_backend, publish_input
from zato.common.pubsub.sql.cleanup import PubSubCleanup
from zato.common.pubsub.sql.config import get_delivered_max_days, ModuleCtx
from zato.common.pubsub.sql.errors import PubSubDuplicateMsgID
from zato.common.pubsub.sql.fenced_ack import PubSubAckConflict

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.sql.backend import SQLPubSubBackend

    SQLPubSubBackend = SQLPubSubBackend

# ################################################################################################################################
# ################################################################################################################################

# The message ID of the message whose dedup record marks the end of the deduplication window
_window_msg_id = 'exactly-once.backend.window'

# The message ID of the message that the over-cap sweep removes, and the payloads published under it
_over_cap_msg_id = 'exactly-once.backend.over-cap'
_over_cap_payload = 'Order ORD-0042 for Maria Johnson'
_different_payload = 'Shipment SHP-1203 for Jane Doe'

# How many fully delivered messages each topic retains while the over-cap sweep removes the message
_no_delivered_messages = '0'

# How long the message that the expiry sweep removes remains in the queue, in seconds
_short_expiration = 60

# How far ahead of the database the clock of the expiry sweep runs, in milliseconds
_expiry_offset_ms = 2 * _short_expiration * Milliseconds_Per_Second

# ################################################################################################################################
# ################################################################################################################################

def run_deduplication_window_scenario() -> 'None':
    """ The dedup record of a message ID keeps the ID taken for a window longer than the retention of the trace,
    a repeat after the aged sweep removed the trace is a repeat all the same, and once the dedup sweep removed
    the dedup record after the window, the same message ID is accepted as a new message.
    """
    max_days = get_delivered_max_days()
    window_days = max_days * 2

    with env_value(ModuleCtx.Env_Dedup_Window_Days, str(window_days)):

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

        # .. the cleanup removes the trace once it is past the retention age, while the dedup record remains ..
        retention_offset_ms = (max_days + 1) * Milliseconds_Per_Day

        cleanup = FutureCleanup(retention_offset_ms)
        counts = cleanup.sweep_once()

        assert counts['aged'] == 1, counts
        assert counts['dedup'] == 0, counts
        assert count_messages(Input_Topic) == 0

        # .. so a repeat after the removal of the trace stores nothing either ..
        _ = backend.publish(Input_Topic, 'payload', msg_id=_window_msg_id)

        assert count_messages(Input_Topic) == 0
        assert count_deliveries(Input_Sub_Key) == 0

        # .. the cleanup removes the dedup record once the window ended ..
        window_offset_ms = (window_days + 1) * Milliseconds_Per_Day

        cleanup = FutureCleanup(window_offset_ms)
        counts = cleanup.sweep_once()

        assert counts['dedup'] == 1, counts

        # .. and the same message ID is a new message after that.
        _ = backend.publish(Input_Topic, 'payload', msg_id=_window_msg_id)

        assert count_messages(Input_Topic) == 1
        assert count_deliveries(Input_Sub_Key) == 1

# ################################################################################################################################

def _remove_over_cap(backend:'SQLPubSubBackend') -> 'None':
    """ Publishes the message of the over-cap message ID, delivers it fully and lets the over-cap sweep remove its trace.
    """
    _ = backend.publish(Input_Topic, _over_cap_payload, msg_id=_over_cap_msg_id)

    removed_count = backend.ack_pulled(Input_Sub_Key, [_over_cap_msg_id])
    assert removed_count == 1

    with env_value(ModuleCtx.Env_Delivered_Max_Messages, _no_delivered_messages):
        counts = PubSubCleanup().sweep_once()

    assert counts['over_cap'] == 1, counts
    assert counts['dedup'] == 0, counts
    assert count_messages(Input_Topic) == 0

# ################################################################################################################################

def run_window_after_over_cap_scenario() -> 'None':
    """ A repeat of a message that the over-cap sweep removed is a repeat within the dedup window,
    with no new message and no delivery.
    """
    backend = new_backend()
    _remove_over_cap(backend)

    _ = backend.publish(Input_Topic, _over_cap_payload, msg_id=_over_cap_msg_id)

    assert count_messages(Input_Topic) == 0
    assert count_deliveries(Input_Sub_Key) == 0

# ################################################################################################################################

def run_different_content_after_removal_scenario() -> 'None':
    """ A publication with the message ID of a removed message and a different payload or a different topic
    fails with PubSubDuplicateMsgID within the dedup window.
    """
    backend = new_backend()
    _remove_over_cap(backend)

    # A different payload under the same message ID ..
    with pytest.raises(PubSubDuplicateMsgID):
        _ = backend.publish(Input_Topic, _different_payload, msg_id=_over_cap_msg_id)

    # .. and the same payload to a different topic are both refused ..
    with pytest.raises(PubSubDuplicateMsgID):
        _ = backend.publish(First_Output_Topic, _over_cap_payload, msg_id=_over_cap_msg_id)

    # .. and store nothing.
    assert count_messages(Input_Topic) == 0
    assert count_messages(First_Output_Topic) == 0
    assert count_deliveries(Input_Sub_Key) == 0

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
