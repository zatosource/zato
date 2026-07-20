# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# gevent
from gevent import sleep

# SQLAlchemy
from sqlalchemy import select

# Zato
from live_amqp.env import get_broker_address
from live_amqp.harness import PubSubAMQPHarness, RESTPushListener
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditOutcome
from zato.common.facade import PubSubFacade
from zato.common.test.rabbitmq_ import declare_and_bind, drain_queue, get_queue_depth, publish_to_exchange
from zato.common.typing_ import cast_
from zato.server.base.config_manager import _pubsub_amqp_bridge_service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_, dictlist
    from zato.common.test.rabbitmq_ import RabbitMQProcess

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# The name every harness registers its audit events under.
_server_name = 'pubsub-amqp-contract'

# The service that publishes through the facade.
_publishing_service = 'contract.publishing-service'

# How long a wait for an asynchronous condition may take before the scenario fails, in seconds.
_wait_deadline_seconds = 10

# How often a wait checks its condition, in seconds.
_wait_poll_seconds = 0.05

# How long a queue drain waits to prove that nothing extra arrives, in seconds.
_drain_seconds = 2

# ################################################################################################################################
# ################################################################################################################################

def get_audit_events(topic_name:'str') -> 'dictlist':
    """ Returns all the audit events of one topic, oldest first.
    """
    engine = get_audit_engine()

    query = select(
        event_table.c.event_type,
        event_table.c.endpoint,
        event_table.c.sub_key,
        event_table.c.outcome,
        event_table.c.msg_id,
        event_table.c.cid,
    )
    query = query.where(event_table.c.object_name == topic_name)
    query = query.order_by(event_table.c.id)

    with engine.connect() as connection:
        rows = connection.execute(query).mappings().all()

    out:'dictlist' = []
    for row in rows:
        out.append(dict(row))

    return out

# ################################################################################################################################

def wait_until(condition:'callable_', description:'str') -> 'None':
    """ Waits until an asynchronous condition holds, failing the scenario after the deadline.
    """
    deadline = monotonic() + _wait_deadline_seconds

    while not condition():
        if monotonic() > deadline:
            raise Exception(f'Condition not met within {_wait_deadline_seconds}s -> {description}')
        sleep(_wait_poll_seconds)

# ################################################################################################################################
# ################################################################################################################################

def run_outconn_publish_scenario(broker:'RabbitMQProcess') -> 'None':
    """ A facade publish to an AMQP-backed topic goes through the real outgoing connection
    to the broker, returns the standard result shape and writes a Published audit event.
    """
    topic_name = 'topic.amqp.contract.publish'
    outconn_name = 'pubsub.contract.outconn'
    exchange = 'pubsub.contract.publish.exchange'
    queue = 'pubsub.contract.publish.queue'
    routing_key = 'pubsub.contract.publish.key'
    cid = 'contract-publish-cid-1'

    harness = PubSubAMQPHarness(get_broker_address(broker), _server_name)

    try:
        # The queue an external consumer would read from ..
        declare_and_bind(broker.amqp_url, exchange, queue, routing_key)

        # .. the real connector with its producer pool ..
        _ = harness.create_outconn(outconn_name)

        # .. an AMQP-backed topic pointing at that outgoing connection ..
        _ = harness.register_amqp_topic(topic_name, outconn_name=outconn_name, exchange=exchange, routing_key=routing_key)

        # .. what a service's self.pubsub.publish call runs ..
        facade = PubSubFacade(cast_('any_', harness.server), _publishing_service)
        result = facade.publish(topic_name, 'contract publish payload', cid=cid)

        # .. the result shape is the standard one ..
        assert result.msg_id.startswith('zpsm.'), f'Unexpected msg_id -> {result.msg_id}'

        # .. the message reached the broker ..
        messages = drain_queue(broker.amqp_url, queue, timeout=_drain_seconds)
        assert messages == ['contract publish payload'], f'Unexpected messages -> {messages}'

        # .. and the publish left exactly one audit event with the same identifiers.
        events = get_audit_events(topic_name)
        assert len(events) == 1, f'Expected one audit event, got {events}'

        event = events[0]
        assert event['event_type'] == AuditEvent.Published
        assert event['outcome'] == AuditOutcome.OK
        assert event['msg_id'] == result.msg_id
        assert event['cid'] == cid
        assert event['endpoint'] == f'{outconn_name} -> {exchange} -> {routing_key}'

    finally:
        harness.stop()

# ################################################################################################################################

