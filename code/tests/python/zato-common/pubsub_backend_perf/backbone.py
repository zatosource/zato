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
from seeding import seed_backlog
from zato.common.pubsub.sql.backend import SQLPubSubBackend

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The backbone pattern - one broker carries every event of a whole organization:
# a thousand distinct channels, each with a handful of subscribers, sustained
# mixed-size traffic across all of them at once.
_topic_count = 1000

# How many subscribers every channel has.
_subscribers_per_topic = 3

# How many pending messages per channel wait in the queues before the consumers start.
_backlog_per_topic = 2

# How many messages are published live in the measured run, spread over all the channels.
_message_count = 2000

# How many publisher greenlets pump concurrently with the consumers.
_publisher_greenlet_count = 30

# Most messages are small envelopes ..
_small_payload = 'backbone-' + 'x' * 1000

# .. but one in twenty carries an embedded document.
_large_payload = 'backbone-large-' + 'x' * 46000
_large_payload_every = 20

# How long one blocking fetch waits inside a consumer greenlet, in milliseconds.
_consumer_block_ms = 5000

# How long the whole run may take at most before it is declared hung, in seconds.
_deadline_seconds = 120

# ################################################################################################################################
# ################################################################################################################################

def _publish_share(backend:'SQLPubSubBackend', topic_names:'strlist', publisher_index:'int') -> 'None':
    """ What one publisher greenlet runs - its share of the measured messages,
    round-robin over all the channels, with every twentieth message carrying
    the large embedded-document payload.
    """
    share, remainder = divmod(_message_count, _publisher_greenlet_count)

    # The remainder of the division goes to the first publishers, one message each,
    # so all the shares add up to the total.
    if publisher_index < remainder:
        share += 1

    for message_index in range(share):
        sequence = publisher_index * share + message_index
        topic_name = topic_names[sequence % _topic_count]

        if sequence % _large_payload_every == 0:
            payload = _large_payload
        else:
            payload = _small_payload

        _ = backend.publish(topic_name, payload)

# ################################################################################################################################

def run_backbone_scenario() -> 'None':
    """ The enterprise backbone - a thousand channels with three subscribers each,
    all active at once, sustained mixed-size traffic with every twentieth message
    carrying an embedded document. The run begins mid-stream, with a small backlog
    already pending in every queue, because a backbone is never idle. The shared
    rate floors must hold across the whole population.
    """
    set_progress_context('backbone', _publisher_greenlet_count, _topic_count * _subscribers_per_topic)

    # Seed the backlog before any consumer exists ..
    seed_seconds = seed_backlog(
        topic_count=_topic_count,
        messages_per_topic=_backlog_per_topic,
        topic_prefix='perf.backbone',
        sub_key_prefix='zpsk.perf.backbone',
        subscribers_per_topic=_subscribers_per_topic,
    )
    backlog_deliveries = _topic_count * _backlog_per_topic * _subscribers_per_topic
    print(f'Seeded {intcomma(backlog_deliveries)} backlog deliveries in {seed_seconds:.2f}s')

    backend = SQLPubSubBackend()

    # .. every channel feeds its own few subscribers ..
    topic_names:'strlist' = []
    sub_keys:'strlist' = []

    for topic_index in range(_topic_count):
        topic_names.append(f'perf.backbone.{topic_index:04d}')

        for subscriber_index in range(_subscribers_per_topic):
            sub_keys.append(f'zpsk.perf.backbone.{topic_index:04d}.{subscriber_index:04d}')

    # .. every publish becomes one delivery per subscriber of its channel ..
    expected_deliveries = backlog_deliveries + _message_count * _subscribers_per_topic

    counters:'anydict' = {
        'delivered': 0,
        'expected': expected_deliveries,
    }

    # .. the clock starts now ..
    start = monotonic()

    consumer_greenlets:'anylist' = []

    for sub_key in sub_keys:
        consumer_greenlets.append(spawn(consume_until_done, backend, sub_key, counters, _consumer_block_ms))

    # .. now the publishers pump concurrently with the consumers ..
    publisher_greenlets:'anylist' = []

    for publisher_index in range(_publisher_greenlet_count):
        publisher_greenlets.append(spawn(_publish_share, backend, topic_names, publisher_index))

    # .. the publish rate is measured over the publishers' own window ..
    _ = joinall(publisher_greenlets, timeout=_deadline_seconds)

    publish_elapsed = monotonic() - start

    # .. wait until everything has been fetched and acknowledged everywhere.
    _ = joinall(consumer_greenlets, timeout=_deadline_seconds)

    elapsed = monotonic() - start

    delivered = counters['delivered']
    assert delivered == expected_deliveries, f'Expected {intcomma(expected_deliveries)} deliveries, got {intcomma(delivered)}'

    publish_rate = _message_count / publish_elapsed
    delivery_rate = delivered / elapsed

    assert publish_rate >= get_min_publish_rate(), f'Backbone publish rate too low: {intcomma(int(publish_rate))}/s'
    assert delivery_rate >= get_min_delivery_rate(), f'Backbone delivery rate too low: {intcomma(int(delivery_rate))}/s'

    print(f'Backbone: {intcomma(int(publish_rate))} publishes/s, {intcomma(int(delivery_rate))} deliveries/s')

# ################################################################################################################################
# ################################################################################################################################
