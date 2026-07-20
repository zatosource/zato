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
from perf import measure_median_seconds, Max_Operation_Seconds
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

# How many messages the publish run pumps through the real outgoing connection.
_publish_message_count = 2000

# How many publisher greenlets pump concurrently.
_publisher_greenlet_count = 20

# How many single publishes the latency measurement runs.
_latency_iterations = 50

# How many channels the delivery run consumes through.
_delivery_channel_count = 20

# How many messages each channel's queue holds when consumption starts.
_delivery_messages_per_queue = 500

# The payloads are small request envelopes.
_payload = 'amqp-perf-' + 'x' * 500

# How long one blocking fetch waits inside a consumer, in seconds.
_drain_events_timeout = 1.0

# How many messages a consumer may hold unacked at a time.
_prefetch_count = 100

# ################################################################################################################################
# ################################################################################################################################

def _publish_share(facade:'PubSubFacade', topic_name:'str', publish_counters:'anydict', publisher_index:'int') -> 'None':
    """ What one publisher greenlet runs - its share of the measured messages.
    """
    share, remainder = divmod(_publish_message_count, _publisher_greenlet_count)

    # The remainder of the division goes to the first publishers, one message each,
    # so all the shares add up to the total.
    if publisher_index < remainder:
        share += 1

    for _ in range(share):
        _ = facade.publish(topic_name, _payload)
        publish_counters['count'] += 1

# ################################################################################################################################

def run_publish_scenario(broker:'RabbitMQProcess', min_publish_rate:'int') -> 'None':
    """ Publish throughput - concurrent publishers going through the real outgoing
    connection must sustain the publish floor, and a single publish, the user-visible
    operation, must complete within the operation budget.
    """
    topic_name = 'perf.amqp.publish.topic'
    outconn_name = 'perf.amqp.publish.outconn'
    exchange = 'perf.amqp.publish.exchange'
    queue = 'perf.amqp.publish.queue'
    routing_key = 'perf.amqp.publish.key'

    harness = PubSubAMQPHarness(get_broker_address(broker), 'pubsub-amqp-perf')

    publish_counters:'anydict' = {'count': 0}
    set_progress_context('publish', publish_counters, harness)

    try:
        declare_and_bind(broker.amqp_url, exchange, queue, routing_key)

        _ = harness.create_outconn(outconn_name)
        _ = harness.register_amqp_topic(topic_name, outconn_name=outconn_name, exchange=exchange, routing_key=routing_key)

        facade = PubSubFacade(cast_('any_', harness.server), 'perf.publishing-service')

        # A single publish is the user-visible operation whose latency is measured ..
        def _publish_once() -> 'None':
            _ = facade.publish(topic_name, _payload)

        median = measure_median_seconds(_publish_once, _latency_iterations)
        assert median <= Max_Operation_Seconds, f'Publish median too slow: {median * 1000:.2f} ms'

        # .. and the concurrent publishers must hold the rate floor.
        start = monotonic()

        publisher_greenlets:'anylist' = []
        for publisher_index in range(_publisher_greenlet_count):
            publisher_greenlets.append(spawn(_publish_share, facade, topic_name, publish_counters, publisher_index))

        _ = joinall(publisher_greenlets, raise_error=True)

        elapsed = monotonic() - start
        publish_rate = _publish_message_count / elapsed

        assert publish_rate >= min_publish_rate, f'Publish rate too low: {intcomma(int(publish_rate))}/s'

        # Everything that was published reached the broker.
        expected_depth = _latency_iterations + _publish_message_count
        depth = get_queue_depth(broker.amqp_url, queue)
        assert depth == expected_depth, f'Expected {intcomma(expected_depth)} messages on the broker, got {intcomma(depth)}'

        print(f'Publish: {intcomma(int(publish_rate))} publishes/s, median {median * 1000:.2f} ms')

    finally:
        harness.stop()

# ################################################################################################################################

def run_delivery_scenario(broker:'RabbitMQProcess', min_delivery_rate:'int') -> 'None':
    """ Delivery throughput - backlogs on many queues consumed by real channels
    and pushed to service subscribers must sustain the delivery floor.
    """
    exchange = 'perf.amqp.delivery.exchange'

    harness = PubSubAMQPHarness(get_broker_address(broker), 'pubsub-amqp-perf')

    publish_counters:'anydict' = {'count': 0}
    set_progress_context('delivery', publish_counters, harness)

    expected_deliveries = _delivery_channel_count * _delivery_messages_per_queue

    try:
        # Every channel gets its own queue with a seeded backlog ..
        queue_names:'strlist' = []

        for channel_index in range(_delivery_channel_count):
            queue = f'perf.amqp.delivery.queue.{channel_index:04d}'
            queue_names.append(queue)

            declare_and_bind(broker.amqp_url, exchange, queue, queue)

        # .. the backlog goes in as a batch, one connection for all of it ..
        seed_start = monotonic()
        bodies:'strlist' = []

        for _ in range(_delivery_messages_per_queue):
            bodies.append(_payload)

        for queue in queue_names:
            publish_many_to_exchange(broker.amqp_url, exchange, queue, bodies)

        seed_seconds = monotonic() - seed_start
        print(f'Seeded {intcomma(expected_deliveries)} messages in {seed_seconds:.2f}s')

        # .. each channel consumes for its own topic with one push subscriber ..
        for channel_index, queue in enumerate(queue_names):
            topic_name = f'perf.amqp.delivery.topic.{channel_index:04d}'
            channel_name = f'perf.amqp.delivery.channel.{channel_index:04d}'
            sub_key = f'zpsk.rest.perf.delivery.{channel_index:04d}'

            harness.add_service_push_subscription(topic_name, sub_key, 'perf.push-service')
            _ = harness.register_amqp_topic(topic_name, channel_name=channel_name)

        # .. consumption starts the moment the channels come up, so the clock starts first.
        start = monotonic()

        for channel_index, queue in enumerate(queue_names):
            channel_name = f'perf.amqp.delivery.channel.{channel_index:04d}'
            _ = harness.create_channel(
                channel_name,
                queue,
                'perf.channel-service',
                prefetch_count=_prefetch_count,
                drain_events_timeout=_drain_events_timeout,
            )

        def _all_delivered() -> 'bool':
            return len(harness.server.service_invocations) == expected_deliveries

        wait_until(_all_delivered, 'every backlog message reached its push subscriber')

        elapsed = monotonic() - start
        delivery_rate = expected_deliveries / elapsed

        assert delivery_rate >= min_delivery_rate, f'Delivery rate too low: {intcomma(int(delivery_rate))}/s'

        # Everything was acked, so every queue is empty.
        for queue in queue_names:
            depth = get_queue_depth(broker.amqp_url, queue)
            assert depth == 0, f'Queue `{queue}` still holds {intcomma(depth)} messages'

        print(f'Delivery: {intcomma(int(delivery_rate))} deliveries/s')

    finally:
        harness.stop()

# ################################################################################################################################
# ################################################################################################################################
