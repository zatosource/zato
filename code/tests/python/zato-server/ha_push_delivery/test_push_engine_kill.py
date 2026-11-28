# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A server killed while the push engine has a request of the batch in flight to a slow subscriber acknowledged nothing
# of that batch, so after a restart every message of the batch is delivered with the next delivery attempt, in the order
# of publication, and only the messages of the request in flight are received twice.

# Zato
from ha_push_delivery.rest_harness import ModuleCtx as RESTCtx, stage_batch, wait_until_concluded

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_push_delivery.rest_harness import RESTPushEnvironment

# ################################################################################################################################
# ################################################################################################################################

def test_server_killed_with_request_in_flight(rest_push_environment:'RESTPushEnvironment') -> 'None':
    """ The batch whose first request was in flight when the server was killed is delivered again after a restart.
    """
    env = rest_push_environment
    receiver = env.receiver
    receiver.reset()

    # The subscriber holds the first request of the batch ..
    first_request = receiver.hold_next()
    msg_ids = stage_batch(env, {})
    receiver.wait_for_requests(1)

    # .. the server is killed while the request is in flight, and the response goes to no one ..
    env.server.kill()
    first_request.set()

    # .. and the server starts again.
    env.server.start()
    wait_until_concluded(msg_ids)

    in_flight = msg_ids[:RESTCtx.Push_Batch_Size]
    not_sent = msg_ids[RESTCtx.Push_Batch_Size:]

    # The messages of the request in flight are received again with the next attempt ..
    for msg_id in in_flight:
        assert receiver.get_attempts(msg_id) == [1, 2], msg_id

    # .. the messages that were not sent are received once, with the attempt of the new claim ..
    for msg_id in not_sent:
        assert receiver.get_attempts(msg_id) == [2], msg_id

    # .. and the batch goes out in the order of publication after the restart.
    assert receiver.get_order(2) == msg_ids

# ################################################################################################################################
# ################################################################################################################################
