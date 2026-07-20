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
from seeding import count_payloads, seed_aged_queue
from zato.common.pubsub.sql.backend import SQLPubSubBackend

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

# The outage-recovery pattern - a subscriber comes back after its downstream was
# out for a day and must work off a deep backlog while publishers keep pumping
# into the same topic and a healthy peer consumes the fresh traffic live.
_topic_name = 'perf.drain.topic'

# The subscriber that was out and now drains its backlog.
_drainer_sub_key = 'zpsk.perf.drain.0000'

# The peer that stayed healthy the whole time.
_peer_sub_key = 'zpsk.perf.drain.0001'

# How deep the drainer's backlog is when it comes back.
_backlog_message_count = 50000

# How long the downstream outage lasted, in days.
_outage_days = 1

# How many fresh messages are published concurrently with the drain.
_fresh_message_count = 2000

# How many publisher greenlets pump concurrently.
_publisher_greenlet_count = 20

# The payload every fresh message carries.
_fresh_payload = 'drain-fresh-' + 'x' * 500

# How long one blocking fetch waits inside a consumer greenlet, in milliseconds.
_consumer_block_ms = 2000

# How long the whole run may take at most before it is declared hung, in seconds.
_deadline_seconds = 120

# ################################################################################################################################
# ################################################################################################################################

def _publish_share(backend:'SQLPubSubBackend', publisher_index:'int') -> 'None':
    """ What one publisher greenlet runs - its share of the fresh messages.
    """
    share, remainder = divmod(_fresh_message_count, _publisher_greenlet_count)

    # The remainder of the division goes to the first publishers, one message each,
    # so all the shares add up to the total.
    if publisher_index < remainder:
        share += 1

    for _ in range(share):
        _ = backend.publish(_topic_name, _fresh_payload)

# ################################################################################################################################

def run_drain_scenario() -> 'None':
    """ Drain under load - a subscriber back from a day-long outage works off
    a 50,000-message backlog while publishers keep pumping fresh traffic into
    the same topic and its healthy peer consumes that traffic live. The drain
    must hold the delivery floor with the publishers running concurrently,
    nothing may be lost and the queue must reach zero.
    """
    set_progress_context('drain', _publisher_greenlet_count, 2)

    backend = SQLPubSubBackend()

    # The backlog the outage left behind, pending only for the drainer ..
    seed_seconds = seed_aged_queue(
        topic_name=_topic_name,
        sub_keys=[_drainer_sub_key, _peer_sub_key],
        delivery_sub_keys=[_drainer_sub_key],
        message_count=_backlog_message_count,
        aged_days=_outage_days,
    )
    print(f'Seeded {intcomma(_backlog_message_count)} backlog messages in {seed_seconds:.2f}s')

    # .. the drainer owes everything - the backlog plus the fresh traffic ..
    drainer_counters:'anydict' = {
        'delivered': 0,
        'expected': _backlog_message_count + _fresh_message_count,
    }

    # .. while the healthy peer owes only the fresh traffic.
    peer_counters:'anydict' = {
        'delivered': 0,
        'expected': _fresh_message_count,
    }

    start = monotonic()

    # Both consumers run from the first moment ..
    consumer_greenlets:'anylist' = []
    consumer_greenlets.append(spawn(consume_until_done, backend, _drainer_sub_key, drainer_counters, _consumer_block_ms))
    consumer_greenlets.append(spawn(consume_until_done, backend, _peer_sub_key, peer_counters, _consumer_block_ms))

    # .. the publishers pump concurrently with the drain from the very start ..
    publisher_greenlets:'anylist' = []

    for publisher_index in range(_publisher_greenlet_count):
        publisher_greenlets.append(spawn(_publish_share, backend, publisher_index))

    # .. the publish floor must hold while the drain is running ..
    _ = joinall(publisher_greenlets, timeout=_deadline_seconds)

    publish_elapsed = monotonic() - start
    publish_rate = _fresh_message_count / publish_elapsed

    assert publish_rate >= get_min_publish_rate(), f'Publish rate too low during drain: {intcomma(int(publish_rate))}/s'

    # .. and everything must eventually go through.
    _ = joinall(consumer_greenlets, timeout=_deadline_seconds)

    elapsed = monotonic() - start

    drained = drainer_counters['delivered']
    expected = drainer_counters['expected']
    assert drained == expected, f'Expected to drain {intcomma(expected)} messages, got {intcomma(drained)}'

    peer_delivered = peer_counters['delivered']
    assert peer_delivered == _fresh_message_count, f'Expected {intcomma(_fresh_message_count)} peer deliveries, got {intcomma(peer_delivered)}'

    drain_rate = drained / elapsed

    assert drain_rate >= get_min_delivery_rate(), f'Drain rate too low under load: {intcomma(int(drain_rate))}/s'

    # With both subscribers done, no payload has a reason to stay and the queue is empty.
    assert count_payloads(_topic_name) == 0

    depths = backend.get_pending_depths([(_drainer_sub_key, _topic_name), (_peer_sub_key, _topic_name)])
    assert depths[_drainer_sub_key] == 0
    assert depths[_peer_sub_key] == 0

    print(f'Drained {intcomma(drained)} messages at {intcomma(int(drain_rate))}/s with {intcomma(int(publish_rate))} publishes/s concurrently')

# ################################################################################################################################
# ################################################################################################################################