def run_inbound_delivery_scenario(broker:'RabbitMQProcess') -> 'None':
    """ A message consumed from an AMQP channel reaches both a service push subscriber
    and a REST push subscriber, is acked on the broker and leaves Delivered audit events.
    """
    topic_name = 'topic.amqp.contract.inbound'
    channel_name = 'pubsub.contract.inbound.channel'
    exchange = 'pubsub.contract.inbound.exchange'
    queue = 'pubsub.contract.inbound.queue'
    routing_key = 'pubsub.contract.inbound.key'
    service_sub_key = 'zpsk.rest.contract.inbound.service'
    rest_sub_key = 'zpsk.rest.contract.inbound.rest'
    push_service = 'contract.push-service'

    harness = PubSubAMQPHarness(get_broker_address(broker), _server_name)

    listener = RESTPushListener()
    listener.start()

    try:
        # The queue external producers publish into ..
        declare_and_bind(broker.amqp_url, exchange, queue, routing_key)

        # .. a real channel consuming from it ..
        _ = harness.create_channel(channel_name, queue, 'contract.channel-service')

        # .. the topic that consumes from that channel ..
        _ = harness.register_amqp_topic(topic_name, channel_name=channel_name)

        # .. one subscriber of each push type ..
        harness.add_service_push_subscription(topic_name, service_sub_key, push_service)
        harness.add_rest_push_subscription(topic_name, rest_sub_key, listener.url)

        # .. an external producer publishes to the broker ..
        publish_to_exchange(broker.amqp_url, exchange, routing_key, 'contract inbound payload')

        # .. both subscribers eventually receive the message ..
        def _both_delivered() -> 'bool':
            return len(harness.server.service_invocations) == 1 and len(listener.received) == 1

        wait_until(_both_delivered, 'both push subscribers received the message')

        invocation = harness.server.service_invocations[0]
        assert invocation['service_name'] == push_service
        assert invocation['request'] == 'contract inbound payload'

        assert listener.received == [b'contract inbound payload'], f'Unexpected REST bodies -> {listener.received}'

        # .. the message was acked, so the queue is empty ..
        def _queue_empty() -> 'bool':
            return get_queue_depth(broker.amqp_url, queue) == 0

        wait_until(_queue_empty, 'the consumed message was acked')

        # .. the channel's own service never ran - the topic's override took the message ..
        assert harness.channel_invocations == [], f'Unexpected channel invocations -> {harness.channel_invocations}'

        # .. and both deliveries left audit events, one per subscriber.
        events = get_audit_events(topic_name)
        assert len(events) == 2, f'Expected two audit events, got {events}'

        sub_keys = []
        for event in events:
            assert event['event_type'] == AuditEvent.Delivered
            assert event['outcome'] == AuditOutcome.OK
            sub_keys.append(event['sub_key'])

        assert sorted(sub_keys) == sorted([service_sub_key, rest_sub_key]), f'Unexpected sub_keys -> {sub_keys}'

    finally:
        listener.stop()
        harness.stop()

# ################################################################################################################################

def run_redelivery_scenario(broker:'RabbitMQProcess') -> 'None':
    """ A failed REST push leaves the message unacked, the broker redelivers it until
    the endpoint recovers, and the audit log holds both the failures and the final delivery.
    """
    topic_name = 'topic.amqp.contract.redelivery'
    channel_name = 'pubsub.contract.redelivery.channel'
    exchange = 'pubsub.contract.redelivery.exchange'
    queue = 'pubsub.contract.redelivery.queue'
    routing_key = 'pubsub.contract.redelivery.key'
    rest_sub_key = 'zpsk.rest.contract.redelivery'

    harness = PubSubAMQPHarness(get_broker_address(broker), _server_name)

    listener = RESTPushListener()
    listener.start()

    # The endpoint is down when the message arrives.
    listener.status_code = 500

    try:
        declare_and_bind(broker.amqp_url, exchange, queue, routing_key)

        _ = harness.create_channel(channel_name, queue, 'contract.channel-service')
        _ = harness.register_amqp_topic(topic_name, channel_name=channel_name)
        harness.add_rest_push_subscription(topic_name, rest_sub_key, listener.url)

        # One message goes out while the endpoint is failing ..
        publish_to_exchange(broker.amqp_url, exchange, routing_key, 'contract redelivery payload')

        # .. the broker redelivers it because the failed push left it unacked ..
        def _was_redelivered() -> 'bool':
            return len(listener.received) >= 2

        wait_until(_was_redelivered, 'the broker redelivered the unacked message')

        # .. the endpoint recovers and the very same message finally goes through ..
        listener.status_code = 200

        def _queue_empty() -> 'bool':
            return get_queue_depth(broker.amqp_url, queue) == 0

        wait_until(_queue_empty, 'the redelivered message was acked after the endpoint recovered')

        # .. the audit log recorded the failures and exactly one final delivery.
        def _has_delivered_event() -> 'bool':
            delivered_count, _ignored = _count_outcomes(topic_name)
            return delivered_count == 1

        wait_until(_has_delivered_event, 'the audit log holds the final delivery')

        delivered_count, failed_count = _count_outcomes(topic_name)
        assert delivered_count == 1, f'Expected one delivery, got {delivered_count}'
        assert failed_count >= 1, f'Expected at least one failure, got {failed_count}'

    finally:
        listener.stop()
        harness.stop()

