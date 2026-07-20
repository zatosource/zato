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
from zato.common.test.rabbitmq_ import declare_and_bind, get_queue_depth
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strlist

    any_ = any_
    from zato.common.test.rabbitmq_ import RabbitMQProcess

# ################################################################################################################################
# ################################################################################################################################

# The broadcast pattern - a fanout exchange copies every publish
# to all the queues bound to it.
_subscriber_count = 10

# How many messages are published in the measured run - each one becomes
# _subscriber_count deliveries.
_message_count = 1000

# How many publisher greenlets pump concurrently with the consumers.
_publisher_greenlet_count = 20

# The payloads are small request envelopes.
_payload = 'amqp-fanout-' + 'x' * 500

# How long one blocking fetch waits inside a consumer, in seconds.
_drain_events_timeout = 1.0

# How many messages a consumer may hold unacked at a time.
_prefetch_count = 100

# ################################################################################################################################
# ################################################################################################################################

def _publish_share(facade:'PubSubFacade', topic_name:'str', publish_counters:'anydict', publisher_index:'int') -> 'None':
    """ What one publisher greenlet runs - its share of the measured messages.
    """
    share, remainder = divmod(_message_count, _publisher_greenlet_count)

    # The remainder of the division goes to the first publishers, one message each,
    # so all the shares add up to the total.
    if publisher_index < remainder:
        share += 1

    for _ in range(share):
        _ = facade.publish(topic_name, _payload)
        publish_counters['count'] += 1

# ################################################################################################################################

def run_fanout_scenario(broker:'RabbitMQProcess', min_publish_rate:'int', min_delivery_rate:'int') -> 'None':
    """ Broadcast fan-out - a fanout exchange copies every publish to ten bound queues,
    each consumed by a real channel pushing to its subscriber, so the delivery side
    must sustain ten times the publish rate.
    """
    publish_topic = 'perf.amqp.fanout.publish'
    outconn_name = 'perf.amqp.fanout.outconn'
    exchange = 'perf.amqp.fanout.exchange'
    routing_key = 'perf.amqp.fanout.key'

    harness = PubSubAMQPHarness(get_broker_address(broker), 'pubsub-amqp-perf')

    publish_counters:'anydict' = {'count': 0}
    set_progress_context('fanout', publish_counters, harness)

    expected_deliveries = _message_count * _subscriber_count

    try:
        # Every subscriber gets its own queue on the fanout exchange,
        # its own channel and its own topic ..
        queue_names:'strlist' = []

        for subscriber_index in range(_subscriber_count):
            queue = f'perf.amqp.fanout.queue.{subscriber_index:04d}'
            queue_names.append(queue)

            declare_and_bind(broker.amqp_url, exchange, queue, routing_key, exchange_type='fanout')

            topic_name = f'perf.amqp.fanout.topic.{subscriber_index:04d}'
            channel_name = f'perf.amqp.fanout.channel.{subscriber_index:04d}'
            sub_key = f'zpsk.rest.perf.fanout.{subscriber_index:04d}'

            harness.add_service_push_subscription(topic_name, sub_key, 'perf.push-service')
            _ = harness.register_amqp_topic(topic_name, channel_name=channel_name)

            _ = harness.create_channel(
                channel_name,
                queue,
                'perf.channel-service',
                prefetch_count=_prefetch_count,
                drain_events_timeout=_drain_events_timeout,
            )

        # .. the publishers go through the real outgoing connection ..
        _ = harness.create_outconn(outconn_name)
        _ = harness.register_amqp_topic(publish_topic, outconn_name=outconn_name, exchange=exchange, routing_key=routing_key)

        facade = PubSubFacade(cast_('any_', harness.server), 'perf.publishing-service')

        start = monotonic()

        publisher_greenlets:'anylist' = []
        for publisher_index in range(_publisher_greenlet_count):
            publisher_greenlets.append(spawn(_publish_share, facade, publish_topic, publish_counters, publisher_index))

        # .. the publish rate is measured over the publishers' own window ..
        _ = joinall(publisher_greenlets, raise_error=True)

        publish_elapsed = monotonic() - start
        publish_rate = _message_count / publish_elapsed

        assert publish_rate >= min_publish_rate, f'Fan-out publish rate too low: {intcomma(int(publish_rate))}/s'

        # .. and every broadcast must reach every subscriber.
        def _all_delivered() -> 'bool':
            return len(harness.server.service_invocations) == expected_deliveries

        wait_until(_all_delivered, 'every broadcast reached every subscriber')

        elapsed = monotonic() - start
        delivery_rate = expected_deliveries / elapsed

        assert delivery_rate >= min_delivery_rate, f'Fan-out delivery rate too low: {intcomma(int(delivery_rate))}/s'

        # Everything was acked, so every queue is empty.
        for queue in queue_names:
            depth = get_queue_depth(broker.amqp_url, queue)
            assert depth == 0, f'Queue `{queue}` still holds {intcomma(depth)} messages'

        print(f'Fan-out: {intcomma(int(publish_rate))} publishes/s, {intcomma(int(delivery_rate))} deliveries/s')

    finally:
        harness.stop()

# ################################################################################################################################
# ################################################################################################################################
