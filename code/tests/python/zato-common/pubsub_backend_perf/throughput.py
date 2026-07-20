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
from common import get_min_delivery_rate, get_min_publish_rate, set_progress_context
from load import consume_until_done
from seeding import delete_all_rows, seed_backlog
from zato.common.pubsub.sql.backend import SQLPubSubBackend

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# How many topics, each with its own subscriber, the publish rate is measured over.
_publish_topic_count = 10

# How many messages the publish rate is measured over.
_publish_message_count = 500

# How many publisher greenlets the publish rate is measured across.
_publish_greenlet_count = 30

# How many topics, each with its own subscriber and consumer greenlet,
# the delivery rate is measured over.
_delivery_topic_count = 50

# How many pending messages per subscriber wait in the queues before the consumers start.
_delivery_backlog_per_subscriber = 60

# How many messages the publishers add live while the backlog drains.
_delivery_message_count = 3000

# How many messages one delivery run works off in total.
_delivery_total_count = _delivery_topic_count * _delivery_backlog_per_subscriber + _delivery_message_count

# How many publisher greenlets pump concurrently with the consumers.
_publisher_greenlet_count = 30

# How long one blocking fetch waits inside a consumer greenlet, in milliseconds.
_consumer_block_ms = 500

# How long the whole delivery run may take at most before it is declared hung, in seconds.
_delivery_deadline_seconds = 60

# ################################################################################################################################
# ################################################################################################################################

def _publish_throughput_share(backend:'SQLPubSubBackend', topic_names:'strlist', publisher_index:'int') -> 'None':
    """ What one publisher greenlet runs - its share of the measured messages,
    each message its own fully durable transaction, round-robin over all the topics.
    """
    share, remainder = divmod(_publish_message_count, _publish_greenlet_count)

    # The remainder of the division goes to the first publishers, one message each,
    # so all the shares add up to the total.
    if publisher_index < remainder:
        share += 1

    for message_index in range(share):
        topic_name = topic_names[(publisher_index * share + message_index) % _publish_topic_count]
        _ = backend.publish(topic_name, f'publish-throughput-{publisher_index}-{message_index}')

# ################################################################################################################################

def run_publish_throughput_scenario() -> 'None':
    """ Publishing must sustain at least 100 messages a second across concurrent
    publishers - the shape of production traffic, where many clients publish at once.
    Every message is still its own fully durable transaction - the databases share
    the transaction log flush across concurrent commits, so the floor holds without
    trading away any durability.
    """
    set_progress_context('publish throughput', _publish_greenlet_count, 0)

    delete_all_rows()

    backend = SQLPubSubBackend()

    # Every topic has a subscriber so each publish writes a delivery row too ..
    topic_names:'strlist' = []

    for topic_index in range(_publish_topic_count):
        topic_name = f'perf.publish.{topic_index:04d}'
        topic_names.append(topic_name)
        backend.subscribe(f'zpsk.perf.publish.{topic_index:04d}', topic_name)

    # .. publish the measured burst from concurrent publishers ..
    start = monotonic()

    greenlets:'anylist' = []

    for publisher_index in range(_publish_greenlet_count):
        greenlets.append(spawn(_publish_throughput_share, backend, topic_names, publisher_index))

    _ = joinall(greenlets, raise_error=True)

    elapsed = monotonic() - start

    # .. and the rate must clear the floor.
    rate = _publish_message_count / elapsed

    assert rate >= get_min_publish_rate(), f'Publish rate too low: {intcomma(int(rate))}/s over {intcomma(_publish_message_count)} messages'

# ################################################################################################################################

def _publish_share(backend:'SQLPubSubBackend', topic_names:'strlist', publisher_index:'int') -> 'None':
    """ What one publisher greenlet runs - its share of the measured messages,
    round-robin over all the topics.
    """
    share, remainder = divmod(_delivery_message_count, _publisher_greenlet_count)

    # The remainder of the division goes to the first publishers, one message each,
    # so all the shares add up to the total.
    if publisher_index < remainder:
        share += 1

    for message_index in range(share):
        topic_name = topic_names[(publisher_index * share + message_index) % _delivery_topic_count]
        _ = backend.publish(topic_name, f'delivery-throughput-{publisher_index}-{message_index}')

# ################################################################################################################################

def run_delivery_throughput_scenario() -> 'None':
    """ Delivery must sustain at least 500 messages a second across the whole subscriber
    population - one consumer greenlet per subscriber doing blocking fetches with batched
    acknowledgements, which is exactly the runtime pattern of push delivery. Every queue
    holds a backlog before the consumers start and publisher greenlets pump fresh traffic
    concurrently, so the measured rate is what delivery itself sustains rather than
    however fast the publishers happen to feed it.
    """
    set_progress_context('delivery throughput', _publisher_greenlet_count, _delivery_topic_count)

    # Seed the backlog before any consumer exists ..
    seed_seconds = seed_backlog(
        topic_count=_delivery_topic_count,
        messages_per_topic=_delivery_backlog_per_subscriber,
        topic_prefix='perf.delivery',
        sub_key_prefix='zpsk.perf.delivery',
    )
    print(f'Seeded {intcomma(_delivery_topic_count * _delivery_backlog_per_subscriber)} backlog messages in {seed_seconds:.2f}s')

    backend = SQLPubSubBackend()

    # .. every topic has its own subscriber ..
    topic_names:'strlist' = []
    sub_keys:'strlist' = []

    for topic_index in range(_delivery_topic_count):
        topic_names.append(f'perf.delivery.{topic_index:04d}')
        sub_keys.append(f'zpsk.perf.delivery.{topic_index:04d}')

    # .. the shared counter tells every consumer when the run is over ..
    counters:'anydict' = {
        'delivered': 0,
        'expected': _delivery_total_count,
    }

    start = monotonic()

    # .. consumers first, draining their backlogs from the very first fetch ..
    greenlets:'anylist' = []

    for sub_key in sub_keys:
        greenlets.append(spawn(consume_until_done, backend, sub_key, counters, _consumer_block_ms))

    # .. now the publishers pump concurrently with the consumers ..
    for publisher_index in range(_publisher_greenlet_count):
        greenlets.append(spawn(_publish_share, backend, topic_names, publisher_index))

    # .. wait until every message has been fetched and acknowledged.
    _ = joinall(greenlets, timeout=_delivery_deadline_seconds)

    elapsed = monotonic() - start

    delivered = counters['delivered']
    assert delivered == _delivery_total_count, f'Expected {intcomma(_delivery_total_count)} deliveries, got {intcomma(delivered)}'

    rate = delivered / elapsed

    assert rate >= get_min_delivery_rate(), f'Delivery rate too low: {intcomma(int(rate))}/s over {intcomma(delivered)} messages'

# ################################################################################################################################
# ################################################################################################################################
