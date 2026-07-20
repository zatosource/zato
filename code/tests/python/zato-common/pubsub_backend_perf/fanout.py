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
from common import is_ssl_enabled, set_progress_context
from load import consume_until_done
from seeding import delete_all_rows
from zato.common.pubsub.sql.backend import SQLPubSubBackend

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The broadcast pattern - every published request goes out to all the peers
# of its topic at once, e.g. a federated network where a lookup is broadcast
# because no single peer is known to hold the answer.
_topic_count = 20

# How many subscribers every topic broadcasts to.
_subscribers_per_topic = 10

# How many messages are published in the measured run - each one becomes
# _subscribers_per_topic deliveries.
_message_count = 1000

# How many publisher greenlets pump concurrently with the consumers.
_publisher_greenlet_count = 20

# The payloads are small request envelopes.
_payload = 'fanout-' + 'x' * 500

# The rates the run must sustain - the publish floor is the standard one,
# the delivery floor is above it because fan-out multiplies every publish tenfold.
_min_publish_rate = 100
_min_delivery_rate = 700

# The floors of runs whose database connection uses SSL.
_min_publish_rate_ssl = 90
_min_delivery_rate_ssl = 630

# How long one blocking fetch waits inside a consumer greenlet, in milliseconds.
_consumer_block_ms = 2000

# How long the whole run may take at most before it is declared hung, in seconds.
_deadline_seconds = 60

# ################################################################################################################################
# ################################################################################################################################

def _publish_share(backend:'SQLPubSubBackend', topic_names:'strlist', publisher_index:'int') -> 'None':
    """ What one publisher greenlet runs - its share of the measured messages,
    round-robin over all the topics.
    """
    share, remainder = divmod(_message_count, _publisher_greenlet_count)

    # The remainder of the division goes to the first publishers, one message each,
    # so all the shares add up to the total.
    if publisher_index < remainder:
        share += 1

    for message_index in range(share):
        topic_name = topic_names[(publisher_index * share + message_index) % _topic_count]
        _ = backend.publish(topic_name, _payload)

# ################################################################################################################################

def run_fanout_scenario() -> 'None':
    """ Broadcast fan-out - every publish is delivered to all ten subscribers of its topic,
    so the delivery side must sustain ten times the publish rate. The publish floor stays
    at the standard one while the delivery floor rises to 700 a second.
    """
    set_progress_context('fanout', _publisher_greenlet_count, _topic_count * _subscribers_per_topic)

    delete_all_rows()

    backend = SQLPubSubBackend()

    # Every topic broadcasts to its own group of subscribers ..
    topic_names:'strlist' = []
    sub_keys:'strlist' = []

    for topic_index in range(_topic_count):
        topic_name = f'perf.fanout.{topic_index:04d}'
        topic_names.append(topic_name)

        for subscriber_index in range(_subscribers_per_topic):
            sub_key = f'zpsk.perf.fanout.{topic_index:04d}.{subscriber_index:04d}'
            sub_keys.append(sub_key)
            backend.subscribe(sub_key, topic_name)

    # .. every publish becomes one delivery per subscriber of its topic ..
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

    # .. the publish rate is measured over the publishers' own window ..
    _ = joinall(publisher_greenlets, timeout=_deadline_seconds)

    publish_elapsed = monotonic() - start

    # .. wait until every broadcast has been fetched and acknowledged everywhere.
    _ = joinall(consumer_greenlets, timeout=_deadline_seconds)

    elapsed = monotonic() - start

    delivered = counters['delivered']
    assert delivered == expected_deliveries, f'Expected {intcomma(expected_deliveries)} deliveries, got {intcomma(delivered)}'

    publish_rate = _message_count / publish_elapsed
    delivery_rate = delivered / elapsed

    if is_ssl_enabled():
        min_publish_rate = _min_publish_rate_ssl
        min_delivery_rate = _min_delivery_rate_ssl
    else:
        min_publish_rate = _min_publish_rate
        min_delivery_rate = _min_delivery_rate

    assert publish_rate >= min_publish_rate, f'Fan-out publish rate too low: {intcomma(int(publish_rate))}/s'
    assert delivery_rate >= min_delivery_rate, f'Fan-out delivery rate too low: {intcomma(int(delivery_rate))}/s'

    print(f'Fan-out: {intcomma(int(publish_rate))} publishes/s, {intcomma(int(delivery_rate))} deliveries/s')

# ################################################################################################################################
# ################################################################################################################################
