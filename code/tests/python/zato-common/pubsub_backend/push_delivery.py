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
from zato.server.base.parallel.delivery import PushDelivery

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, callable_

# ################################################################################################################################
# ################################################################################################################################

# The topic, subscribers and target service all the push delivery assertions share.
_topic = 'pubsub.backend.test.push'
_sub_key = 'zpsk.test.push.1'
_sub_key_pull = 'zpsk.test.push.2'
_service_name = 'test.push.target'

# How long one wait for an expected delivery outcome may take at most, in seconds -
# generous because a retry sleeps for seconds before its next attempt.
_wait_timeout_seconds = 30

# How long one polling sleep is, in seconds.
_poll_interval_seconds = 0.05

# How many messages the startup drain and the live phase each cover.
_drain_message_count = 5
_live_message_count = 3

# A failure count high enough that delivery cannot succeed before the message expires.
_fail_until_expired = 1_000_000

# How quickly the expiring message expires, in seconds.
_short_expiration_seconds = 1

# The sleep a publisher asks for between its two attempts, in seconds.
_publisher_sleep_time = 1

# The sleep a message without settings gets before its first retry, in seconds, and how much
# more than that the retry may take - the policy's jitter plus the greenlet's own overhead.
_default_sleep_time = PubSub.Delivery.Default_Sleep_Time
_jitter_fraction = PubSub.Delivery.Jitter_Percent / 100
_slack_seconds = 0.5

# ################################################################################################################################
# ################################################################################################################################

class _StubConfigManager:
    """ Carries the push subscriptions the way the server's config manager does.
    """
    def __init__(self) -> 'None':
        self._push_subs:'anydict' = {}

# ################################################################################################################################

class _StubServer:
    """ Stands in for the server - records every service invocation, when it was made and whether it was refused,
    and fails the requested number of them first.
    """
    def __init__(self) -> 'None':
        self.config_manager = _StubConfigManager()
        self.invoked:'anylist' = []
        self.attempt_times:'anylist' = []
        self.fail_count = 0

    def invoke(self, service_name:'str', payload:'any_') -> 'None':

        self.attempt_times.append(monotonic())

        if self.fail_count > 0:
            self.fail_count -= 1
            raise Exception('Simulated delivery failure')

        self.invoked.append((service_name, payload))

# ################################################################################################################################

def _get_last_gap(server:'_StubServer') -> 'float':
    """ How long the last attempt came after the one before it.
    """
    last_time = server.attempt_times[-1]
    previous_time = server.attempt_times[-2]

    out = last_time - previous_time
    return out

# ################################################################################################################################

def _assert_gap_within(gap:'float', expected:'float') -> 'None':
    """ A gap between two attempts is what the policy's sleep says, give or take the jitter and the slack.
    """
    lower = expected - _slack_seconds
    upper = expected + expected * _jitter_fraction + _slack_seconds

    assert lower <= gap <= upper, (gap, expected)

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
    a failed delivery is retried as the message's own settings or the default policy say,
    a message whose round ran out leaves the queue, and a message that expires for the push
    subscriber leaves the queue while other subscribers keep it.
    """
    delete_all_rows()

    backend = SQLPubSubBackend()
    server = _StubServer()
    delivery = PushDelivery(server, backend) # type: ignore[arg-type]

    # The delivery is stopped however the scenario ends - a failure before its own stop would otherwise leave
    # a greenlet behind that keeps fetching from a database the process has since moved away from.
    try:
        _run_push_delivery_flow(backend, server, delivery)
    finally:
        delivery.stop()

# ################################################################################################################################

def _run_push_delivery_flow(backend:'SQLPubSubBackend', server:'_StubServer', delivery:'PushDelivery') -> 'None':
    """ The scenario itself, with the delivery whose greenlets it runs on.
    """

    # The push subscription and its runtime queue state.
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

    # .. a failed delivery is retried after the sleep its publisher asked for ..
    server.fail_count = 1
    _ = backend.publish(_topic, 'push-retried', max_retries=1, retry_sleep_time=_publisher_sleep_time)

    delivered_so_far += 1

    _wait_until(lambda: len(server.invoked) == delivered_so_far, 'the failed delivery is retried')
    assert server.invoked[-1] == (_service_name, 'push-retried'), server.invoked[-1]

    gap = _get_last_gap(server)
    _assert_gap_within(gap, _publisher_sleep_time)

    # .. a failed delivery of a message without settings is retried after the default policy's first sleep ..
    server.fail_count = 1
    _ = backend.publish(_topic, 'push-retried-default')

    delivered_so_far += 1

    _wait_until(lambda: len(server.invoked) == delivered_so_far, 'the failed delivery is retried under the default policy')
    assert server.invoked[-1] == (_service_name, 'push-retried-default'), server.invoked[-1]

    gap = _get_last_gap(server)
    _assert_gap_within(gap, _default_sleep_time)

    # .. a message that allows no retries and fails once is given up on - it leaves the queue,
    # .. it was attempted exactly once and the message behind it is delivered ..
    server.fail_count = 1
    attempts_so_far = len(server.attempt_times)

    _ = backend.publish(_topic, 'push-given-up', max_retries=0)

    _wait_until(lambda: not get_delivery_rows(_sub_key), 'the given-up message leaves the push queue')

    assert len(server.invoked) == delivered_so_far, server.invoked[-1]
    assert len(server.attempt_times) == attempts_so_far + 1, len(server.attempt_times)

    _ = backend.publish(_topic, 'push-after-given-up')

    delivered_so_far += 1

    _wait_until(lambda: len(server.invoked) == delivered_so_far, 'the message after the given-up one is delivered')
    assert server.invoked[-1] == (_service_name, 'push-after-given-up'), server.invoked[-1]

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

    # .. stopping the subscriber's greenlet ends the run cleanly.
    delivery.stop_sub_key(_sub_key)

# ################################################################################################################################
# ################################################################################################################################
