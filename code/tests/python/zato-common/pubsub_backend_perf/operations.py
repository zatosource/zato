# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# gevent
from gevent import joinall, sleep, spawn

# Zato
from common import Min_Delivery_Rate_Per_Second
from load import consume_until_stopped
from seeding import count_rows, seed_backlog
from zato.common.api import PubSub
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.config import get_batch_size

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The operations pattern - the whole population is draining deep backlogs with
# fresh traffic still arriving into the same queues, and in the middle of it
# operators clear the deepest queues, each while its consumer keeps consuming
# and its publishers keep publishing.
_topic_count = 100

# The naming the seeded backlog uses
_topic_prefix = 'perf.operations'
_sub_key_prefix = 'zpsk.perf.operations'

# How many of the deepest queues the operators clear mid-drain
_cleared_queue_count = 20

# How many operator greenlets issue the clears concurrently
_operator_greenlet_count = 2

# How many fresh messages are published concurrently with the drain,
# round-robin over all the topics - the count divides evenly by the
# topic count so every queue's arithmetic is exact
_fresh_message_count = 2000

# How many publisher greenlets pump concurrently
_publisher_greenlet_count = 2

# The payload every fresh message carries
_fresh_payload = 'operations-fresh-' + 'x' * 500

# How long one blocking fetch waits inside a consumer greenlet, in milliseconds
_consumer_block_ms = 2000

# How long the drain gets before the operators step in, in seconds
_operator_delay_seconds = 1

# How long one clear of one deep queue may take under full load, in seconds
_clear_budget_seconds = 120

# How often the end-of-run check reads the queue depths, in seconds
_depth_poll_seconds = 1

# A message fetched right before its rows were cleared is still acknowledged
# afterwards and counted by both sides - at-least-once semantics. Each such
# overlap is at most one in-flight fetch batch per clear pass over the queue.
_fetch_batch_size = PubSub.Message.Default_Max_Messages

# ################################################################################################################################
# ################################################################################################################################

def _publish_share(backend:'SQLPubSubBackend', topic_names:'strlist', publisher_index:'int') -> 'None':
    """ What one publisher greenlet runs - its share of the fresh messages,
    round-robin over all the topics, cleared ones included, because the system
    keeps accepting requests to a queue no matter what operators do to it.
    """
    share = _fresh_message_count // _publisher_greenlet_count

    for message_index in range(share):
        topic_name = topic_names[(publisher_index * share + message_index) % _topic_count]
        _ = backend.publish(topic_name, _fresh_payload)

# ################################################################################################################################

def _clear_share(backend:'SQLPubSubBackend', sub_keys:'strlist', results:'anydict') -> 'None':
    """ What one operator greenlet runs - clearing its share of the deepest queues,
    one after another, each while that queue's consumer stays attached and fresh
    traffic keeps arriving.
    """
    for sub_key in sub_keys:

        clear_start = monotonic()
        result = backend.clear_queue(sub_key)
        clear_elapsed = monotonic() - clear_start

        results[sub_key] = {
            'cleared_count': result['cleared_count'],
            'elapsed': clear_elapsed,
        }

# ################################################################################################################################

def _pick_deepest_queues(backend:'SQLPubSubBackend', sub_keys:'strlist', topic_names:'strlist') -> 'strlist':
    """ Returns the subscribers with the deepest pending queues - the ones
    operators actually want to clear.
    """
    depths = backend.get_pending_depths(list(zip(sub_keys, topic_names)))

    by_depth = sorted(sub_keys, key=depths.__getitem__, reverse=True)

    out = by_depth[:_cleared_queue_count]
    return out

# ################################################################################################################################

def _wait_until_empty(backend:'SQLPubSubBackend', sub_keys:'strlist', topic_names:'strlist', deadline_seconds:'int') -> 'None':
    """ Waits until every queue reads zero, checking the depths periodically.
    """
    pairs = list(zip(sub_keys, topic_names))
    deadline = monotonic() + deadline_seconds

    while monotonic() < deadline:

        depths = backend.get_pending_depths(pairs)

        if not any(depths.values()):
            return

        sleep(_depth_poll_seconds)

    raise AssertionError('Queues did not drain to zero within the deadline')

# ################################################################################################################################

