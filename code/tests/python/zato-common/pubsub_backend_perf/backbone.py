# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# gevent
from gevent import joinall, sleep, spawn

# humanize
from humanize import intcomma

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

# The backbone pattern - one broker carries every event of a whole organization:
# a thousand distinct channels, each with a handful of subscribers, sustained
# mixed-size traffic across all of them at once.
_topic_count = 1000

# How many subscribers every channel has - fan-out stays low on a backbone,
# each channel feeds only the few systems that need it
_subscribers_per_topic = 3

# How many messages are published in the measured run, spread over all the channels
_message_count = 2000

# How many publisher greenlets pump concurrently with the consumers
_publisher_greenlet_count = 5

# Most messages are small envelopes ..
_small_payload = 'backbone-' + 'x' * 1000

# .. but one in twenty carries an embedded document, the way real feeds do
_large_payload = 'backbone-large-' + 'x' * 46000
_large_payload_every = 20

# How long one blocking fetch waits inside a consumer greenlet, in milliseconds -
# long, because with three thousand consumers the timeout re-checks must stay rare
_consumer_block_ms = 5000

# How long the whole run may take at most before it is declared hung, in seconds
_deadline_seconds = 120

# How long the consumers get to finish their initial empty fetches and block
# on their wake-up events before the measured window opens, in seconds
_settle_seconds = 2

# ################################################################################################################################
# ################################################################################################################################

def _publish_share(backend:'SQLPubSubBackend', topic_names:'strlist', publisher_index:'int') -> 'None':
    """ What one publisher greenlet runs - its share of the measured messages,
    round-robin over all the channels, with every twentieth message carrying
    the large embedded-document payload.
    """
    share = _message_count // _publisher_greenlet_count

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
    carrying an embedded document. The shared rate floors must hold across
    the whole population.
    """
    set_progress_context('backbone', _publisher_greenlet_count, _topic_count * _subscribers_per_topic)

    delete_all_rows()

    backend = SQLPubSubBackend()

    # Every channel feeds its own few subscribers ..
    topic_names:'strlist' = []
    sub_keys:'strlist' = []

    for topic_index in range(_topic_count):
        topic_name = f'perf.backbone.{topic_index:04d}'
        topic_names.append(topic_name)

        for subscriber_index in range(_subscribers_per_topic):
            sub_key = f'zpsk.perf.backbone.{topic_index:04d}.{subscriber_index:04d}'
            sub_keys.append(sub_key)
            backend.subscribe(sub_key, topic_name)

    # .. every publish becomes one delivery per subscriber of its channel ..
    expected_deliveries = _message_count * _subscribers_per_topic

    counters:'anydict' = {
        'delivered': 0,
        'expected': expected_deliveries,
    }

    # .. consumers first - and with three thousand of them, the clock starts only
    # .. once they have all run their initial empty fetch and are blocking on their
    # .. wake-up events, because spawn cost is not what this scenario measures ..
    greenlets:'anylist' = []

    for sub_key in sub_keys:
        greenlets.append(spawn(consume_until_done, backend, sub_key, counters, _consumer_block_ms))

    sleep(_settle_seconds)
    start = monotonic()

    # .. now the publishers pump concurrently with the consumers ..
    for publisher_index in range(_publisher_greenlet_count):
        greenlets.append(spawn(_publish_share, backend, topic_names, publisher_index))

    # .. wait until everything has been fetched and acknowledged everywhere.
    _ = joinall(greenlets, timeout=_deadline_seconds)

    elapsed = monotonic() - start

    delivered = counters['delivered']
    assert delivered == expected_deliveries, f'Expected {intcomma(expected_deliveries)} deliveries, got {intcomma(delivered)}'

    publish_rate = _message_count / elapsed
    delivery_rate = delivered / elapsed

    assert publish_rate >= Min_Publish_Rate_Per_Second, f'Backbone publish rate too low: {intcomma(int(publish_rate))}/s'
    assert delivery_rate >= Min_Delivery_Rate_Per_Second, f'Backbone delivery rate too low: {intcomma(int(delivery_rate))}/s'

    print(f'Backbone: {intcomma(int(publish_rate))} publishes/s, {intcomma(int(delivery_rate))} deliveries/s')

# ################################################################################################################################
# ################################################################################################################################
