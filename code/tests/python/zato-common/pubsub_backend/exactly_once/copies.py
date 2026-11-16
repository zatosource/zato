# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
from gevent import joinall, spawn

# Zato
from exactly_once.common import build, count_deliveries, First_Output_Sub_Key, First_Output_Topic, get_built_msg_id, \
    get_msg_ids, Input_Sub_Key, lease_repeatedly, new_backend, publish_input
from zato.common.pubsub.sql.fenced_ack import PubSubAckConflict

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.sql.backend import SQLPubSubBackend
    from zato.common.pubsub.sql.publication import BuiltPublication
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

# How many copies of one message compete for its acknowledgement
_copy_count = 10

copy_list = list['_Copy']

# ################################################################################################################################
# ################################################################################################################################

class _Copy:
    """ One copy of a leased message, which acknowledges it with its own attempt and its own publication.
    """

    def __init__(self, backend:'SQLPubSubBackend', msg_id:'str', delivery_attempt:'int') -> 'None':
        self.backend = backend
        self.msg_id = msg_id
        self.delivery_attempt = delivery_attempt

        data = f'output-{delivery_attempt}'
        self.publication:'BuiltPublication' = build(backend, First_Output_Topic, data)

        self.is_committed = False
        self.is_rejected = False

# ################################################################################################################################

    def run(self) -> 'None':
        consumed = [(self.msg_id, self.delivery_attempt)]
        publications = [self.publication]

        try:
            _ = self.backend.ack_pulled_with_publications(Input_Sub_Key, consumed, publications)
        except PubSubAckConflict:
            self.is_rejected = True
        else:
            self.is_committed = True

# ################################################################################################################################
# ################################################################################################################################

def run_concurrent_copies_scenario() -> 'None':
    """ Copies of one message acknowledge it concurrently, each with its own attempt and its own publication,
    after as many consecutive leases, and only the copy with the current attempt commits.
    """
    backend = new_backend()
    msg_id = publish_input(backend, 'input')

    # The message is leased as many times as there are copies ..
    now_ms = backend.clock.now_ms()
    lease_result = lease_repeatedly(backend, now_ms, _copy_count)

    assert lease_result.attempts[msg_id] == _copy_count

    # .. each copy holds one of the attempts ..
    copies:'copy_list' = []

    for index in range(_copy_count):
        delivery_attempt = index + 1
        message_copy = _Copy(backend, msg_id, delivery_attempt)
        copies.append(message_copy)

    # .. all of them acknowledge at once ..
    greenlets:'anylist' = []

    for message_copy in copies:
        greenlet = spawn(message_copy.run)
        greenlets.append(greenlet)

    _ = joinall(greenlets, raise_error=True)

    # .. and only the copy of the last lease commits.
    committed:'copy_list' = []

    for message_copy in copies:
        if message_copy.is_committed:
            committed.append(message_copy)
        else:
            assert message_copy.is_rejected, message_copy.delivery_attempt

    committed_count = len(committed)
    assert committed_count == 1

    winner = committed[0]
    winner_msg_id = get_built_msg_id(winner.publication)

    assert winner.delivery_attempt == _copy_count
    assert get_msg_ids(First_Output_Topic) == [winner_msg_id]
    assert count_deliveries(First_Output_Sub_Key) == 1
    assert count_deliveries(Input_Sub_Key) == 0

# ################################################################################################################################
# ################################################################################################################################
