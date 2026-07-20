# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# gevent
from gevent import sleep

# Zato
from common import delete_all_rows, get_delivery_rows, get_message_rows
from zato.common.api import PubSub
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.server.base.parallel.delivery import SQLPushDelivery

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, callable_

# ################################################################################################################################
# ################################################################################################################################

# The topic, subscribers and target service all the push delivery assertions share
_topic = 'pubsub.backend.test.push'
_sub_key = 'zpsk.test.push.1'
_sub_key_pull = 'zpsk.test.push.2'
_service_name = 'test.push.target'

# How long one wait for an expected delivery outcome may take at most, in seconds -
# generous because a retry sleeps for seconds before its next attempt
_wait_timeout_seconds = 30

# How long one polling sleep is, in seconds
_poll_interval_seconds = 0.05

# How many messages the startup drain and the live phase each cover
_drain_message_count = 5
_live_message_count = 3

# A failure count high enough that delivery cannot succeed before the message expires
_fail_until_expired = 1_000_000

# How quickly the expiring message expires, in seconds
_short_expiration_seconds = 1

# ################################################################################################################################
# ################################################################################################################################

class _StubConfigManager:
    """ Carries the push subscriptions the way the server's config manager does.
    """
    def __init__(self) -> 'None':
        self._push_subs:'anydict' = {}

# ################################################################################################################################

class _StubServer:
    """ Stands in for the server - records every service invocation and fails
    the requested number of them first.
    """
    def __init__(self) -> 'None':
        self.config_manager = _StubConfigManager()
        self.invoked:'anylist' = []
        self.fail_count = 0

    def invoke(self, service_name:'str', payload:'any_') -> 'None':

        if self.fail_count > 0:
            self.fail_count -= 1
            raise Exception('Simulated delivery failure')

        self.invoked.append((service_name, payload))

# ################################################################################################################################

def _wait_until(condition:'callable_', description:'str') -> 'None':
    """ Polls until the condition holds, failing loudly if it does not in time.
    """
    deadline = monotonic() + _wait_timeout_seconds

    while monotonic() < deadline:

        if condition():
            return

        sleep(_poll_interval_seconds)

    raise AssertionError(f'Timed out waiting until {description}')

# ################################################################################################################################

def run_push_delivery_scenario() -> 'None':
    """ Push delivery over the shared backend - the startup drain picks up what
    a previous process left behind, a publish wakes the delivery greenlet up,
    a failed delivery is retried, and a message that expires for the push
    subscriber leaves the queue while other subscribers keep it.
    """
    delete_all_rows()

    backend = SQLPubSubBackend()
    server = _StubServer()
    delivery = SQLPushDelivery(server, backend) # type: ignore[arg-type]

    # The push subscription and its runtime queue state
    sub_config = {
        'topic_name': _topic,
        'push_type': PubSub.Push_Type.Service,
        'push_service_name': _service_name,
    }

    server.config_manager._push_subs[_sub_key] = [sub_config]
    backend.subscribe(_sub_key, _topic)

    # Messages published before the greenlet exists model what a stopped process
    # left unacknowledged - the startup drain must deliver them all ..
    for index in range(_drain_message_count):
        _ = backend.publish(_topic, f'push-drain-{index}')

    delivery.start_sub_key(_sub_key)

    _wait_until(lambda: len(server.invoked) == _drain_message_count, 'the startup drain delivers everything')
    _wait_until(lambda: not get_delivery_rows(_sub_key), 'the startup drain acknowledges everything')

    # .. every delivery invoked the configured service with the published payload ..
    assert server.invoked[0] == (_service_name, 'push-drain-0'), server.invoked[0]

    # .. new publications wake the blocking fetch up and are delivered live ..
    for index in range(_live_message_count):
        _ = backend.publish(_topic, f'push-live-{index}')

    delivered_so_far = _drain_message_count + _live_message_count

    _wait_until(lambda: len(server.invoked) == delivered_so_far, 'the live publications are delivered')
    _wait_until(lambda: not get_delivery_rows(_sub_key), 'the live publications are acknowledged')

    # .. a failed delivery is retried until it succeeds ..
    server.fail_count = 1
    _ = backend.publish(_topic, 'push-retried')

    delivered_so_far += 1

    _wait_until(lambda: len(server.invoked) == delivered_so_far, 'the failed delivery is retried')
    assert server.invoked[-1] == (_service_name, 'push-retried'), server.invoked[-1]

    # .. a message that keeps failing expires for the push subscriber and leaves
    # .. its queue, while the second subscriber - a pull one with no push greenlet -
    # .. keeps both its delivery row and the payload ..
    backend.subscribe(_sub_key_pull, _topic)

    server.fail_count = _fail_until_expired
    _ = backend.publish(_topic, 'push-expired', expiration=_short_expiration_seconds)

    _wait_until(lambda: not get_delivery_rows(_sub_key), 'the expired message leaves the push queue')

    server.fail_count = 0

    # .. the expired message was never delivered ..
    assert len(server.invoked) == delivered_so_far, server.invoked[-1]

    # .. yet the pull subscriber still holds it, payload included.
    pull_rows = get_delivery_rows(_sub_key_pull)
    assert len(pull_rows) == 1, pull_rows

    retained_payload_count = 0

    for row in get_message_rows(_topic):
        if row.payload is not None:
            retained_payload_count += 1

    assert retained_payload_count == 1, retained_payload_count

    # .. stopping the subscriber's greenlet and the whole delivery ends the run cleanly.
    delivery.stop_sub_key(_sub_key)
    delivery.stop()

# ################################################################################################################################
# ################################################################################################################################
