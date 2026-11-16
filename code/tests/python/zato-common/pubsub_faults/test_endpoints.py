# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Items 15.12 and 15.6 - push endpoints that misbehave and push links with stream faults, while a healthy endpoint
# receives its messages without delay. Each message is accepted once, or given up with an audit event once
# its retries run out, and each repeated copy has a higher attempt number.

# stdlib
import os
from time import monotonic

# gevent
from gevent import sleep, spawn

# SQLAlchemy
from sqlalchemy import text

# Zato
from endpoints import Behavior_Late_OK, Behavior_Mid_Close, Behavior_Normal, Behavior_Redirect, Behavior_Silent, \
    Behavior_Slow_Reader, Behavior_TLS_Stall, Endpoint
from toxiproxy import Stream_Upstream, Toxiproxy
from zato.common.api import PubSub
from zato.common.audit_log.api import AuditLog, get_audit_engine
from zato.common.audit_log.common import AuditEvent
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.test.pubsub_database import pubsub_db_env
from zato.server.base.parallel.delivery import PushDelivery

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, intlist, strintdict, strlist, strstrdict

    floatlist       = list[float]
    strfloatdict    = dict[str, float]
    strintlistdict  = dict[str, intlist]
    strendpointdict = dict[str, Endpoint]

# ################################################################################################################################
# ################################################################################################################################

_server_name = 'faults.endpoints'

# The endpoints - the name, the behavior, how many messages it receives and the retry settings of its messages.
_healthy = 'healthy'
_redirect_target = 'redirect-target'

_endpoints:'anylist' = [
    (_healthy, Behavior_Normal, 600, (3, 1)),
    (Behavior_Slow_Reader, Behavior_Slow_Reader, 3, (3, 1)),
    (Behavior_Late_OK, Behavior_Late_OK, 3, (3, 1)),
    (Behavior_Mid_Close, Behavior_Mid_Close, 5, (3, 1)),
    (Behavior_Silent, Behavior_Silent, 2, (1, 1)),
    (Behavior_TLS_Stall, Behavior_TLS_Stall, 2, (1, 1)),
    (Behavior_Redirect, Behavior_Redirect, 20, (3, 1)),
]

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

# The endpoints whose messages are given up once their retries run out.
_given_up = [Behavior_Silent, Behavior_TLS_Stall, 'link-black-hole', 'link-reset', 'link-cut']

_healthy_interval_seconds = 0.05
_healthy_p99_limit_seconds = 1.0

_run_timeout_seconds = 600
_poll_seconds = 1.0

_queue_depth_query = text('select count(*) from pubsub_delivery where sub_key = :sub_key')
_failed_events_query = text('select msg_id from event where event_type = :event_type and sub_key = :sub_key')

# ################################################################################################################################
# ################################################################################################################################

class _StubConfigManager:
    """ Holds the push subscriptions the way the configuration manager of a server does.
    """
    def __init__(self) -> 'None':
        self._push_subs:'anydict' = {}

# ################################################################################################################################
# ################################################################################################################################

class _StubServer:
    """ Stands in for the server whose push delivery the suite runs.
    """
    def __init__(self) -> 'None':
        self.config_manager = _StubConfigManager()

# ################################################################################################################################
# ################################################################################################################################

def _get_sub_key(name:'str') -> 'str':
    out = f'zpsk.faults.endpoints.{name}'
    return out

# ################################################################################################################################

def _get_topic_name(name:'str') -> 'str':
    out = f'faults.endpoints.{name}'
    return out

# ################################################################################################################################
# ################################################################################################################################

class _Run:
    """ The endpoints, their subscriptions and the account of their messages.
    """

    def __init__(self, backend:'SQLPubSubBackend', toxiproxy:'Toxiproxy') -> 'None':
        self.backend = backend
        self.toxiproxy = toxiproxy

        self.endpoints:'strendpointdict' = {}
        self.urls:'strstrdict' = {}
        self.message_counts:'strintdict' = {}
        self.retry_settings:'anydict' = {}
        self.publish_times:'strfloatdict' = {}

# ################################################################################################################################

    def _add(self, name:'str', endpoint:'Endpoint', message_count:'int', retry_settings:'any_') -> 'None':
        self.endpoints[name] = endpoint
        self.message_counts[name] = message_count
        self.retry_settings[name] = retry_settings

# ################################################################################################################################

    def start_endpoints(self) -> 'None':

        # The target of the redirect accepts everything ..
        target = Endpoint(_redirect_target, Behavior_Normal)
        self.endpoints[_redirect_target] = target

        # .. each other endpoint is reached directly ..
        for name, behavior, message_count, retry_settings in _endpoints:
            endpoint = Endpoint(name, behavior, target.port)
            self._add(name, endpoint, message_count, retry_settings)

            scheme = 'https' if behavior == Behavior_TLS_Stall else 'http'
            self.urls[name] = f'{scheme}://127.0.0.1:{endpoint.port}/'

        # .. apart from those behind a proxy, which receive what passes through their toxic.
        for name, toxic_type, attributes, message_count, retry_settings in _toxic_endpoints:
            endpoint = Endpoint(name, Behavior_Normal)
            self._add(name, endpoint, message_count, retry_settings)

            listen_port = self.toxiproxy.add_proxy(name, endpoint.port)
            self.toxiproxy.add_toxic(name, toxic_type, attributes, Stream_Upstream)
            self.urls[name] = f'http://127.0.0.1:{listen_port}/'

