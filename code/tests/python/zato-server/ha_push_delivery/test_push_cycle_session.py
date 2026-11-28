# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A database session of the server terminated while it commits a push cycle, after the subscriber accepted every
# message of the batch, acknowledged nothing of that batch, so the running server delivers the batch again with the next
# delivery attempt, in the order of publication, no message is lost and no message outside the batch is delivered twice.

# Zato
from ha_push_delivery.rest_harness import CommitHold, publish_message, stage_batch, terminate_session, \
    wait_until_concluded

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_push_delivery.rest_harness import RESTPushEnvironment

# ################################################################################################################################
# ################################################################################################################################

def test_session_terminated_during_cycle_commit(rest_push_environment:'RESTPushEnvironment') -> 'None':
    """ The batch whose commit ended with its session is delivered again by the same server, and nothing else is.
    """
    env = rest_push_environment
    receiver = env.receiver
    receiver.reset()

    # The first request of the batch is held ..
    first_request = receiver.hold_next()
    msg_ids = stage_batch(env, {})
    receiver.wait_for_requests(1)

    # .. while the test locks the delivery rows, which the batch was claimed with already ..
    commit_hold = CommitHold(env)

    try:
        commit_hold.lock()
        first_request.set()

        # .. the subscriber accepts every message, the commit of the cycle waits for the lock,
        # and the session of the server that commits is terminated.
        pid = commit_hold.wait_for_blocked_session()
        terminate_session(pid)

    finally:
        commit_hold.release()

    # A message is published after the batch ..
    later_msg_id = publish_message(env, 'later', {})
    wait_until_concluded(msg_ids + [later_msg_id])

    # .. each message of the batch is delivered twice, the second time with the next attempt ..
    for msg_id in msg_ids:
        assert receiver.get_attempts(msg_id) == [1, 2], msg_id

    # .. in the order of publication each time ..
    assert receiver.get_order(2) == msg_ids
    assert receiver.get_order(1) == msg_ids + [later_msg_id]

    # .. and the message published afterwards is delivered once.
    assert receiver.get_attempts(later_msg_id) == [1]

# ################################################################################################################################
# ################################################################################################################################
