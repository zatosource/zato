# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# gevent
from gevent import joinall, spawn

# humanize
from humanize import intcomma

# Zato
from common import set_progress_context, Min_Delivery_Rate_Per_Second, Min_Publish_Rate_Per_Second
from load import consume_until_done
from seeding import count_payloads, seed_aged_queue
from zato.common.pubsub.sql.backend import SQLPubSubBackend

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The laggard pattern - one subscriber of a broadcast topic stops acknowledging
# for months while its peers keep working. Old unacknowledged rows that nothing
# may delete must not degrade anyone else.
_topic_name = 'perf.laggard.topic'

# How many subscribers the topic broadcasts to - one of them is the laggard
_subscriber_count = 10

# How many unacknowledged messages the laggard has accumulated
_aged_message_count = 100000

# How many months' worth of age the accumulated messages carry, in days
_aged_days = 90

# How many fresh messages are published while the laggard is still down
_fresh_message_count = 1000

# How many publisher greenlets pump concurrently with the fast consumers
_publisher_greenlet_count = 2

# The payload every fresh message carries
_fresh_payload = 'laggard-fresh-' + 'x' * 500

# How long one blocking fetch waits inside a consumer greenlet, in milliseconds
_consumer_block_ms = 2000

# How long the live phase may take at most before it is declared hung, in seconds
_deadline_seconds = 60

# ################################################################################################################################
# ################################################################################################################################

def _publish_share(backend:'SQLPubSubBackend', publisher_index:'int') -> 'None':
    """ What one publisher greenlet runs - its share of the fresh messages.
    """
    share = _fresh_message_count // _publisher_greenlet_count

    for _ in range(share):
        _ = backend.publish(_topic_name, _fresh_payload)

# ################################################################################################################################

def _run_live_phase(backend:'SQLPubSubBackend', fast_sub_keys:'strlist') -> 'None':
    """ Fresh traffic flows and the fast subscribers consume it all while the laggard
    stays down - the months-old backlog must not slow any of this down.
    """
    expected_deliveries = _fresh_message_count * len(fast_sub_keys)

    counters:'anydict' = {
        'delivered': 0,
        'expected': expected_deliveries,
    }

    start = monotonic()

    # The fast consumers first, so they are already waiting when the first publish lands ..
    greenlets:'anylist' = []

    for sub_key in fast_sub_keys:
        greenlets.append(spawn(consume_until_done, backend, sub_key, counters, _consumer_block_ms))

    # .. now the publishers pump concurrently with them ..
    for publisher_index in range(_publisher_greenlet_count):
        greenlets.append(spawn(_publish_share, backend, publisher_index))

    # .. and everything fresh must be fetched and acknowledged by every fast peer.
    _ = joinall(greenlets, timeout=_deadline_seconds)

    elapsed = monotonic() - start

    delivered = counters['delivered']
    assert delivered == expected_deliveries, f'Expected {intcomma(expected_deliveries)} deliveries, got {intcomma(delivered)}'

    publish_rate = _fresh_message_count / elapsed
    delivery_rate = delivered / elapsed

    assert publish_rate >= Min_Publish_Rate_Per_Second, f'Laggard-phase publish rate too low: {intcomma(int(publish_rate))}/s'
    assert delivery_rate >= Min_Delivery_Rate_Per_Second, f'Laggard-phase delivery rate too low: {intcomma(int(delivery_rate))}/s'

    print(f'Laggard live phase: {intcomma(int(publish_rate))} publishes/s, {intcomma(int(delivery_rate))} deliveries/s')

# ################################################################################################################################

def _run_drain_phase(backend:'SQLPubSubBackend', laggard_sub_key:'str') -> 'None':
    """ The laggard comes back after months and works off its whole queue -
    the aged backlog plus the fresh messages that queued up behind it.
    """
    expected = _aged_message_count + _fresh_message_count

    start = monotonic()
    drained = 0

    # The same fetch-then-batch-ack loop push delivery runs, until the queue is empty ..
    while True:

        messages = backend.fetch_messages(laggard_sub_key, block_ms=0)

        if not messages:
            break

        msg_ids:'strlist' = []

        for message in messages:
            msg_ids.append(message['msg_id'])

        _ = backend.ack_messages(laggard_sub_key, msg_ids)

        drained += len(messages)

    elapsed = monotonic() - start

    # .. everything the laggard ever held must have gone through ..
    assert drained == expected, f'Expected to drain {intcomma(expected)} messages, got {intcomma(drained)}'

    # .. at no less than the delivery floor even on a months-old queue.
    drain_rate = drained / elapsed

    assert drain_rate >= Min_Delivery_Rate_Per_Second, f'Drain rate too low: {intcomma(int(drain_rate))}/s'

    print(f'Laggard drained {intcomma(drained)} messages at {intcomma(int(drain_rate))}/s')

# ################################################################################################################################

def run_laggard_scenario() -> 'None':
    """ One subscriber of a broadcast topic has not acknowledged anything for three months
    while its nine peers acknowledged everything long ago. The aged backlog must not slow
    down fresh traffic, payloads must be retained exactly as long as the laggard needs them,
    and when it finally comes back, the whole queue must drain at the delivery floor
    with every payload dropped afterwards.
    """
    set_progress_context('laggard live phase', _publisher_greenlet_count, _subscriber_count - 1)

    backend = SQLPubSubBackend()

    laggard_sub_key = 'zpsk.perf.laggard.0000'

    fast_sub_keys:'strlist' = []

    for subscriber_index in range(1, _subscriber_count):
        fast_sub_keys.append(f'zpsk.perf.laggard.{subscriber_index:04d}')

    all_sub_keys = [laggard_sub_key] + fast_sub_keys

    # The laggard's three months of unacknowledged messages, seeded natively ..
    seed_seconds = seed_aged_queue(
        topic_name=_topic_name,
        sub_keys=all_sub_keys,
        delivery_sub_keys=[laggard_sub_key],
        message_count=_aged_message_count,
        aged_days=_aged_days,
    )
    print(f'Seeded {intcomma(_aged_message_count)} aged messages in {seed_seconds:.2f}s')

    # .. every aged payload is retained because the laggard still needs it ..
    assert count_payloads(_topic_name) == _aged_message_count

    # .. fresh traffic must be entirely unaffected by the aged backlog ..
    _run_live_phase(backend, fast_sub_keys)

    # .. the dashboard view of the queue stays exact - months-old plus fresh ..
    depths = backend.get_pending_depths([(laggard_sub_key, _topic_name)])
    assert depths[laggard_sub_key] == _aged_message_count + _fresh_message_count

    # .. the laggard comes back and works everything off ..
    set_progress_context('laggard drain phase', 0, 1)
    _run_drain_phase(backend, laggard_sub_key)

    # .. and with the last subscriber done, every single payload is dropped.
    assert count_payloads(_topic_name) == 0

    depths = backend.get_pending_depths([(laggard_sub_key, _topic_name)])
    assert depths[laggard_sub_key] == 0

# ################################################################################################################################
# ################################################################################################################################
