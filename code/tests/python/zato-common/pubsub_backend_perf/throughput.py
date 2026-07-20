# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# gevent
from gevent import joinall, spawn

# Zato
from common import set_progress_context, Min_Delivery_Rate_Per_Second, Min_Publish_Rate_Per_Second
from load import consume_until_done
from seeding import delete_all_rows
from zato.common.pubsub.sql.backend import SQLPubSubBackend

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# How many topics, each with its own subscriber, the publish rate is measured over
_publish_topic_count = 10

# How many messages the publish rate is measured over
_publish_message_count = 500

# How many topics, each with its own subscriber and consumer greenlet,
# the delivery rate is measured over
_delivery_topic_count = 50

# How many messages the delivery rate is measured over
_delivery_message_count = 3000

# How many publisher greenlets pump concurrently with the consumers
_publisher_greenlet_count = 5

# How long one blocking fetch waits inside a consumer greenlet, in milliseconds
_consumer_block_ms = 500

# How long the whole delivery run may take at most before it is declared hung, in seconds
_delivery_deadline_seconds = 60

# ################################################################################################################################
# ################################################################################################################################

def run_publish_throughput_scenario() -> 'None':
    """ Publishing must sustain at least 100 messages a second - measured one publish
    at a time, each its own transaction, round-robin over subscribed topics.
    """
    set_progress_context('publish throughput', 1, 0)

    delete_all_rows()

    backend = SQLPubSubBackend()

    # Every topic has a subscriber so each publish writes a delivery row too ..
    topic_names:'strlist' = []

    for topic_index in range(_publish_topic_count):
        topic_name = f'perf.publish.{topic_index:04d}'
        topic_names.append(topic_name)
        backend.subscribe(f'zpsk.perf.publish.{topic_index:04d}', topic_name)

    # .. publish the measured burst ..
    start = monotonic()

    for message_index in range(_publish_message_count):
        topic_name = topic_names[message_index % _publish_topic_count]
        _ = backend.publish(topic_name, f'publish-throughput-{message_index}')

    elapsed = monotonic() - start

    # .. and the rate must clear the floor.
    rate = _publish_message_count / elapsed

    assert rate >= Min_Publish_Rate_Per_Second, f'Publish rate too low: {rate:.0f}/s over {_publish_message_count} messages'

# ################################################################################################################################

def _publish_share(backend:'SQLPubSubBackend', topic_names:'strlist', publisher_index:'int') -> 'None':
    """ What one publisher greenlet runs - its share of the measured messages,
    round-robin over all the topics.
    """
    share = _delivery_message_count // _publisher_greenlet_count

    for message_index in range(share):
        topic_name = topic_names[(publisher_index * share + message_index) % _delivery_topic_count]
        _ = backend.publish(topic_name, f'delivery-throughput-{publisher_index}-{message_index}')

# ################################################################################################################################

def run_delivery_throughput_scenario() -> 'None':
    """ Delivery must sustain at least 500 messages a second across the whole subscriber
    population - one consumer greenlet per subscriber doing blocking fetches with batched
    acknowledgements while publisher greenlets pump concurrently, which is exactly
    the runtime pattern of push delivery.
    """
    set_progress_context('delivery throughput', _publisher_greenlet_count, _delivery_topic_count)

    delete_all_rows()

    backend = SQLPubSubBackend()

    # Every topic has its own subscriber ..
    topic_names:'strlist' = []
    sub_keys:'strlist' = []

    for topic_index in range(_delivery_topic_count):
        topic_name = f'perf.delivery.{topic_index:04d}'
        sub_key = f'zpsk.perf.delivery.{topic_index:04d}'

        topic_names.append(topic_name)
        sub_keys.append(sub_key)

        backend.subscribe(sub_key, topic_name)

    # .. the shared counter tells every consumer when the run is over ..
    counters:'anydict' = {
        'delivered': 0,
        'expected': _delivery_message_count,
    }

    start = monotonic()

    # .. consumers first, so they are already waiting when the first publish lands ..
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
    assert delivered == _delivery_message_count, f'Expected {_delivery_message_count} deliveries, got {delivered}'

    rate = delivered / elapsed

    assert rate >= Min_Delivery_Rate_Per_Second, f'Delivery rate too low: {rate:.0f}/s over {delivered} messages'

# ################################################################################################################################
# ################################################################################################################################
