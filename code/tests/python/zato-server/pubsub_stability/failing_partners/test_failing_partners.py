# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from time import monotonic

# gevent
from gevent import sleep, spawn

# Zato
from pubsub_rest.latency import get_run_latency
from zato.common.test.perf_report import report_result, start_measurement

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pubsub_rest.latency import latency_list, SteadyLatency
    from pubsub_rest.receiver import Push
    from pubsub_rest.server import PubSubServer
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The partners, as the setup of the suite names their endpoints.
_healthy = 'healthy'
_slow = 'slow'
_flaky = 'flaky'
_failing = 'failing'
_unresponsive = 'unresponsive'

# How long the slow partner takes to respond, in seconds.
_slow_response_seconds = 2

# Every that many requests the flaky partner responds with HTTP 500, which is 20 percent of them.
_flaky_failure_every = 5

# How long the unresponsive partner holds a request without responding, in seconds,
# which is longer than the server waits for a response.
_unresponsive_hold_seconds = 3600

# How many messages each partner receives, and how often the healthy partner receives one, in seconds.
_message_counts = {
    _healthy: 600,
    _slow: 10,
    _flaky: 25,
    _failing: 3,
    _unresponsive: 2,
}

_healthy_interval_seconds = 0.05

# The retry settings that the messages of each partner travel with - how many retries and how long the first pause is.
_retry_settings = {
    _healthy: (3, 1),
    _slow: (3, 1),
    _flaky: (5, 1),
    _failing: (2, 1),
    _unresponsive: (1, 1),
}

# How long the healthy partner may wait for its messages at the 99th percentile, in seconds.
_healthy_p99_limit_seconds = 1.0

# How long the whole run may take before it fails, in seconds.
_run_timeout_seconds = 300

# How often the run checks whether every partner is done, in seconds.
_poll_seconds = 1.0

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class _Request:
    """ One request that a partner received.
    """
    msg_id: 'str'
    attempt: 'int'
    received_at: 'float'
    is_accepted: 'bool'

request_list = list[_Request]

# ################################################################################################################################
# ################################################################################################################################

class _Partners:
    """ The behavior of each partner, recording each request that reaches its endpoint.
    """

    def __init__(self, partner_names:'strlist') -> 'None':
        self.requests:'dict[str, request_list]' = {}
        self.flaky_request_count = 0

        for name in partner_names:
            self.requests[name] = []

    def _respond(self, name:'str') -> 'bool':
        """ Behaves as the given partner does and returns whether it accepted the request.
        """
        if name == _slow:
            sleep(_slow_response_seconds)
            out = True

        elif name == _flaky:
            self.flaky_request_count += 1
            out = self.flaky_request_count % _flaky_failure_every != 0

        elif name == _failing:
            out = False

        elif name == _unresponsive:
            sleep(_unresponsive_hold_seconds)
            out = False

        else:
            out = True

        return out

    def on_push(self, push:'Push') -> 'bool':

        name = push.path.strip('/')

        # The request is recorded on arrival, including one that is never responded to ..
        request = _Request()
        request.msg_id = push.msg_id
        request.attempt = push.attempt
        request.received_at = monotonic()
        request.is_accepted = False

        self.requests[name].append(request)

        # .. and the partner behaves as it does.
        request.is_accepted = self._respond(name)

        out = request.is_accepted
        return out

    def get_accepted_msg_ids(self, name:'str') -> 'set[str]':
        out:'set[str]' = set()

        for request in self.requests[name]:
            if request.is_accepted:
                out.add(request.msg_id)

        return out

# ################################################################################################################################
# ################################################################################################################################

def _publish(server:'PubSubServer', topic_name:'str', name:'str', publish_times:'anydict') -> 'None':
    """ Publishes the messages of one partner, recording when each one was published.
    """
    max_retries, retry_sleep_time = _retry_settings[name]

    for index in range(_message_counts[name]):

        msg_id = server.publish_with_retries(topic_name, {'partner': name, 'index': index}, max_retries, retry_sleep_time)
        publish_times[msg_id] = monotonic()

        if name == _healthy:
            sleep(_healthy_interval_seconds)

# ################################################################################################################################

def _is_done(server:'PubSubServer', partners:'_Partners', sub_keys:'anydict') -> 'bool':
    """ Whether each partner received its messages and every queue is empty.
    """
    depths = server.get_queue_depths(list(sub_keys.values()))

    for depth in depths.values():
        if depth:
            return False

    for name in (_healthy, _slow, _flaky):
        if len(partners.get_accepted_msg_ids(name)) < _message_counts[name]:
            return False

    return True

