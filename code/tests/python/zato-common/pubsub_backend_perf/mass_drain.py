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
from common import Min_Delivery_Rate_Per_Second
from load import consume_until_done
from seeding import count_rows, seed_backlog
from zato.common.pubsub.sql.backend import SQLPubSubBackend

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The mass-recovery pattern - a shared outage, e.g. the whole downstream side
# or the network was gone, ends and every subscriber comes back at once,
# each with its own deep backlog, all draining simultaneously while
# publishers keep pumping fresh traffic into all the topics.
# How deep each backlog is comes in as a parameter - the main perf target
# runs the smaller scale and the dedicated mass target the bigger one.
_topic_count = 100

# The naming the seeded backlog uses
_topic_prefix = 'perf.massdrain'
_sub_key_prefix = 'zpsk.perf.massdrain'

# How many fresh messages are published concurrently with the mass drain,
# round-robin over all the topics
_fresh_message_count = 2000

# How many publisher greenlets pump concurrently
_publisher_greenlet_count = 2

# The payload every fresh message carries
_fresh_payload = 'massdrain-fresh-' + 'x' * 500

# How long one blocking fetch waits inside a consumer greenlet, in milliseconds
_consumer_block_ms = 2000

# ################################################################################################################################
# ################################################################################################################################

def _publish_share(backend:'SQLPubSubBackend', topic_names:'strlist', publisher_index:'int') -> 'None':
    """ What one publisher greenlet runs - its share of the fresh messages,
    round-robin over all the topics.
    """
    share = _fresh_message_count // _publisher_greenlet_count

    for message_index in range(share):
        topic_name = topic_names[(publisher_index * share + message_index) % _topic_count]
        _ = backend.publish(topic_name, _fresh_payload)

# ################################################################################################################################

def run_mass_drain_scenario(*, backlog_per_subscriber:'int', deadline_seconds:'int', min_publish_rate:'int') -> 'None':
    """ Mass drain under load - the outage was shared, so all one hundred subscribers
    come back at the same moment, each with its own deep backlog, and drain
    simultaneously while publishers keep pumping fresh traffic into every topic.
    The whole population must hold the delivery floor together, the publishers
    must hold the publish floor beside them, and every queue must reach zero.
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

    # .. the whole population owes the backlog plus the fresh traffic ..
    counters:'anydict' = {
        'delivered': 0,
        'expected': total_backlog + _fresh_message_count,
    }

    start = monotonic()

    # .. everyone comes back at the same moment ..
    consumer_greenlets:'anylist' = []

    for sub_key in sub_keys:
        consumer_greenlets.append(spawn(consume_until_done, backend, sub_key, counters, _consumer_block_ms))

    # .. and the publishers pump into every topic while the drain runs ..
    publisher_greenlets:'anylist' = []

    for publisher_index in range(_publisher_greenlet_count):
        publisher_greenlets.append(spawn(_publish_share, backend, topic_names, publisher_index))

    # .. the publish floor must hold while the whole population is draining ..
    _ = joinall(publisher_greenlets, timeout=deadline_seconds)

    publish_elapsed = monotonic() - start
    publish_rate = _fresh_message_count / publish_elapsed

    assert publish_rate >= min_publish_rate, f'Publish rate too low during mass drain: {publish_rate:.0f}/s'

    # .. and everything must eventually go through.
    _ = joinall(consumer_greenlets, timeout=deadline_seconds)

    elapsed = monotonic() - start

    delivered = counters['delivered']
    expected = counters['expected']
    assert delivered == expected, f'Expected to drain {expected} messages, got {delivered}'

    drain_rate = delivered / elapsed

    assert drain_rate >= Min_Delivery_Rate_Per_Second, f'Mass drain rate too low: {drain_rate:.0f}/s'

    # With every subscriber done there is nothing left in flight anywhere.
    assert count_rows('pubsub_delivery') == 0

    depths = backend.get_pending_depths(list(zip(sub_keys, topic_names)))

    for sub_key in sub_keys:
        assert depths[sub_key] == 0, f'Expected an empty queue for {sub_key}, got {depths[sub_key]}'

    message = f'Mass drain: {_topic_count} subscribers drained {delivered} messages at {drain_rate:.0f}/s'
    message += f' with {publish_rate:.0f} publishes/s concurrently'
    print(message)

# ################################################################################################################################
# ################################################################################################################################
