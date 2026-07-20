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
from common import set_progress_context, wait_until
from live_amqp.env import get_broker_address
from live_amqp.harness import PubSubAMQPHarness
from zato.common.facade import PubSubFacade
from zato.common.test.rabbitmq_ import declare_and_bind, get_queue_depth, publish_many_to_exchange
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strlist

    any_ = any_
    from zato.common.test.rabbitmq_ import RabbitMQProcess

# ################################################################################################################################
# ################################################################################################################################

# The outage-recovery pattern - a subscriber comes back after its downstream was out
# and must work off a deep backlog while publishers keep pumping into the same
# exchange and a healthy peer consumes the fresh traffic live.
_drainer_queue = 'perf.amqp.drain.queue.drainer'
_peer_queue = 'perf.amqp.drain.queue.peer'

# How deep the drainer's backlog is when it comes back.
_backlog_message_count = 50000

# How many fresh messages are published concurrently with the drain.
_fresh_message_count = 2000

# How many publisher greenlets pump concurrently.
_publisher_greenlet_count = 20

# The payload every message carries.
_payload = 'amqp-drain-' + 'x' * 500

# How long one blocking fetch waits inside a consumer, in seconds.
_drain_events_timeout = 1.0

# How many messages a consumer may hold unacked at a time.
_prefetch_count = 100

# ################################################################################################################################
# ################################################################################################################################

def _publish_share(facade:'PubSubFacade', topic_name:'str', publish_counters:'anydict', publisher_index:'int') -> 'None':
    """ What one publisher greenlet runs - its share of the fresh messages.
    """
    share, remainder = divmod(_fresh_message_count, _publisher_greenlet_count)

    # The remainder of the division goes to the first publishers, one message each,
    # so all the shares add up to the total.
    if publisher_index < remainder:
        share += 1

    for _ in range(share):
        _ = facade.publish(topic_name, _payload)
        publish_counters['count'] += 1

# ################################################################################################################################

def run_drain_scenario(broker:'RabbitMQProcess', min_publish_rate:'int', min_delivery_rate:'int') -> 'None':
    """ Drain under load - a subscriber back from an outage works off a 50,000-message
    backlog while publishers keep pumping fresh traffic into the same exchange and its
    healthy peer consumes that traffic live. The drain must hold the delivery floor
    with the publishers running concurrently, nothing may be lost and both queues
    must reach zero.
    """
    publish_topic = 'perf.amqp.drain.publish'
    outconn_name = 'perf.amqp.drain.outconn'
    exchange = 'perf.amqp.drain.exchange'
    routing_key = 'perf.amqp.drain.key'

    drainer_topic = 'perf.amqp.drain.topic.drainer'
    drainer_channel = 'perf.amqp.drain.channel.drainer'
    peer_topic = 'perf.amqp.drain.topic.peer'
    peer_channel = 'perf.amqp.drain.channel.peer'

    harness = PubSubAMQPHarness(get_broker_address(broker), 'pubsub-amqp-perf')

    publish_counters:'anydict' = {'count': 0}
    set_progress_context('drain', publish_counters, harness)

    # The drainer owes everything - the backlog plus the fresh traffic -
    # while the healthy peer owes only the fresh traffic.
    expected_deliveries = _backlog_message_count + _fresh_message_count + _fresh_message_count

    try:
        # Both queues receive whatever is published to the shared exchange ..
        declare_and_bind(broker.amqp_url, exchange, _drainer_queue, routing_key)
        declare_and_bind(broker.amqp_url, exchange, _peer_queue, routing_key)

        # .. the backlog the outage left behind goes into the drainer's queue only,
        # .. as a batch through the default exchange ..
        seed_start = monotonic()
        bodies:'strlist' = []

        for _ in range(_backlog_message_count):
            bodies.append(_payload)

        publish_many_to_exchange(broker.amqp_url, '', _drainer_queue, bodies)

        seed_seconds = monotonic() - seed_start
        print(f'Seeded {intcomma(_backlog_message_count)} backlog messages in {seed_seconds:.2f}s')

        # .. each queue has its own channel, topic and push subscriber ..
        harness.add_service_push_subscription(drainer_topic, 'zpsk.rest.perf.drain.drainer', 'perf.push-service')
        harness.add_service_push_subscription(peer_topic, 'zpsk.rest.perf.drain.peer', 'perf.push-service')

        _ = harness.register_amqp_topic(drainer_topic, channel_name=drainer_channel)
        _ = harness.register_amqp_topic(peer_topic, channel_name=peer_channel)

        # .. the publishers go through the real outgoing connection ..
        _ = harness.create_outconn(outconn_name)
        _ = harness.register_amqp_topic(publish_topic, outconn_name=outconn_name, exchange=exchange, routing_key=routing_key)

        facade = PubSubFacade(cast_('any_', harness.server), 'perf.publishing-service')

        # .. the drain starts the moment the channels come up, so the clock starts first.
        start = monotonic()

        for channel_name, queue in ((drainer_channel, _drainer_queue), (peer_channel, _peer_queue)):
            _ = harness.create_channel(
                channel_name,
                queue,
                'perf.channel-service',
                prefetch_count=_prefetch_count,
                drain_events_timeout=_drain_events_timeout,
            )

        # The publishers pump concurrently with the drain from the very start ..
        publisher_greenlets:'anylist' = []
        for publisher_index in range(_publisher_greenlet_count):
            publisher_greenlets.append(spawn(_publish_share, facade, publish_topic, publish_counters, publisher_index))

        # .. the publish floor must hold while the drain is running ..
        _ = joinall(publisher_greenlets, raise_error=True)

        publish_elapsed = monotonic() - start
        publish_rate = _fresh_message_count / publish_elapsed

        assert publish_rate >= min_publish_rate, f'Publish rate too low during drain: {intcomma(int(publish_rate))}/s'

        # .. and everything must eventually go through.
        def _all_delivered() -> 'bool':
            return len(harness.server.service_invocations) == expected_deliveries

        wait_until(_all_delivered, 'the backlog and the fresh traffic were fully delivered')

        elapsed = monotonic() - start
        drain_rate = expected_deliveries / elapsed

        assert drain_rate >= min_delivery_rate, f'Drain rate too low under load: {intcomma(int(drain_rate))}/s'

        # Everything was acked, so both queues are empty.
        for queue in (_drainer_queue, _peer_queue):
            depth = get_queue_depth(broker.amqp_url, queue)
            assert depth == 0, f'Queue `{queue}` still holds {intcomma(depth)} messages'

        print(f'Drained {intcomma(expected_deliveries)} messages at {intcomma(int(drain_rate))}/s ' + \
            f'with {intcomma(int(publish_rate))} publishes/s concurrently')

    finally:
        harness.stop()

# ################################################################################################################################
# ################################################################################################################################
