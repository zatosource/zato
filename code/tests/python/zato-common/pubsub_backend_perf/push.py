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
from common import get_min_delivery_rate, get_min_publish_rate, set_progress_context
from seeding import count_rows, seed_backlog
from zato.common.api import PubSub
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.server.base.parallel.delivery import PushDelivery

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# How many topics run, each with its own push subscriber and its own delivery greenlet.
_topic_count = 200

# How many pending messages per subscriber wait in the queues before the delivery greenlets start.
_backlog_per_subscriber = 40

# How many messages the publishers add live while the backlog drains.
_message_count = 4_000

# How many messages the run delivers in total.
_total_delivery_count = _topic_count * _backlog_per_subscriber + _message_count

# How many publisher greenlets pump concurrently with the delivery greenlets.
_publisher_greenlet_count = 30

# The name of the service every push subscription targets.
_service_name = 'perf.push.target'

# How long the whole run may take at most before it is declared hung, in seconds.
_deadline_seconds = 120

# How long one polling sleep is while waiting for the deliveries, in seconds.
_poll_interval_seconds = 0.2

# ################################################################################################################################
# ################################################################################################################################

class _StubConfigManager:
    """ Carries the push subscriptions the way the server's config manager does.
    """
    def __init__(self) -> 'None':
        self._push_subs:'anydict' = {}

# ################################################################################################################################

class _StubServer:
    """ Stands in for the server - counts every service invocation, yielding
    the way a real invocation yields on its network I/O.
    """
    def __init__(self) -> 'None':
        self.config_manager = _StubConfigManager()
        self.invoked_count = 0

    def invoke(self, service_name:'str', payload:'any_') -> 'None':
        self.invoked_count += 1

        # A real invocation switches greenlets on its network I/O - without this yield
        # the delivery greenlets would starve the publishers on the shared loop.
        sleep(0)

# ################################################################################################################################

def _publish_share(backend:'SQLPubSubBackend', topic_names:'strlist', publisher_index:'int') -> 'None':
    """ What one publisher greenlet runs - its share of the measured messages,
    round-robin over all the topics. The remainder of the division goes to the
    first publishers, one message each, so all the shares add up to the total.
    """
    share, remainder = divmod(_message_count, _publisher_greenlet_count)

    if publisher_index < remainder:
        share += 1

    for message_index in range(share):
        topic_name = topic_names[(publisher_index * share + message_index) % _topic_count]
        _ = backend.publish(topic_name, f'push-perf-{publisher_index}-{message_index}')

# ################################################################################################################################

def run_push_delivery_scenario() -> 'None':
    """ Push delivery at population scale - one delivery greenlet per subscriber,
    all sharing one backend. Each greenlet first drains the backlog its queue held
    when it started - the startup path a restart or a takeover runs - and then
    delivers the live traffic the publishers pump concurrently, message by message
    as the wake-up events arrive. The delivery rate must clear the floor across
    both paths and every batch must be acknowledged, leaving no delivery rows behind.
    """
    set_progress_context('push delivery', _publisher_greenlet_count, _topic_count)

    # The backlog is pending in the queues before any delivery greenlet exists ..
    seed_seconds = seed_backlog(
        topic_count=_topic_count,
        messages_per_topic=_backlog_per_subscriber,
        topic_prefix='perf.push',
        sub_key_prefix='zpsk.perf.push',
    )
    print(f'Seeded {intcomma(_topic_count * _backlog_per_subscriber)} backlog messages in {seed_seconds:.2f}s')

    backend = SQLPubSubBackend()
    server = _StubServer()
    delivery = PushDelivery(server, backend) # type: ignore[arg-type]

    # .. every topic has its own push subscriber, subscribed already by the seeding ..
    topic_names:'strlist' = []
    sub_keys:'strlist' = []

    for topic_index in range(_topic_count):
        topic_name = f'perf.push.{topic_index:04d}'
        sub_key = f'zpsk.perf.push.{topic_index:04d}'

        topic_names.append(topic_name)
        sub_keys.append(sub_key)

        server.config_manager._push_subs[sub_key] = [{
            'topic_name': topic_name,
            'push_type': PubSub.Push_Type.Service,
            'push_service_name': _service_name,
        }]

    # .. the clock starts now ..
    start = monotonic()

    # .. the delivery greenlets drain their backlogs first and then wait
    # .. on their wake-up events ..
    for sub_key in sub_keys:
        delivery.start_sub_key(sub_key)

    # .. now the publishers pump concurrently with the deliveries ..
    publishers:'anylist' = []

    for publisher_index in range(_publisher_greenlet_count):
        publishers.append(spawn(_publish_share, backend, topic_names, publisher_index))

    _ = joinall(publishers, timeout=_deadline_seconds)

    publish_elapsed = monotonic() - start

    # .. wait until every message was pushed to the service and its batch acknowledged ..
    deadline = monotonic() + _deadline_seconds

    while monotonic() < deadline:

        if server.invoked_count == _total_delivery_count:
            if count_rows('pubsub_delivery') == 0:
                break

        sleep(_poll_interval_seconds)

    elapsed = monotonic() - start

    delivery.stop()

    # .. everything went through ..
    invoked = server.invoked_count
    assert invoked == _total_delivery_count, f'Expected {intcomma(_total_delivery_count)} deliveries, got {intcomma(invoked)}'

    # .. every batch was acknowledged - the queues are empty ..
    remaining = count_rows('pubsub_delivery')
    assert remaining == 0, f'Expected no delivery rows, got {intcomma(remaining)}'

    # .. and both rates must clear their floors.
    publish_rate = _message_count / publish_elapsed
    delivery_rate = invoked / elapsed

    message = f'Push delivery: {intcomma(invoked)} messages to {_topic_count} subscribers'
    message += f' at {intcomma(int(delivery_rate))}/s with {intcomma(int(publish_rate))} publishes/s'
    print(message)

    assert publish_rate >= get_min_publish_rate(), \
        f'Publish rate too low during push delivery: {intcomma(int(publish_rate))}/s'

    assert delivery_rate >= get_min_delivery_rate(), \
        f'Push delivery rate too low: {intcomma(int(delivery_rate))}/s over {intcomma(invoked)} messages'

# ################################################################################################################################
# ################################################################################################################################