# ################################################################################################################################

def _get_healthy_latency(partners:'_Partners', publish_times:'anydict') -> 'SteadyLatency':
    """ How long the healthy partner waited for its messages at the 99th percentile, in seconds, outside the seconds
    in which the host stalled the deliveries.
    """
    samples:'latency_list' = []

    for request in partners.requests[_healthy]:
        published_at = publish_times[request.msg_id]
        samples.append((published_at, request.received_at - published_at))

    out = get_run_latency(samples, _healthy_p99_limit_seconds)
    return out

# ################################################################################################################################

def _check_attempts(partners:'_Partners', name:'str', expected_attempts:'int') -> 'None':
    """ Each message of a partner that never accepts one was attempted as often as its retry settings allow,
    with attempt numbers that rise by one.
    """
    attempts_by_msg_id:'dict[str, list[int]]' = {}

    for request in partners.requests[name]:
        if request.msg_id not in attempts_by_msg_id:
            attempts_by_msg_id[request.msg_id] = []
        attempts_by_msg_id[request.msg_id].append(request.attempt)

    assert len(attempts_by_msg_id) == _message_counts[name], (name, attempts_by_msg_id)

    expected = list(range(1, expected_attempts + 1))

    for msg_id, attempts in attempts_by_msg_id.items():
        assert sorted(attempts) == expected, (name, msg_id, attempts)

# ################################################################################################################################
# ################################################################################################################################

def test_failing_partners(server:'PubSubServer') -> 'None':
    """ Push partners that respond slowly, fail some requests, fail all of them or never respond receive what
    their retry settings allow, the messages they never accept are given up with an audit event each,
    and the healthy partner receives its messages without delay throughout.
    """
    partner_names:'strlist' = server.properties['partner_names']
    partner_prefix = server.properties['partner_prefix']

    partners = _Partners(partner_names)
    server.properties['endpoints'].handler = partners.on_push

    all_sub_keys = server.get_sub_keys()
    sub_keys:'anydict' = {}

    for name in partner_names:
        sub_keys[name] = all_sub_keys[f'{partner_prefix}.{name}']

    measurement = start_measurement(server.get_client(), server.get_database())

    # The messages of all the partners are published at the same time ..
    publish_times:'anydict' = {}
    publishers:'anylist' = []

    for name in partner_names:
        publisher = spawn(_publish, server, f'{partner_prefix}.{name}', name, publish_times)
        publishers.append(publisher)

    for publisher in publishers:
        _ = publisher.get()

    # .. and the run waits until every partner received its messages and every queue is empty.
    start = monotonic()

    while not _is_done(server, partners, sub_keys):
        assert monotonic() - start < _run_timeout_seconds, ('Partners not done', server.get_queue_depths(list(sub_keys.values())))
        sleep(_poll_seconds)

    healthy = _get_healthy_latency(partners, publish_times)

    _ = report_result(measurement, 'pubsub-failing-partners', {'healthy_p99_seconds': healthy.percentile})

    # The healthy partner received each of its messages once and without delay ..
    healthy_requests = partners.requests[_healthy]
    assert len(healthy_requests) == _message_counts[_healthy], len(healthy_requests)
    assert healthy.percentile < _healthy_p99_limit_seconds, healthy

    # .. the slow partner received each of its messages once ..
    assert len(partners.requests[_slow]) == _message_counts[_slow], len(partners.requests[_slow])

    # .. the flaky partner accepted each of its messages once, after a retry where it failed one ..
    flaky_accepted = partners.get_accepted_msg_ids(_flaky)
    assert len(flaky_accepted) == _message_counts[_flaky], len(flaky_accepted)

    flaky_rejected = len(partners.requests[_flaky]) - _message_counts[_flaky]
    assert flaky_rejected == len(partners.requests[_flaky]) // _flaky_failure_every, flaky_rejected

    # .. the failing and the unresponsive partners received every attempt that the retry settings allow ..
    _check_attempts(partners, _failing, _retry_settings[_failing][0] + 1)
    _check_attempts(partners, _unresponsive, _retry_settings[_unresponsive][0] + 1)

    # .. and each message they never accepted was given up with an audit event.
    for name in (_failing, _unresponsive):
        failed_msg_ids = server.get_failed_msg_ids(sub_keys[name])
        assert len(failed_msg_ids) == _message_counts[name], (name, failed_msg_ids)

# ################################################################################################################################
# ################################################################################################################################
