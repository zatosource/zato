# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Items 15.12 and 15.6 - push endpoints that misbehave and push links with stream faults, while a healthy endpoint
# receives its messages without delay. Each message is accepted once, or given up with an audit event once
# its retries run out, and each repeated copy has a higher attempt number.

# stdlib
from time import monotonic

# gevent
from gevent import sleep, spawn

# pytest
import pytest

# Zato
from endpoints import Behavior_Late_OK, Behavior_Mid_Close, Behavior_Normal, Behavior_Redirect, Behavior_Redirect_Found, \
    Behavior_Redirect_Loop, Behavior_Redirect_Permanent, Behavior_Silent, Behavior_Slow_Reader, Behavior_TLS_Stall, Endpoint
from fault_server import Server_Config
from pubsub_rest.latency import get_run_latency
from toxiproxy import Stream_Upstream, Toxiproxy
from zato.server.base.parallel.delivery_rest import Max_Push_Redirects

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Generator
    from pubsub_rest.definition import Definition
    from pubsub_rest.latency import latency_list, SteadyLatency
    from pubsub_rest.server import PubSubServer
    from zato.common.typing_ import any_, anydict, anylist, intlist, strintdict, strlist, strstrdict

    strfloatdict    = dict[str, float]
    strintlistdict  = dict[str, intlist]
    strendpointdict = dict[str, Endpoint]
    rungen          = Generator['_Run', None, None]

# ################################################################################################################################
# ################################################################################################################################

# The endpoints - the name, the behavior, how many messages it receives and the retry settings of its messages.
_healthy = 'healthy'

_endpoints:'anylist' = [
    (_healthy, Behavior_Normal, 600, (3, 1)),
    (Behavior_Slow_Reader, Behavior_Slow_Reader, 3, (3, 1)),
    (Behavior_Late_OK, Behavior_Late_OK, 3, (3, 1)),
    (Behavior_Mid_Close, Behavior_Mid_Close, 5, (3, 1)),
    (Behavior_Silent, Behavior_Silent, 2, (1, 1)),
    (Behavior_TLS_Stall, Behavior_TLS_Stall, 2, (1, 1)),
    (Behavior_Redirect, Behavior_Redirect, 20, (3, 1)),
    (Behavior_Redirect_Permanent, Behavior_Redirect_Permanent, 20, (3, 1)),
    (Behavior_Redirect_Found, Behavior_Redirect_Found, 3, (1, 1)),
    (Behavior_Redirect_Loop, Behavior_Redirect_Loop, 3, (1, 1)),
]

# The endpoints that redirect to an endpoint of their own, which accepts everything.
_redirected_to_target = [Behavior_Redirect, Behavior_Redirect_Permanent, Behavior_Redirect_Found]

# The endpoints whose redirect is followed, so that their targets receive each message once.
_followed = [Behavior_Redirect, Behavior_Redirect_Permanent]

# How many requests each attempt of a message sends to the endpoint that redirects to itself.
_loop_request_count = Max_Push_Redirects + 1

# The endpoints behind a proxy of Toxiproxy - the name, the toxic and its attributes, how many messages it receives
# and the retry settings of its messages. Each toxic applies to what the delivery sends.
_toxic_endpoints:'anylist' = [
    ('link-latency', 'latency', {'latency': 2000, 'jitter': 0}, 10, (3, 1)),
    ('link-bandwidth', 'bandwidth', {'rate': 1}, 10, (3, 1)),
    ('link-slicer', 'slicer', {'average_size': 10, 'size_variation': 5, 'delay': 100}, 20, (3, 1)),
    ('link-black-hole', 'timeout', {'timeout': 0}, 2, (1, 1)),
    ('link-reset', 'reset_peer', {'timeout': 0}, 3, (1, 1)),
    ('link-cut', 'limit_data', {'bytes': 100}, 3, (1, 1)),
]

# The endpoints whose messages are accepted at the second attempt, after the first one fails.
_accepted_on_retry = [Behavior_Slow_Reader, Behavior_Late_OK, Behavior_Mid_Close]

# The endpoints whose messages are accepted at the first attempt.
_accepted_at_once = [_healthy, 'link-latency', 'link-bandwidth', 'link-slicer']

# The endpoints whose messages are given up once their retries run out. A delivery refuses a 302,
# and a redirect to the endpoint itself exceeds the limit of redirects, so each attempt to them fails.
_given_up = [
    Behavior_Silent,
    Behavior_TLS_Stall,
    Behavior_Redirect_Found,
    Behavior_Redirect_Loop,
    'link-black-hole',
    'link-reset',
    'link-cut',
]

# The record of the server that gives up a message of a subscriber whose retries ran out
_given_up_record = 'PubSub delivery given up for sub_key `{}`'

# The path that every endpoint is pushed to on its host
_url_path = '/'

_healthy_interval_seconds = 0.05
_healthy_p99_limit_seconds = 1.0

_run_timeout_seconds = 600
_poll_seconds = 1.0

# ################################################################################################################################
# ################################################################################################################################

