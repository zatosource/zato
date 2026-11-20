# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The audit events of the outgoing calls that a push subscriber service makes are committed before each call returns,
# in an attempt that is still in progress, in an attempt that failed and in an attempt of a message that is concluded
# but not yet acknowledged, so a server that is killed leaves one event for each call that reached the endpoint.

# stdlib
from functools import partial

# Zato
from ha_push_delivery.harness import count_audit_events, count_outgoing_requests, count_outputs, count_pending, \
    count_received, count_rejected, import_enmasse, is_concluded, ModuleCtx as HarnessCtx, new_key_prefix, publish, \
    stage_batch, wait_until
from zato.common.audit_log.api import AuditEvent
from zato.common.test.exactly_once.control import count_invocations, hold, release, wait_until_held

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_push_delivery.harness import PushEnvironment

# ################################################################################################################################
# ################################################################################################################################

# How long the test waits for an invocation that the test holds, in seconds,
# which includes the wait of a retry round before the held attempt
_hold_timeout = 120.0

# The invocation of the failing message that the test holds - its second attempt, after the first one failed
_second_invocation = 2

# ################################################################################################################################
# ################################################################################################################################

def _assert_calls_recorded(env:'PushEnvironment', key:'str', expected:'int') -> 'None':
    """ The audit log holds one event for each request with the key that the endpoint received.
    """
    outgoing_count = count_outgoing_requests(key)
    received_count = count_received(env, key)

    assert outgoing_count == expected, (key, outgoing_count, expected)
    assert received_count == expected, (key, received_count, expected)

# ################################################################################################################################

def _assert_rejected_calls_recorded(env:'PushEnvironment', key:'str', expected:'int') -> 'None':
    """ The audit log holds one event for each request with the key that the endpoint rejected.
    """
    outgoing_count = count_outgoing_requests(key)
    rejected_count = count_rejected(env, key)

    assert outgoing_count == expected, (key, outgoing_count, expected)
    assert rejected_count == expected, (key, rejected_count, expected)

# ################################################################################################################################
# ################################################################################################################################

def test_outgoing_call_recorded_during_attempt(push_environment:'PushEnvironment') -> 'None':
    """ A server killed while a later message of the batch is still processed keeps the events of the outgoing calls
    of every message of the batch, whereas the conclusion of the earlier message commits with the batch only.
    """
    env = push_environment
    batch = stage_batch(env, False, True)

    keys_by_msg_id = {
        batch.first_msg_id: batch.first_key,
        batch.second_msg_id: batch.second_key,
    }

    try:

        # Both messages called the endpoint by the time the second one is held in its first attempt ..
        wait_until_held(batch.second_key, _hold_timeout)

        _assert_calls_recorded(env, batch.first_key, 1)
        _assert_calls_recorded(env, batch.second_key, 1)

        # .. while the first message is concluded in the transaction of the batch, which has not committed yet ..
        assert count_audit_events(batch.first_msg_id, AuditEvent.Delivered) == 0
        assert count_pending(batch.first_msg_id) == 1

        # .. the server is killed during the attempt and the events of both calls remain ..
        env.server.kill()

        _assert_calls_recorded(env, batch.first_key, 1)
        _assert_calls_recorded(env, batch.second_key, 1)

    # .. the attempt is never left held for the tests that follow ..
    finally:
        release(batch.second_key)

    # .. the server starts again and the batch is delivered again ..
    env.server.start()

    for msg_id, key in keys_by_msg_id.items():
        delivered = partial(is_concluded, msg_id, AuditEvent.Delivered)
        wait_until(delivered, f'delivery of {key}')

    # .. and each call that reached the endpoint has one event of its own.
    for msg_id, key in keys_by_msg_id.items():
        _assert_calls_recorded(env, key, 2)

        assert count_invocations(key) == 2
        assert count_outputs(key) == 1
        assert count_audit_events(msg_id, AuditEvent.Delivered) == 1

# ################################################################################################################################

def test_failed_attempts_recorded_while_endpoint_rejects(push_environment:'PushEnvironment') -> 'None':
    """ A server killed in a later attempt of a message whose endpoint rejects every request keeps the events
    of the outgoing calls of the failed attempts and of the attempt in progress.
    """
    env = push_environment
    key = new_key_prefix() + 'rejected'

    # The delivery is active and the endpoint rejects every request ..
    import_enmasse(env, True)
    env.receiver.behavior.set_reject_503()

    try:

        # .. the message fails its first attempt and is held in its second one ..
        hold(key)
        msg_id = publish(env, key, True, HarnessCtx.Failing_Retry_Settings, _second_invocation)

        wait_until_held(key, _hold_timeout)
        _assert_rejected_calls_recorded(env, key, 2)

        # .. the server is killed during the second attempt and the events of both calls remain ..
        env.server.kill()
        _assert_rejected_calls_recorded(env, key, 2)

        # .. the server starts again and the message runs a new round until it is given up on ..
        release(key)
        env.server.start()

        given_up = partial(is_concluded, msg_id, AuditEvent.Delivery_Failed)
        wait_until(given_up, f'new round of {key}')

        # .. and each call of each round has one event of its own.
        invocation_count = count_invocations(key)
        _assert_rejected_calls_recorded(env, key, invocation_count)

        assert invocation_count == 4
        assert count_audit_events(msg_id, AuditEvent.Delivery_Failed) == 1

    finally:
        release(key)
        env.receiver.behavior.set_accept()

# ################################################################################################################################
# ################################################################################################################################
