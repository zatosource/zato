# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The publications that a push subscriber service makes while it processes a delivery batch are logged and counted
# only once the batch commits, a publication under a message ID that stands for a different message is refused
# to the service when it publishes, and a batch whose publication lost its message ID to a different message
# before the commit commits nothing and is delivered again.

# stdlib
from functools import partial

# Zato
from ha_push_delivery.harness import count_audit_events, count_outputs, count_published_log_entries, \
    get_message_correl_ids, import_enmasse, is_concluded, ModuleCtx as HarnessCtx, new_key_prefix, publish, \
    publish_output, wait_until
from zato.common.audit_log.api import AuditEvent
from zato.common.pubsub.sql.errors import PubSubDuplicateMsgID
from zato.common.test.exactly_once.control import count_invocations, hold, read_publications, release, wait_until_held

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_push_delivery.harness import PushEnvironment

# ################################################################################################################################
# ################################################################################################################################

# How long the test waits for an invocation that the test holds, in seconds
_hold_timeout = 120.0

# What the subscriber records when a publication is refused its message ID
_duplicate_outcome = PubSubDuplicateMsgID.__name__

# ################################################################################################################################
# ################################################################################################################################

def _has_published_log_entry(env:'PushEnvironment', msg_id:'str') -> 'bool':
    log_entry_count = count_published_log_entries(env, msg_id)

    out = log_entry_count > 0
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_conflicting_id_refused_at_publish(push_environment:'PushEnvironment') -> 'None':
    """ A subscriber service that publishes under a message ID of a different stored message is refused the ID
    in each attempt, and the message ID keeps the message that it stands for.
    """
    env = push_environment
    import_enmasse(env, True)

    prefix = new_key_prefix()
    key = prefix + 'refused-at-publish'
    original_key = prefix + 'original'
    output_msg_id = prefix + 'output'

    # The message ID stands for a message of another publisher ..
    publish_output(env, output_msg_id, original_key)

    # .. the subscriber publishes under the same ID in each attempt of its round ..
    msg_id = publish(env, key, False, HarnessCtx.Failing_Retry_Settings, output_msg_id=output_msg_id)

    given_up = partial(is_concluded, msg_id, AuditEvent.Delivery_Failed)
    wait_until(given_up, f'round of {key}')

    # .. and is refused the ID each time, without a message ID returned to it ..
    assert count_invocations(key) == 2
    assert read_publications(key) == [_duplicate_outcome, _duplicate_outcome]
    assert count_audit_events(msg_id, AuditEvent.Delivered) == 0

    # .. while the ID keeps the original message, the only one logged as published under it.
    assert get_message_correl_ids(output_msg_id) == [original_key]
    assert count_outputs(key) == 0
    assert count_published_log_entries(env, output_msg_id) == 1

# ################################################################################################################################

def test_conflicting_id_taken_before_commit(push_environment:'PushEnvironment') -> 'None':
    """ A batch whose publication lost its message ID to a different message before the commit of the batch
    commits nothing, the message is delivered again and the subscriber is refused the ID from then on.
    """
    env = push_environment
    import_enmasse(env, True)

    prefix = new_key_prefix()
    key = prefix + 'taken-before-commit'
    other_key = prefix + 'other'
    output_msg_id = prefix + 'output'

    # The subscriber publishes under a message ID that nothing stands for yet and is held ..
    hold(key)
    msg_id = publish(env, key, False, HarnessCtx.Failing_Retry_Settings, output_msg_id=output_msg_id)

    try:
        wait_until_held(key, _hold_timeout)
        assert read_publications(key) == [output_msg_id]

        # .. another publisher takes the ID for a message of its own before the batch commits ..
        publish_output(env, output_msg_id, other_key)

    # .. the attempt is never left held for the tests that follow ..
    finally:
        release(key)

    # .. so the batch commits nothing, the message is delivered again in a new round,
    # .. and the subscriber is refused the ID in each attempt of that round ..
    given_up = partial(is_concluded, msg_id, AuditEvent.Delivery_Failed)
    wait_until(given_up, f'new round of {key}')

    assert count_invocations(key) == 3
    assert read_publications(key) == [output_msg_id, _duplicate_outcome, _duplicate_outcome]
    assert count_audit_events(msg_id, AuditEvent.Delivery_Failed) == 1

    # .. while the ID keeps the message of the other publisher, the only one logged as published under it.
    assert get_message_correl_ids(output_msg_id) == [other_key]
    assert count_outputs(key) == 0
    assert count_published_log_entries(env, output_msg_id) == 1

# ################################################################################################################################

def test_publication_announced_after_commit(push_environment:'PushEnvironment') -> 'None':
    """ A publication of a subscriber service is neither logged nor stored while the batch is still processed,
    and it is logged once and stored once the batch commits.
    """
    env = push_environment
    import_enmasse(env, True)

    key = new_key_prefix() + 'announced'

    # The subscriber publishes and is held ..
    hold(key)
    msg_id = publish(env, key, False, {})

    try:
        wait_until_held(key, _hold_timeout)

        outcomes = read_publications(key)
        outcome_count = len(outcomes)
        assert outcome_count == 1, outcomes

        output_msg_id = outcomes[0]

        # .. while its publication is neither logged nor stored ..
        assert count_published_log_entries(env, output_msg_id) == 0
        assert get_message_correl_ids(output_msg_id) == []

    # .. the attempt is never left held for the tests that follow ..
    finally:
        release(key)

    # .. and once the batch commits, the publication is stored ..
    delivered = partial(is_concluded, msg_id, AuditEvent.Delivered)
    wait_until(delivered, f'delivery of {key}')

    assert get_message_correl_ids(output_msg_id) == [key]

    # .. and logged once.
    announced = partial(_has_published_log_entry, env, output_msg_id)
    wait_until(announced, f'published log entry of {output_msg_id}')

    assert count_published_log_entries(env, output_msg_id) == 1

# ################################################################################################################################

def test_failed_attempt_publication_not_announced(push_environment:'PushEnvironment') -> 'None':
    """ The publications of the attempts that fail are neither logged nor stored.
    """
    env = push_environment
    import_enmasse(env, True)

    key = new_key_prefix() + 'failed-attempts'

    # Each attempt of the round publishes and then fails ..
    msg_id = publish(env, key, True, HarnessCtx.Failing_Retry_Settings)

    given_up = partial(is_concluded, msg_id, AuditEvent.Delivery_Failed)
    wait_until(given_up, f'round of {key}')

    outcomes = read_publications(key)
    outcome_count = len(outcomes)
    assert outcome_count == 2, outcomes

    # .. and none of the publications is logged or stored.
    for output_msg_id in outcomes:
        assert count_published_log_entries(env, output_msg_id) == 0
        assert get_message_correl_ids(output_msg_id) == []

    assert count_outputs(key) == 0

# ################################################################################################################################
# ################################################################################################################################