def _get_subscriber_name(name:'str') -> 'str':
    out = f'faults.endpoints.{name}'
    return out

# ################################################################################################################################

def _get_topic_name(name:'str') -> 'str':
    out = f'faults.endpoints.{name}'
    return out

# ################################################################################################################################

def _get_target_name(name:'str') -> 'str':
    out = f'{name}-target'
    return out

# ################################################################################################################################
# ################################################################################################################################

class _Run:
    """ The endpoints, their subscriptions and the account of their messages.
    """

    def __init__(self, toxiproxy:'Toxiproxy') -> 'None':
        self.toxiproxy = toxiproxy
        self.server:'PubSubServer | None' = None

        self.endpoints:'strendpointdict' = {}
        self.hosts:'strstrdict' = {}
        self.message_counts:'strintdict' = {}
        self.retry_settings:'anydict' = {}
        self.publish_times:'strfloatdict' = {}
        self.sub_keys:'strstrdict' = {}

# ################################################################################################################################

    def _add(self, name:'str', endpoint:'Endpoint', message_count:'int', retry_settings:'any_') -> 'None':
        self.endpoints[name] = endpoint
        self.message_counts[name] = message_count
        self.retry_settings[name] = retry_settings

# ################################################################################################################################

    def start_endpoints(self) -> 'None':

        # Each endpoint is reached directly, and the target of each redirect accepts everything ..
        for name, behavior, message_count, retry_settings in _endpoints:

            if name in _redirected_to_target:
                target_name = _get_target_name(name)
                target = Endpoint(target_name, Behavior_Normal)
                self.endpoints[target_name] = target
                redirect_port = target.port
            else:
                redirect_port = None

            endpoint = Endpoint(name, behavior, redirect_port)
            self._add(name, endpoint, message_count, retry_settings)

            scheme = 'https' if behavior == Behavior_TLS_Stall else 'http'
            self.hosts[name] = f'{scheme}://127.0.0.1:{endpoint.port}'

        # .. apart from those behind a proxy, which receive what passes through their toxic.
        for name, toxic_type, attributes, message_count, retry_settings in _toxic_endpoints:
            endpoint = Endpoint(name, Behavior_Normal)
            self._add(name, endpoint, message_count, retry_settings)

            listen_port = self.toxiproxy.add_proxy(name, endpoint.port)
            self.toxiproxy.add_toxic(name, toxic_type, attributes, Stream_Upstream)
            self.hosts[name] = f'http://127.0.0.1:{listen_port}'

# ################################################################################################################################

    def stop_endpoints(self) -> 'None':
        for endpoint in self.endpoints.values():
            endpoint.stop()

# ################################################################################################################################

    def define(self, server:'PubSubServer', definition:'Definition') -> 'None':
        """ Each endpoint is subscribed to a topic of its own and pushed to through its URL.
        """
        for name in self.message_counts:
            subscriber_name = _get_subscriber_name(name)
            topic_name = _get_topic_name(name)
            _ = definition.add_push_subscriber_at(subscriber_name, [topic_name], self.hosts[name], _url_path)

        self.server = server
        server.ready_callbacks.append(self._attach)

# ################################################################################################################################

    def _attach(self) -> 'None':
        server = self.get_server()
        sub_keys = server.get_sub_keys()

        for name in self.message_counts:
            self.sub_keys[name] = sub_keys[_get_subscriber_name(name)]

        # The server gives up each message of the endpoints that accept none of them.
        state = server.get_state()

        for name in _given_up:
            state.expected_server_records.append(_given_up_record.format(self.sub_keys[name]))

# ################################################################################################################################

    def get_server(self) -> 'PubSubServer':
        server = self.server
        assert server is not None, 'The server of the endpoints has not been started'
        return server

# ################################################################################################################################

    def publish(self, name:'str') -> 'None':
        max_retries, retry_sleep_time = self.retry_settings[name]
        topic_name = _get_topic_name(name)
        message_count = self.message_counts[name]

        server = self.get_server()

        for index in range(message_count):
            data = {'endpoint': name, 'index': index}
            msg_id = server.publish_with_retries(topic_name, data, max_retries, retry_sleep_time)
            self.publish_times[msg_id] = monotonic()

            if name == _healthy:
                sleep(_healthy_interval_seconds)

# ################################################################################################################################

    def get_queue_depths(self) -> 'anydict':
        out = self.get_server().get_queue_depths(list(self.sub_keys.values()))
        return out

# ################################################################################################################################

    def is_done(self) -> 'bool':

        for depth in self.get_queue_depths().values():
            if depth:
                return False

        return True

# ################################################################################################################################

    def get_failed_msg_ids(self, name:'str') -> 'strlist':
        out = self.get_server().get_failed_msg_ids(self.sub_keys[name])
        return out

# ################################################################################################################################
# ################################################################################################################################

def _get_attempts(endpoint:'Endpoint') -> 'strintlistdict':
    out:'strintlistdict' = {}

    for request in endpoint.requests:
        if request.msg_id not in out:
            out[request.msg_id] = []
        out[request.msg_id].append(request.attempt)

    return out

