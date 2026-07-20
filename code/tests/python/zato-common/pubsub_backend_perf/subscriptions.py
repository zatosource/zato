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
from seeding import delete_all_rows
from zato.common.pubsub.sql.backend import SQLPubSubBackend

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The subscription-API pattern - external client applications register interest
# in record types and are pushed a message whenever a matching record changes,
# replacing polling. Two hundred concurrent subscribers spread over fifty types.
_topic_count = 50

# How many subscriber applications every record type has.
_subscribers_per_topic = 4

# How many messages are published in the measured run.
_message_count = 1000

# How many publisher greenlets pump concurrently with the consumers.
_publisher_greenlet_count = 30

# The three payload tiers real subscription traffic comes in -
# most notifications carry one record ..
_single_record_payload = 'record-' + 'x' * 2000

# .. one in five carries a batch of records ..
_batch_payload = 'batch-' + 'x' * 50000
_batch_every = 5

# .. and one in fifty carries a full profile bundle.
_bundle_payload = 'bundle-' + 'x' * 2300000
_bundle_every = 50

# How long one blocking fetch waits inside a consumer greenlet, in milliseconds.
_consumer_block_ms = 2000

# How long the whole run may take at most before it is declared hung, in seconds.
_deadline_seconds = 120

# ################################################################################################################################
# ################################################################################################################################

def _publish_share(backend:'SQLPubSubBackend', topic_names:'strlist', publisher_index:'int') -> 'None':
    """ What one publisher greenlet runs - its share of the measured messages,
    round-robin over all the record types, with the three payload tiers
    interleaved the way real subscription traffic is.
    """
    share, remainder = divmod(_message_count, _publisher_greenlet_count)

    # The remainder of the division goes to the first publishers, one message each,
    # so all the shares add up to the total.
    if publisher_index < remainder:
        share += 1

    for message_index in range(share):
        sequence = publisher_index * share + message_index
        topic_name = topic_names[sequence % _topic_count]

        # The rarest tier wins when the counters coincide ..
        if sequence % _bundle_every == 0:
            payload = _bundle_payload
        elif sequence % _batch_every == 0:
            payload = _batch_payload
        else:
            payload = _single_record_payload

        # .. and the message is published with the payload selected above.
        _ = backend.publish(topic_name, payload)

# ################################################################################################################################

def run_subscriptions_scenario() -> 'None':
    """ Concurrent API subscriptions - two hundred subscriber applications over fifty
    record types, pushed a message on every record change, with the three payload tiers
    of real subscription traffic - single records, batches and multi-megabyte bundles -
    all flowing through the same delivery path. The shared rate floors must hold.
    """
    set_progress_context('subscriptions', _publisher_greenlet_count, _topic_count * _subscribers_per_topic)

    delete_all_rows()

    backend = SQLPubSubBackend()

    # Every record type feeds its own group of subscriber applications ..
    topic_names:'strlist' = []
    sub_keys:'strlist' = []

    for topic_index in range(_topic_count):
        topic_name = f'perf.subscriptions.{topic_index:04d}'
        topic_names.append(topic_name)

        for subscriber_index in range(_subscribers_per_topic):
            sub_key = f'zpsk.perf.subscriptions.{topic_index:04d}.{subscriber_index:04d}'
            sub_keys.append(sub_key)
            backend.subscribe(sub_key, topic_name)

    # .. every record change becomes one delivery per subscriber of its type ..
    expected_deliveries = _message_count * _subscribers_per_topic

    counters:'anydict' = {
        'delivered': 0,
        'expected': expected_deliveries,
    }

    start = monotonic()

    # .. consumers first, so they are already waiting when the first publish lands ..
    consumer_greenlets:'anylist' = []

    for sub_key in sub_keys:
        consumer_greenlets.append(spawn(consume_until_done, backend, sub_key, counters, _consumer_block_ms))

    # .. now the publishers pump concurrently with the consumers ..
    publisher_greenlets:'anylist' = []

    for publisher_index in range(_publisher_greenlet_count):
        publisher_greenlets.append(spawn(_publish_share, backend, topic_names, publisher_index))

    # .. the publish floor is measured over the publish phase - it must hold
    # .. with the consumers running concurrently ..
    _ = joinall(publisher_greenlets, timeout=_deadline_seconds)

    publish_elapsed = monotonic() - start

    # .. and wait until every notification has been fetched and acknowledged everywhere.
    _ = joinall(consumer_greenlets, timeout=_deadline_seconds)

    elapsed = monotonic() - start

    delivered = counters['delivered']
    assert delivered == expected_deliveries, f'Expected {intcomma(expected_deliveries)} deliveries, got {intcomma(delivered)}'

    publish_rate = _message_count / publish_elapsed
    delivery_rate = delivered / elapsed

    assert publish_rate >= get_min_publish_rate(), f'Subscriptions publish rate too low: {intcomma(int(publish_rate))}/s'
    assert delivery_rate >= get_min_delivery_rate(), f'Subscriptions delivery rate too low: {intcomma(int(delivery_rate))}/s'

    print(f'Subscriptions: {intcomma(int(publish_rate))} publishes/s, {intcomma(int(delivery_rate))} deliveries/s')

# ################################################################################################################################
# ################################################################################################################################
