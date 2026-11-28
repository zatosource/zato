# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The messages of a push delivery batch that were concluded are committed while a later message of the batch
# waits in its retry round or is still being processed, so a server that is killed, a subscription that is edited
# and a server that is stopped leave the outgoing calls, the publications and the audit events of those messages
# recorded, and the messages are not delivered again.

# stdlib
from functools import partial

# Zato
from ha_push_delivery.harness import count_audit_events, count_outgoing_requests, count_outputs, count_pending, \
    count_received, expected_server_records, import_enmasse, is_concluded, ModuleCtx as HarnessCtx, stage_batch, wait_until
from zato.common.audit_log.api import AuditEvent
from zato.common.test.exactly_once.control import count_invocations, release, wait_until_held

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_push_delivery.harness import PushEnvironment, StagedBatch

# ################################################################################################################################
# ################################################################################################################################

# How long the concluded first message may take to commit once the second one failed its first attempt, in seconds,
# which is well within the wait before the second attempt
_commit_timeout = HarnessCtx.Retry_Wait_Seconds / 2

# How long the test waits for an invocation that the test holds, in seconds
_hold_timeout = 120.0

# ################################################################################################################################
# ################################################################################################################################

def _has_invocations(key:'str', count:'int') -> 'bool':
    invocation_count = count_invocations(key)

    out = invocation_count >= count
    return out

# ################################################################################################################################

def _wait_for_commit_during_round(batch:'StagedBatch') -> 'None':
    """ Waits until the second message failed its first attempt and asserts that the first message was committed
    while the second one waits for its second attempt.
    """
    second_invoked = partial(_has_invocations, batch.second_key, 1)
    wait_until(second_invoked, f'first invocation of {batch.second_key}')

    first_delivered = partial(is_concluded, batch.first_msg_id, AuditEvent.Delivered)
    wait_until(first_delivered, f'commit of {batch.first_key} during the retry round', _commit_timeout)

    assert count_invocations(batch.second_key) == 1
    assert count_pending(batch.second_msg_id) == 1

# ################################################################################################################################

def _wait_for_second_given_up(env:'PushEnvironment', batch:'StagedBatch') -> 'None':
    """ Waits until a new round of the second message ran out and the message left the queue,
    which the server logs as an error.
    """
    given_up_record = f'msg_id `{batch.second_msg_id}` after'

    with expected_server_records(env.server, (given_up_record,)):

        second_given_up = partial(is_concluded, batch.second_msg_id, AuditEvent.Delivery_Failed)
        wait_until(second_given_up, f'new round of {batch.second_key}')

        assert count_audit_events(batch.second_msg_id, AuditEvent.Delivery_Failed) == 1

# ################################################################################################################################

def _assert_first_recorded_once(env:'PushEnvironment', batch:'StagedBatch') -> 'None':
    """ The first message was processed once, and its outgoing call, its publication and its audit events
    are recorded once.
    """
    assert count_pending(batch.first_msg_id) == 0
    assert count_invocations(batch.first_key) == 1
    assert count_received(env, batch.first_key) == 1
    assert count_outputs(batch.first_key) == 1
    assert count_audit_events(batch.first_msg_id, AuditEvent.Delivered) == 1
    assert count_outgoing_requests(batch.first_key) == 1

# ################################################################################################################################
# ################################################################################################################################

def test_server_killed_during_retry_round(push_environment:'PushEnvironment') -> 'None':
    """ A server killed while a later message of the batch waits in its retry round keeps everything that the messages
    concluded before it produced.
    """
    env = push_environment
    batch = stage_batch(env, True, False)

    _wait_for_commit_during_round(batch)

    # The server is killed before the second attempt and starts again ..
    env.server.kill()
    assert count_invocations(batch.second_key) == 1

    env.server.start()

    # .. the second message runs a new round ..
    _wait_for_second_given_up(env, batch)

    # .. and the first message is neither delivered again nor missing anything.
    _assert_first_recorded_once(env, batch)

# ################################################################################################################################

def test_subscription_edited_during_retry_round(push_environment:'PushEnvironment') -> 'None':
    """ A subscription edited while a later message of the batch waits in its retry round, which stops the delivery
    of the subscription, keeps everything that the messages concluded before it produced.
    """
    env = push_environment
    batch = stage_batch(env, True, False)

    _wait_for_commit_during_round(batch)

    # The delivery is stopped before the second attempt and starts again ..
    import_enmasse(env, False)
    assert count_invocations(batch.second_key) == 1

    import_enmasse(env, True)

    # .. the second message runs a new round ..
    _wait_for_second_given_up(env, batch)

    # .. and the first message is neither delivered again nor missing anything.
    _assert_first_recorded_once(env, batch)

# ################################################################################################################################

def test_server_stopped_during_attempt(push_environment:'PushEnvironment') -> 'None':
    """ A server stopped while a later message of the batch is still processed for longer than the delivery
    may take to pause keeps everything that the messages concluded before it produced, and nothing
    that the attempt in progress produced is committed twice.
    """
    env = push_environment
    batch = stage_batch(env, False, True)

    # The second message is processed when the server is stopped ..
    wait_until_held(batch.second_key, _hold_timeout)

    env.server.stop()
    release(batch.second_key)

    env.server.start()

    # .. it is delivered again ..
    second_delivered = partial(is_concluded, batch.second_msg_id, AuditEvent.Delivered)
    wait_until(second_delivered, f'delivery of {batch.second_key}')

    assert count_invocations(batch.second_key) == 2
    assert count_outputs(batch.second_key) == 1

    # .. and the first message is neither delivered again nor missing anything.
    _assert_first_recorded_once(env, batch)

# ################################################################################################################################
# ################################################################################################################################
