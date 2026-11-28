# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A subscriber that accepts part of a push request has those messages acknowledged before the retry wait of the rest,
# so a server killed during the wait delivers again after a restart only the messages that were not acknowledged,
# in the order of publication, and no message is lost.

# stdlib
from functools import partial

# Zato
from ha_push_delivery.harness import wait_until
from ha_push_delivery.rest_harness import is_acknowledged, ModuleCtx as RESTCtx, stage_batch, wait_until_concluded

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_push_delivery.rest_harness import RESTPushEnvironment

# ################################################################################################################################
# ################################################################################################################################

# How many messages of the first request the subscriber accepts
_accept_count = 2

# ################################################################################################################################
# ################################################################################################################################

def test_server_killed_after_partial_acceptance(rest_push_environment:'RESTPushEnvironment') -> 'None':
    """ The messages that the subscriber accepted are not delivered again after the server is killed
    in the retry wait of the rest of the request.
    """
    env = rest_push_environment
    receiver = env.receiver
    receiver.reset()

    # The subscriber accepts only the first messages of the first request ..
    receiver.accept_next(_accept_count)
    msg_ids = stage_batch(env, RESTCtx.Retry_Settings)

    accepted = msg_ids[:_accept_count]
    not_accepted = msg_ids[_accept_count:RESTCtx.Push_Batch_Size]
    not_sent = msg_ids[RESTCtx.Push_Batch_Size:]

    # .. which are acknowledged before the retry wait of the rest ..
    accepted_acknowledged = partial(is_acknowledged, accepted)
    wait_until(accepted_acknowledged, f'acknowledgement of {accepted}', RESTCtx.Outcome_Timeout)

    # .. the server is killed during the wait and starts again.
    env.server.kill()
    env.server.start()

    wait_until_concluded(msg_ids)

    # The accepted messages are received once ..
    for msg_id in accepted:
        assert receiver.get_attempts(msg_id) == [1], msg_id

    # .. the rest of the first request is received again with the next attempt ..
    for msg_id in not_accepted:
        assert receiver.get_attempts(msg_id) == [1, 2], msg_id

    # .. the messages that were not sent are received once, with the attempt of the new claim ..
    for msg_id in not_sent:
        assert receiver.get_attempts(msg_id) == [2], msg_id

    # .. and what was not acknowledged goes out in the order of publication after the restart.
    assert receiver.get_order(2) == not_accepted + not_sent

# ################################################################################################################################
# ################################################################################################################################
