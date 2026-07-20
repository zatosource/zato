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
# and its publishers keep publishing. How many queues there are, how deep each
# one is and how many get cleared all come in as parameters - the same scenario
# runs both as many mid-size queues and as few queues of millions of messages each.

# The naming the seeded backlog uses
_topic_prefix = 'perf.operations'
_sub_key_prefix = 'zpsk.perf.operations'

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

# How often the end-of-run check reads the queue depths, in seconds
_depth_poll_seconds = 1

# How long the consumers keep consuming after the clears when the run does not
# drain to zero, in seconds - long enough to show the system stays live
# with the operators done, short enough not to dominate the runtime
_post_clear_window_seconds = 60

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
    topic_count = len(topic_names)

    for message_index in range(share):
        topic_name = topic_names[(publisher_index * share + message_index) % topic_count]
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

def _pick_deepest_queues(
    backend:'SQLPubSubBackend',
    sub_keys:'strlist',
    topic_names:'strlist',
    cleared_queue_count:'int',
    ) -> 'strlist':
    """ Returns the subscribers with the deepest pending queues - the ones
    operators actually want to clear.
    """
    depths = backend.get_pending_depths(list(zip(sub_keys, topic_names)))

    by_depth = sorted(sub_keys, key=depths.__getitem__, reverse=True)

    out = by_depth[:cleared_queue_count]
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

def run_operations_scenario(
    *,
    topic_count:'int',
    backlog_per_subscriber:'int',
    cleared_queue_count:'int',
    clear_budget_seconds:'int',
    deadline_seconds:'int',
    min_publish_rate:'int',
    min_delivery_rate:'int',
    drain_to_zero:'bool',
    ) -> 'None':
    """ Live operations on a draining system - every consumer works off a deep
    backlog with fresh traffic still arriving into every queue, and mid-drain the
    operators clear the deepest queues, each while its consumer keeps consuming.
    Publishing must hold its floor throughout, every clear must finish within
    its budget, and at the end every message must be accounted for exactly -
    consumed or cleared, none lost, with the double-counting window no bigger
    than at-least-once delivery inherently allows.

    With drain_to_zero the consumers finish every remaining message and the
    delivery floor covers the whole run. Without it - the mode the millions-deep
    scale runs in, where the remainder would be a handful of consumers grinding
    for hours - the consumers get a fixed post-clear window to hold the delivery
    floor, and then the operators clear every remaining queue, the way a stuck
    environment is recovered, with the accounting covering both paths.
    """
    backend = SQLPubSubBackend()

    # Every subscriber's backlog, seeded natively in one go ..
    total_backlog = topic_count * backlog_per_subscriber

    seed_seconds = seed_backlog(
        topic_count=topic_count,
        messages_per_topic=backlog_per_subscriber,
        topic_prefix=_topic_prefix,
        sub_key_prefix=_sub_key_prefix,
    )
    print(f'Seeded {total_backlog} backlog messages in {seed_seconds:.2f}s')

    topic_names:'strlist' = []
    sub_keys:'strlist' = []

    for topic_index in range(topic_count):
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

    cleared_sub_keys = _pick_deepest_queues(backend, sub_keys, topic_names, cleared_queue_count)
    clear_results:'anydict' = {}

    operator_greenlets:'anylist' = []
    operator_share = cleared_queue_count // _operator_greenlet_count

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

    assert len(clear_results) == cleared_queue_count

    for sub_key, clear_result in clear_results.items():
        clear_elapsed = clear_result['elapsed']
        assert clear_elapsed <= clear_budget_seconds, f'Clear of {sub_key} too slow: {clear_elapsed:.1f}s'

    # .. with drain_to_zero the consumers finish everything that was not cleared ..
    window_delivered = 0

    if drain_to_zero:
        _wait_until_empty(backend, sub_keys, topic_names, deadline_seconds)

    # .. otherwise they get a fixed window to show delivery holds its floor
    # .. with the operators done ..
    else:
        window_before = sum(per_sub_delivered.values())
        sleep(_post_clear_window_seconds)
        window_delivered = sum(per_sub_delivered.values()) - window_before

    elapsed = monotonic() - start

    stop['is_set'] = True
    _ = joinall(consumer_greenlets, timeout=deadline_seconds)

    # .. whatever the window left behind, the operators now clear - each sweep
    # .. is the same clear-millions-in-one-action operation and gets the same budget.
    # .. The consumers are gone, so the sweep counts are exact ..
    swept_counts:'anydict' = {}

    if not drain_to_zero:
        for sub_key in sub_keys:

            sweep_start = monotonic()
            result = backend.clear_queue(sub_key)
            sweep_elapsed = monotonic() - sweep_start

            assert sweep_elapsed <= clear_budget_seconds, f'Sweep of {sub_key} too slow: {sweep_elapsed:.1f}s'

            swept_counts[sub_key] = result['cleared_count']

    # .. every message must now be accounted for exactly. Every queue was owed
    # .. its backlog plus its share of the fresh traffic ..
    fresh_per_topic = _fresh_message_count // topic_count
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

        accounted = delivered

        if sub_key in clear_results:
            cleared = clear_results[sub_key]['cleared_count']
            total_cleared += cleared
            accounted += cleared

        if not drain_to_zero:
            swept = swept_counts[sub_key]
            total_cleared += swept
            accounted += swept

        # .. a mid-run cleared queue was raced by its consumer, so its overlap
        # .. stays within what at-least-once delivery allows ..
        if sub_key in clear_results:
            assert accounted >= expected_per_queue, \
                f'Messages lost on {sub_key}: {accounted} accounted for, {expected_per_queue} expected'

            overlap = accounted - expected_per_queue
            assert overlap <= max_overlap_per_queue, f'Overlap too big on {sub_key}: {overlap}'

            total_overlap += overlap

        # .. every other queue balances exactly - what it delivered, plus what
        # .. the final sweep found, is precisely what it was owed.
        else:
            assert accounted == expected_per_queue, \
                f'Expected {expected_per_queue} accounted for on {sub_key}, got {accounted}'

    # .. nothing is in flight anywhere anymore ..
    assert count_rows('pubsub_delivery') == 0

    # .. and the population held the delivery floor with the operators at work -
    # .. over the whole run when it drains to zero, over the post-clear window otherwise.
    delivery_rate = total_delivered / elapsed

    if drain_to_zero:
        assert delivery_rate >= min_delivery_rate, f'Delivery rate too low during operations: {delivery_rate:.0f}/s'
    else:
        window_rate = window_delivered / _post_clear_window_seconds
        assert window_rate >= min_delivery_rate, f'Post-clear delivery rate too low: {window_rate:.0f}/s'

    message = f'Operations: {total_delivered} delivered at {delivery_rate:.0f}/s, {total_cleared} cleared'
    message += f' across {cleared_queue_count} queues of {backlog_per_subscriber} each, overlap {total_overlap},'
    message += f' {publish_rate:.0f} publishes/s concurrently'
    print(message)

# ################################################################################################################################
# ################################################################################################################################