# ################################################################################################################################

def _count_outcomes(topic_name:'str') -> 'tuple[int, int]':
    """ How many Delivered and Delivery_Failed audit events one topic holds.
    """
    delivered_count = 0
    failed_count = 0

    for event in get_audit_events(topic_name):

        if event['event_type'] == AuditEvent.Delivered:
            delivered_count += 1

        elif event['event_type'] == AuditEvent.Delivery_Failed:
            failed_count += 1

    return delivered_count, failed_count

# ################################################################################################################################

def run_override_lifecycle_scenario(broker:'RabbitMQProcess') -> 'None':
    """ Registering a topic against a channel points the channel's consumers at the pub/sub
    delivery service, removing the topic restores the channel's own service, and registering
    the topic again applies the override once more - the create, delete and re-create cycle.
    """
    topic_name = 'topic.amqp.contract.override'
    channel_name = 'pubsub.contract.override.channel'
    exchange = 'pubsub.contract.override.exchange'
    queue = 'pubsub.contract.override.queue'
    routing_key = 'pubsub.contract.override.key'
    service_sub_key = 'zpsk.rest.contract.override'
    channel_service = 'contract.channel-own-service'
    push_service = 'contract.override.push-service'

    harness = PubSubAMQPHarness(get_broker_address(broker), _server_name)

    try:
        declare_and_bind(broker.amqp_url, exchange, queue, routing_key)

        # The channel starts with its own service ..
        channel_config = harness.create_channel(channel_name, queue, channel_service)
        assert channel_config['service_name'] == channel_service

        # .. registering the topic applies the override in place ..
        _ = harness.register_amqp_topic(topic_name, channel_name=channel_name)
        assert channel_config['service_name'] == _pubsub_amqp_bridge_service

        harness.add_service_push_subscription(topic_name, service_sub_key, push_service)

        # .. a message now goes to the topic's push subscriber ..
        publish_to_exchange(broker.amqp_url, exchange, routing_key, 'override payload 1')

        def _first_delivered() -> 'bool':
            return len(harness.server.service_invocations) == 1

        wait_until(_first_delivered, 'the first message reached the push subscriber')
        assert harness.channel_invocations == []

        # .. deleting the topic restores the channel's own service ..
        harness.remove_amqp_topic(topic_name)
        assert channel_config['service_name'] == channel_service

        # .. and the next message goes to that service, not to pub/sub ..
        publish_to_exchange(broker.amqp_url, exchange, routing_key, 'override payload 2')

        def _channel_service_ran() -> 'bool':
            return len(harness.channel_invocations) == 1

        wait_until(_channel_service_ran, 'the channel service received the message after the override was removed')

        invocation = harness.channel_invocations[0]
        assert invocation['service_name'] == channel_service
        assert invocation['body'] == 'override payload 2'
        assert len(harness.server.service_invocations) == 1

        # .. re-creating the topic applies the override again.
        _ = harness.register_amqp_topic(topic_name, channel_name=channel_name)
        assert channel_config['service_name'] == _pubsub_amqp_bridge_service

        publish_to_exchange(broker.amqp_url, exchange, routing_key, 'override payload 3')

        def _second_delivered() -> 'bool':
            return len(harness.server.service_invocations) == 2

        wait_until(_second_delivered, 'the third message reached the push subscriber again')

    finally:
        harness.stop()

# ################################################################################################################################

def run_tls_rejects_plain_scenario(broker:'RabbitMQProcess') -> 'None':
    """ A TLS-only broker accepts no plain AMQP connections.
    """
    from kombu import Connection

    plain_url = broker.amqp_url.replace('amqps://', 'amqp://')

    try:
        with Connection(plain_url) as connection:
            _ = connection.ensure_connection(max_retries=1, timeout=2)

    # This is what must happen - the plain connection cannot be established.
    except Exception:
        connected = False

    else:
        connected = True

    assert not connected, 'A plain AMQP connection to a TLS-only broker unexpectedly succeeded'

# ################################################################################################################################
# ################################################################################################################################