# ################################################################################################################################

def _get_healthy_latency(run:'_Run') -> 'SteadyLatency':
    """ How long the healthy endpoint waited for its messages at the 99th percentile, outside the seconds
    in which the host stalled the deliveries.
    """
    samples:'latency_list' = []

    for request in run.endpoints[_healthy].requests:
        published_at = run.publish_times[request.msg_id]
        samples.append((published_at, request.received_at - published_at))

    out = get_run_latency(samples, _healthy_p99_limit_seconds)
    return out

# ################################################################################################################################

def _check(run:'_Run') -> 'None':
    """ What each endpoint received and what was given up.
    """
    endpoints = run.endpoints
    message_counts = run.message_counts

    # The healthy endpoint received its messages without delay ..
    healthy = _get_healthy_latency(run)
    assert healthy.percentile < _healthy_p99_limit_seconds, healthy

    # .. each endpoint that accepts at once received each message once ..
    for name in _accepted_at_once:
        attempts = _get_attempts(endpoints[name])
        assert len(attempts) == message_counts[name], (name, attempts)

        for msg_id, msg_attempts in attempts.items():
            assert msg_attempts == [1], (name, msg_id, msg_attempts)

    # .. each endpoint that misbehaves at the first attempt received the repeated copy as the second attempt
    # .. and accepted it, the late one having processed the first copy as well ..
    for name in _accepted_on_retry:
        attempts = _get_attempts(endpoints[name])
        assert len(attempts) == message_counts[name], (name, attempts)

        for msg_id, msg_attempts in attempts.items():
            msg_attempts.sort()
            assert msg_attempts == [1, 2], (name, msg_id, msg_attempts)

        accepted:'strlist' = []

        for request in endpoints[name].requests:
            if request.is_accepted:
                accepted.append(request.msg_id)

        copies_accepted = 2 if name == Behavior_Late_OK else 1
        assert len(accepted) == message_counts[name] * copies_accepted, (name, accepted)

    # .. a 307 and a 308 were followed, so their targets received each message once, at its first attempt ..
    for name in _followed:
        target_name = _get_target_name(name)
        target_attempts = _get_attempts(endpoints[target_name])
        assert len(target_attempts) == message_counts[name], (target_name, target_attempts)

        for msg_id, msg_attempts in target_attempts.items():
            assert msg_attempts == [1], (target_name, msg_id, msg_attempts)

    # .. a 302 was refused, so its target received no request ..
    found_target_name = _get_target_name(Behavior_Redirect_Found)
    found_target_requests = endpoints[found_target_name].requests
    assert not found_target_requests, found_target_requests

    # .. a redirect to the endpoint itself was followed until the limit of redirects at each attempt ..
    loop_attempts = _get_attempts(endpoints[Behavior_Redirect_Loop])
    assert len(loop_attempts) == message_counts[Behavior_Redirect_Loop], loop_attempts

    for msg_id, msg_attempts in loop_attempts.items():
        for attempt in set(msg_attempts):
            request_count = msg_attempts.count(attempt)
            assert request_count == _loop_request_count, (msg_id, attempt, request_count)

    # .. and each message that was never accepted was given up with an audit event.
    for name in _given_up:
        failed_msg_ids = run.get_failed_msg_ids(name)
        assert len(failed_msg_ids) == message_counts[name], (name, failed_msg_ids)

        for request in endpoints[name].requests:
            assert not request.is_accepted, (name, request)

# ################################################################################################################################

@pytest.fixture
def endpoint_run(endpoint_work_dir:'str') -> 'rungen':
    """ The endpoints of the test, started before the server, which pushes to them.
    """
    toxiproxy = Toxiproxy('endpoints')
    toxiproxy.start()

    run = _Run(toxiproxy)

    try:
        run.start_endpoints()
        Server_Config.definers.append(run.define)

        # The database of this test is not faulted, so no record of a database fault is expected.
        Server_Config.expected_server_records = []

        yield run

    finally:
        Server_Config.reset()
        run.stop_endpoints()
        toxiproxy.stop()

# ################################################################################################################################

def test_endpoints(endpoint_work_dir:'str', endpoint_run:'_Run', server:'PubSubServer') -> 'None':
    """ Push endpoints that read slowly, never respond, respond late, close in the middle of a response, stall
    the TLS handshake or redirect with 307, 308, 302 or to themselves, and push links that are slow, limited, sliced,
    held, reset or cut.
    """
    run = endpoint_run

    # The messages of all the endpoints are published at the same time ..
    publishers:'anylist' = []

    for name in run.message_counts:
        publisher = spawn(run.publish, name)
        publishers.append(publisher)

    for publisher in publishers:
        _ = publisher.get()

    # .. and the run waits until every queue is empty.
    start = monotonic()

    while not run.is_done():
        assert monotonic() - start < _run_timeout_seconds, ('Endpoints not done', run.get_queue_depths())
        sleep(_poll_seconds)

    _check(run)

# ################################################################################################################################
# ################################################################################################################################