# ################################################################################################################################

    def stop_endpoints(self) -> 'None':
        for endpoint in self.endpoints.values():
            endpoint.stop()

# ################################################################################################################################

    def publish(self, name:'str') -> 'None':
        max_retries, retry_sleep_time = self.retry_settings[name]
        topic_name = _get_topic_name(name)
        message_count = self.message_counts[name]

        for index in range(message_count):
            data = {'endpoint': name, 'index': index}
            result = self.backend.publish(topic_name, data, max_retries=max_retries, retry_sleep_time=retry_sleep_time)
            self.publish_times[result.msg_id] = monotonic()

            if name == _healthy:
                sleep(_healthy_interval_seconds)

# ################################################################################################################################

    def get_queue_depth(self, name:'str') -> 'int':
        sub_key = _get_sub_key(name)

        with self.backend.engine.connect() as connection:
            out = connection.execute(_queue_depth_query, {'sub_key': sub_key}).scalar_one()

        return out

# ################################################################################################################################

    def get_queue_depths(self) -> 'strintdict':
        out:'strintdict' = {}

        for name in self.message_counts:
            out[name] = self.get_queue_depth(name)

        return out

# ################################################################################################################################

    def is_done(self) -> 'bool':

        for name in self.message_counts:
            if self.get_queue_depth(name):
                out = False
                break
        else:
            out = True

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

def _get_failed_msg_ids(name:'str') -> 'strlist':
    sub_key = _get_sub_key(name)
    params = {'event_type': AuditEvent.Delivery_Failed, 'sub_key': sub_key}

    with get_audit_engine().connect() as connection:
        rows = connection.execute(_failed_events_query, params).fetchall()

    out:'strlist' = []

    for row in rows:
        out.append(row.msg_id)

    return out

# ################################################################################################################################

def _get_healthy_p99(run:'_Run') -> 'float':
    latencies:'floatlist' = []

    for request in run.endpoints[_healthy].requests:
        published_at = run.publish_times[request.msg_id]
        latencies.append(request.received_at - published_at)

    latencies.sort()
    index = int(len(latencies) * 0.99)

    out = latencies[index]
    return out

# ################################################################################################################################

def _check(run:'_Run') -> 'None':
    """ What each endpoint received and what was given up.
    """
    endpoints = run.endpoints
    message_counts = run.message_counts

    # The healthy endpoint received its messages without delay ..
    healthy_p99 = _get_healthy_p99(run)
    assert healthy_p99 < _healthy_p99_limit_seconds, healthy_p99

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

    # .. a redirect reached its target, which received each message once ..
    target_attempts = _get_attempts(endpoints[_redirect_target])
    assert len(target_attempts) == message_counts[Behavior_Redirect], target_attempts

    # .. and each message that was never accepted was given up with an audit event.
    for name in _given_up:
        failed_msg_ids = _get_failed_msg_ids(name)
        assert len(failed_msg_ids) == message_counts[name], (name, failed_msg_ids)

        for request in endpoints[name].requests:
            assert not request.is_accepted, (name, request)

# ################################################################################################################################

def _run_endpoints(toxiproxy:'Toxiproxy') -> 'None':
    audit_log = AuditLog(_server_name)
    backend = SQLPubSubBackend(audit_log=audit_log)
    backend.take_over()

    run = _Run(backend, toxiproxy)
    run.start_endpoints()

    stub_server:'any_' = _StubServer()
    push_delivery = PushDelivery(stub_server, backend)

    # Each endpoint is subscribed to a topic of its own and pushed to through its URL ..
    for name in run.message_counts:
        sub_key = _get_sub_key(name)
        topic_name = _get_topic_name(name)

        backend.subscribe(sub_key, topic_name)

        stub_server.config_manager._push_subs[sub_key] = [{
            'topic_name': topic_name,
            'push_type': PubSub.Push_Type.REST,
            'rest_push_url': run.urls[name],
        }]

        push_delivery.start_sub_key(sub_key)

    # .. the messages of all the endpoints are published at the same time ..
    publishers:'anylist' = []

    for name in run.message_counts:
        publisher = spawn(run.publish, name)
        publishers.append(publisher)

    for publisher in publishers:
        _ = publisher.get()

    # .. and the run waits until every queue is empty.
    start = monotonic()

    try:
        while not run.is_done():
            assert monotonic() - start < _run_timeout_seconds, ('Endpoints not done', run.get_queue_depths())
            sleep(_poll_seconds)
    finally:
        push_delivery.stop()
        run.stop_endpoints()

    audit_log.flush()
    _check(run)

# ################################################################################################################################
# ################################################################################################################################

def test_endpoints(endpoint_work_dir:'str') -> 'None':
    """ Push endpoints that read slowly, never respond, respond late, close in the middle of a response, stall
    the TLS handshake or redirect, and push links that are slow, limited, sliced, held, reset or cut.
    """
    audit_db_path = os.path.join(endpoint_work_dir, 'audit.db')
    audit_env:'strstrdict' = {'Zato_Audit_Log_DB_Name': audit_db_path}

    toxiproxy = Toxiproxy('endpoints')
    toxiproxy.start()

    try:
        with pubsub_db_env(audit_env):
            _run_endpoints(toxiproxy)
    finally:
        toxiproxy.stop()

# ################################################################################################################################
# ################################################################################################################################