def run_operations_scenario(*, backlog_per_subscriber:'int', deadline_seconds:'int', min_publish_rate:'int') -> 'None':
    """ Live operations on a draining system - one hundred consumers work off deep
    backlogs with fresh traffic still arriving into every queue, and mid-drain the
    operators clear the twenty deepest queues, each while its consumer keeps
    consuming. Publishing must hold its floor throughout, every clear must finish
    within its budget, and at the end every message must be accounted for exactly -
    consumed or cleared, none lost, with the double-counting window no bigger than
    at-least-once delivery inherently allows.
    """
    backend = SQLPubSubBackend()

    # Every subscriber's backlog, seeded natively in one go ..
    total_backlog = _topic_count * backlog_per_subscriber

    seed_seconds = seed_backlog(
        topic_count=_topic_count,
        messages_per_topic=backlog_per_subscriber,
        topic_prefix=_topic_prefix,
        sub_key_prefix=_sub_key_prefix,
    )
    print(f'Seeded {total_backlog} backlog messages in {seed_seconds:.2f}s')

    topic_names:'strlist' = []
    sub_keys:'strlist' = []

    for topic_index in range(_topic_count):
        topic_names.append(f'{_topic_prefix}.{topic_index:04d}')
        sub_keys.append(f'{_sub_key_prefix}.{topic_index:04d}')

    # .. how much each queue will deliver cannot be known upfront -
    # .. the operators decide that mid-run - so deliveries are counted per queue ..
    per_sub_delivered:'anydict' = {}

    for sub_key in sub_keys:
        per_sub_delivered[sub_key] = 0

    stop:'anydict' = {'is_set': False}

    start = monotonic()

    # .. every queue has its consumer attached for the whole run ..
    consumer_greenlets:'anylist' = []

    for sub_key in sub_keys:
        consumer_greenlets.append(spawn(consume_until_stopped, backend, sub_key, per_sub_delivered, stop, _consumer_block_ms))

    # .. the publishers pump into every topic throughout ..
    publisher_greenlets:'anylist' = []

    for publisher_index in range(_publisher_greenlet_count):
        publisher_greenlets.append(spawn(_publish_share, backend, topic_names, publisher_index))

    # .. the drain gets going, then the operators pick the deepest queues and clear them ..
    sleep(_operator_delay_seconds)

    cleared_sub_keys = _pick_deepest_queues(backend, sub_keys, topic_names)
    clear_results:'anydict' = {}

    operator_greenlets:'anylist' = []
    operator_share = _cleared_queue_count // _operator_greenlet_count

    for operator_index in range(_operator_greenlet_count):
        share_start = operator_index * operator_share
        share = cleared_sub_keys[share_start:share_start + operator_share]
        operator_greenlets.append(spawn(_clear_share, backend, share, clear_results))

    # .. the publish floor must hold with the drain and the clears both running ..
    _ = joinall(publisher_greenlets, timeout=deadline_seconds)

    publish_elapsed = monotonic() - start
    publish_rate = _fresh_message_count / publish_elapsed

    assert publish_rate >= min_publish_rate, f'Publish rate too low during operations: {publish_rate:.0f}/s'

    # .. every clear must finish within its budget ..
    _ = joinall(operator_greenlets, timeout=deadline_seconds)

    assert len(clear_results) == _cleared_queue_count

    for sub_key, clear_result in clear_results.items():
        clear_elapsed = clear_result['elapsed']
        assert clear_elapsed <= _clear_budget_seconds, f'Clear of {sub_key} too slow: {clear_elapsed:.1f}s'

    # .. the consumers finish everything that was not cleared ..
    _wait_until_empty(backend, sub_keys, topic_names, deadline_seconds)

    elapsed = monotonic() - start

    stop['is_set'] = True
    _ = joinall(consumer_greenlets, timeout=deadline_seconds)

    # .. every message must now be accounted for exactly. Every queue was owed
    # .. its backlog plus its share of the fresh traffic ..
    fresh_per_topic = _fresh_message_count // _topic_count
    expected_per_queue = backlog_per_subscriber + fresh_per_topic

    # .. a cleared queue's messages were either consumed or cleared - none lost,
    # .. and the overlap stays within what at-least-once delivery allows ..
    clear_batch_size = get_batch_size()
    max_overlap_per_queue = _fetch_batch_size * (backlog_per_subscriber // clear_batch_size + 1)

    total_delivered = 0
    total_cleared = 0
    total_overlap = 0

    for sub_key in sub_keys:

        delivered = per_sub_delivered[sub_key]
        total_delivered += delivered

        if sub_key in clear_results:
            cleared = clear_results[sub_key]['cleared_count']
            total_cleared += cleared

            accounted = delivered + cleared
            assert accounted >= expected_per_queue, \
                f'Messages lost on {sub_key}: {accounted} accounted for, {expected_per_queue} expected'

            overlap = accounted - expected_per_queue
            assert overlap <= max_overlap_per_queue, f'Overlap too big on {sub_key}: {overlap}'

            total_overlap += overlap

        # .. an uncleared queue delivered everything it was owed, exactly.
        else:
            assert delivered == expected_per_queue, \
                f'Expected {expected_per_queue} deliveries on {sub_key}, got {delivered}'

    # .. nothing is in flight anywhere anymore ..
    assert count_rows('pubsub_delivery') == 0

    # .. and the population held the delivery floor with the operators at work.
    delivery_rate = total_delivered / elapsed

    assert delivery_rate >= Min_Delivery_Rate_Per_Second, f'Delivery rate too low during operations: {delivery_rate:.0f}/s'

    message = f'Operations: {total_delivered} delivered at {delivery_rate:.0f}/s, {total_cleared} cleared'
    message += f' across {_cleared_queue_count} deep queues, overlap {total_overlap},'
    message += f' {publish_rate:.0f} publishes/s concurrently'
    print(message)

# ################################################################################################################################
# ################################################################################################################################
