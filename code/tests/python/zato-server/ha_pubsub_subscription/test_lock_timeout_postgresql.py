# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.pubsub.subscription_list import Lock_Timeout_Ms

# Local
from _support import assert_rows_equal_list, is_postgresql, publish_client, pull_client, RowLock, \
    wait_for_no_unconfirmed, yaml_subscription

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The shares of the lock timeout within which a caller that needs no locked row completes,
    # and within which a caller that needs one fails
    Free_Share = 0.5
    Blocked_Min_Share = 0.5
    Blocked_Max_Share = 3.0

    Topic_Sub_Lock = 'select 1 from pubsub_topic_sub where sub_key = %s and topic_name = %s for update'
    Queue_Count_Lock = 'select 1 from pubsub_queue_count where sub_key = %s and topic_name = %s for update'
    Delivery_Lock = 'select 1 from pubsub_delivery where sub_key = %s and message_id = ' + \
        '(select id from pubsub_message where msg_id = %s) for update'

# ################################################################################################################################
# ################################################################################################################################

def _new_data() -> 'str':
    out = 'lock.timeout.' + CryptoManager.generate_hex_string(32)
    return out

# ################################################################################################################################

def _publish_free(publisher:'any_', topic_name:'str') -> 'str':
    """ Publishes a message that needs no locked row, which commits within a share of the lock timeout.
    """
    started = monotonic()
    response = publisher.publish(topic_name, _new_data())
    elapsed_ms = (monotonic() - started) * 1000

    assert elapsed_ms < Lock_Timeout_Ms * ModuleCtx.Free_Share

    out = response['msg_id']
    return out

# ################################################################################################################################

def _assert_blocked(elapsed_ms:'float') -> 'None':
    """ Confirms that a caller that needed a locked row failed after the lock timeout and not much later.
    """
    assert elapsed_ms >= Lock_Timeout_Ms * ModuleCtx.Blocked_Min_Share
    assert elapsed_ms < Lock_Timeout_Ms * ModuleCtx.Blocked_Max_Share

# ################################################################################################################################
# ################################################################################################################################

pytestmark = pytest.mark.skipif(not is_postgresql(), reason='The lock timeout applies to PostgreSQL')

# ################################################################################################################################
# ################################################################################################################################

def test_lock_on_topic_sub(
    environment:'any_',
    pickup:'any_',
    runtime:'any_',
    names:'any_',
    database_proxy:'any_',
    ) -> 'None':
    """ A lock on the row of a pair fails only the publications to its topic, after the lock timeout,
    while publications to other topics commit and an enmasse file is applied.
    """
    sub_key = runtime.sub_key(names.security_pull)
    added_pair = (sub_key, names.topic_second.lower())
    publisher = publish_client(environment, names)

    lock = RowLock(database_proxy.database, ModuleCtx.Topic_Sub_Lock, [sub_key, names.topic_pull.lower()])
    lock.acquire()

    try:
        _ = _publish_free(publisher, names.topic_second)

        started = monotonic()

        with pytest.raises(Exception):
            _ = publisher.publish(names.topic_pull, _new_data())

        _assert_blocked((monotonic() - started) * 1000)

        pickup.apply('add-second-while-row-locked',
            yaml_subscription(names.security_pull, [names.topic_pull, names.topic_second]))

        _ = _publish_free(publisher, names.topic_second)

    finally:
        lock.release()

    wait_for_no_unconfirmed(runtime)

    assert added_pair in runtime.governed_pairs()
    assert_rows_equal_list(runtime)

# ################################################################################################################################

def test_lock_on_queue_count(environment:'any_', runtime:'any_', names:'any_', database_proxy:'any_') -> 'None':
    """ A lock on a row of pubsub_queue_count fails no publication, because the triggers append rows of their own.
    """
    sub_key = runtime.sub_key(names.security_pull)
    publisher = publish_client(environment, names)

    # A row of the queue exists once a message was queued for it
    _ = _publish_free(publisher, names.topic_pull)

    lock = RowLock(database_proxy.database, ModuleCtx.Queue_Count_Lock, [sub_key, names.topic_pull.lower()])
    lock.acquire()

    try:
        _ = _publish_free(publisher, names.topic_pull)
        _ = _publish_free(publisher, names.topic_second)
    finally:
        lock.release()

# ################################################################################################################################

def test_lock_on_delivery(environment:'any_', runtime:'any_', names:'any_', database_proxy:'any_') -> 'None':
    """ A lock on a delivery fails only its acknowledgement, after the lock timeout, while publications commit,
    and the acknowledgement succeeds after the release.
    """
    sub_key = runtime.sub_key(names.security_pull)
    publisher = publish_client(environment, names)
    subscriber = pull_client(environment, names, names.security_pull)

    seed_msg_id = _publish_free(publisher, names.topic_pull)

    # The message is leased to the subscriber without an acknowledgement ..
    response = subscriber.pull(max_messages=50, needs_ack=False)

    pulled_msg_ids:'list[str]' = []
    for message in response['messages']:
        pulled_msg_ids.append(message['meta']['msg_id'])

    assert seed_msg_id in pulled_msg_ids

    # .. its delivery is locked ..
    lock = RowLock(database_proxy.database, ModuleCtx.Delivery_Lock, [sub_key, seed_msg_id])
    lock.acquire()

    try:
        _ = _publish_free(publisher, names.topic_pull)
        _ = _publish_free(publisher, names.topic_second)

        started = monotonic()

        with pytest.raises(Exception):
            _ = subscriber.ack([seed_msg_id])

        _assert_blocked((monotonic() - started) * 1000)

    finally:
        lock.release()

    # .. and the acknowledgement removes the delivery once the lock is released.
    depth_before = runtime.queue_depth(sub_key)
    _ = subscriber.ack([seed_msg_id])

    assert runtime.queue_depth(sub_key) == depth_before - 1

# ################################################################################################################################
# ################################################################################################################################
