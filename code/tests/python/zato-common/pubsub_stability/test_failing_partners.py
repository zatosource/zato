# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass
from logging import getLogger
from time import monotonic

# gevent
from gevent import sleep, spawn
from gevent.pywsgi import WSGIServer

# SQLAlchemy
from sqlalchemy import text

# Zato
from zato.common.api import PubSub
from zato.common.audit_log.api import AuditLog, get_audit_engine
from zato.common.audit_log.common import AuditEvent
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.test.pubsub_database import pubsub_db_env
from zato.server.base.parallel.delivery import PushDelivery

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, callable_, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato.test.pubsub_stability.failing_partners')

# ################################################################################################################################
# ################################################################################################################################

# The name under which the audit events of the run are written.
_server_name = 'stability.partners'

# The partners, each with a push endpoint of its own.
_healthy = 'healthy'
_slow = 'slow'
_flaky = 'flaky'
_failing = 'failing'
_unresponsive = 'unresponsive'

_partner_names = [_healthy, _slow, _flaky, _failing, _unresponsive]

# How long the slow partner takes to respond, in seconds.
_slow_response_seconds = 2

# Every that many requests the flaky partner responds with HTTP 500, which is 20 percent of them.
_flaky_failure_every = 5

# How long the unresponsive partner holds a request without responding, in seconds.
_unresponsive_hold_seconds = 3600

# How many messages each partner receives, and how often the healthy partner receives one, in seconds.
_message_counts = {
    _healthy: 600,
    _slow: 10,
    _flaky: 200,
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

_header_msg_id = 'HTTP_X_ZATO_MSG_ID'
_header_attempt = 'HTTP_X_ZATO_DELIVERY_ATTEMPT'

_queue_depth_query = text('select count(*) from pubsub_delivery where sub_key = :sub_key')
_failed_events_query = text('select msg_id from event where event_type = :event_type and sub_key = :sub_key')

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
    """ The push endpoints of all the partners, recording each request that reaches them.
    """

    def __init__(self) -> 'None':
        self.requests:'dict[str, request_list]' = {}
        self.flaky_request_count = 0

        for name in _partner_names:
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

    def __call__(self, environ:'anydict', start_response:'callable_') -> 'anylist':

        # The request body is read in full, as a real partner would read it ..
        _ = environ['wsgi.input'].read()

        name = environ['PATH_INFO'].strip('/')

        # .. the request is recorded on arrival, including one that is never responded to ..
        request = _Request()
        request.msg_id = environ[_header_msg_id]
        request.attempt = int(environ[_header_attempt])
        request.received_at = monotonic()
        request.is_accepted = False

        self.requests[name].append(request)

        # .. the partner behaves as it does ..
        request.is_accepted = self._respond(name)

        # .. and the response tells the delivery how it went.
        if request.is_accepted:
            start_response('200 OK', [('Content-Type', 'application/json')])
        else:
            start_response('500 Internal Server Error', [('Content-Type', 'application/json')])

        out = [b'{}']
        return out

# ################################################################################################################################
# ################################################################################################################################

class _StubConfigManager:
    """ Holds the push subscriptions the way the configuration manager of a server does.
    """
    def __init__(self) -> 'None':
        self._push_subs:'anydict' = {}

class _StubServer:
    """ Stands in for the server whose push delivery the suite runs.
    """
    def __init__(self) -> 'None':
        self.config_manager = _StubConfigManager()

# ################################################################################################################################
# ################################################################################################################################

def _get_sub_key(name:'str') -> 'str':
    out = f'zpsk.stability.partners.{name}'
    return out

# ################################################################################################################################

def _get_topic_name(name:'str') -> 'str':
    out = f'stability.partners.{name}'
    return out

# ################################################################################################################################

def _publish(backend:'SQLPubSubBackend', name:'str', publish_times:'anydict') -> 'None':
    """ Publishes the messages of one partner, recording when each one was published.
    """
    max_retries, retry_sleep_time = _retry_settings[name]
    topic_name = _get_topic_name(name)

    for index in range(_message_counts[name]):

        result = backend.publish(topic_name, {'partner': name, 'index': index},
            max_retries=max_retries, retry_sleep_time=retry_sleep_time)

        publish_times[result.msg_id] = monotonic()

        if name == _healthy:
            sleep(_healthy_interval_seconds)

# ################################################################################################################################

def _get_queue_depth(backend:'SQLPubSubBackend', name:'str') -> 'int':
    with backend.engine.connect() as connection:
        out = connection.execute(_queue_depth_query, {'sub_key': _get_sub_key(name)}).scalar_one()
    return out

# ################################################################################################################################

def _get_accepted_msg_ids(partners:'_Partners', name:'str') -> 'set[str]':
    out:'set[str]' = set()

    for request in partners.requests[name]:
        if request.is_accepted:
            out.add(request.msg_id)

    return out

# ################################################################################################################################

def _get_failed_msg_ids(name:'str') -> 'strlist':
    """ Returns the messages of a partner for which the audit log records a delivery that was given up.
    """
    params = {'event_type': AuditEvent.Delivery_Failed, 'sub_key': _get_sub_key(name)}

    with get_audit_engine().connect() as connection:
        rows = connection.execute(_failed_events_query, params).fetchall()

    out:'strlist' = []
    for row in rows:
        out.append(row.msg_id)

    return out

# ################################################################################################################################

def _get_queue_depths(backend:'SQLPubSubBackend') -> 'anydict':
    out:'anydict' = {}

    for name in _partner_names:
        out[name] = _get_queue_depth(backend, name)

    return out

# ################################################################################################################################

def _is_done(backend:'SQLPubSubBackend', partners:'_Partners') -> 'bool':
    """ Whether each partner received its messages and every queue is empty.
    """
    for name in _partner_names:
        if _get_queue_depth(backend, name):
            return False

    for name in (_healthy, _slow, _flaky):
        if len(_get_accepted_msg_ids(partners, name)) < _message_counts[name]:
            return False

    return True

# ################################################################################################################################

def _get_healthy_p99(partners:'_Partners', publish_times:'anydict') -> 'float':
    """ How long the healthy partner waited for its messages at the 99th percentile, in seconds.
    """
    latencies:'list[float]' = []

    for request in partners.requests[_healthy]:
        latency = request.received_at - publish_times[request.msg_id]
        latencies.append(latency)

    latencies.sort()
    index = int(len(latencies) * 0.99)
    out = latencies[index]

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

def _run_partners() -> 'None':
    """ Runs all the partners against a backend whose audit log is in the work directory of the run.
    """
    partners = _Partners()
    server = WSGIServer(('127.0.0.1', 0), partners, log=None, error_log=None)
    server.start()

    audit_log = AuditLog(_server_name)
    backend = SQLPubSubBackend(audit_log=audit_log)
    backend.take_over()

    stub_server:'any_' = _StubServer()
    push_delivery = PushDelivery(stub_server, backend)

    # Each partner is subscribed to a topic of its own and pushed to through its endpoint ..
    for name in _partner_names:

        sub_key = _get_sub_key(name)
        topic_name = _get_topic_name(name)

        backend.subscribe(sub_key, topic_name)

        stub_server.config_manager._push_subs[sub_key] = [{
            'topic_name': topic_name,
            'push_type': PubSub.Push_Type.REST,
            'rest_push_url': f'http://127.0.0.1:{server.server_port}/{name}',
        }]

        push_delivery.start_sub_key(sub_key)

    # .. the messages of all the partners are published at the same time ..
    publish_times:'anydict' = {}
    publishers:'anylist' = []

    for name in _partner_names:
        publisher = spawn(_publish, backend, name, publish_times)
        publishers.append(publisher)

    for publisher in publishers:
        _ = publisher.get()

    # .. and the run waits until every partner received its messages and every queue is empty.
    start = monotonic()

    try:
        while not _is_done(backend, partners):
            assert monotonic() - start < _run_timeout_seconds, ('Partners not done', _get_queue_depths(backend))
            sleep(_poll_seconds)
    finally:
        push_delivery.stop()
        server.stop(timeout=1)

    audit_log.flush()

    # The healthy partner received each of its messages once and without delay ..
    healthy_requests = partners.requests[_healthy]
    assert len(healthy_requests) == _message_counts[_healthy], len(healthy_requests)

    healthy_p99 = _get_healthy_p99(partners, publish_times)
    logger.info('Healthy partner p99 -> %.3fs', healthy_p99)
    assert healthy_p99 < _healthy_p99_limit_seconds, healthy_p99

    # .. the slow partner received each of its messages once ..
    assert len(partners.requests[_slow]) == _message_counts[_slow], len(partners.requests[_slow])

    # .. the flaky partner accepted each of its messages once, after a retry where it failed one ..
    flaky_accepted = _get_accepted_msg_ids(partners, _flaky)
    assert len(flaky_accepted) == _message_counts[_flaky], len(flaky_accepted)

    flaky_rejected = len(partners.requests[_flaky]) - _message_counts[_flaky]
    assert flaky_rejected == len(partners.requests[_flaky]) // _flaky_failure_every, flaky_rejected

    # .. the failing and the unresponsive partners received every attempt that the retry settings allow ..
    _check_attempts(partners, _failing, _retry_settings[_failing][0] + 1)
    _check_attempts(partners, _unresponsive, _retry_settings[_unresponsive][0] + 1)

    # .. and each message they never accepted was given up with an audit event.
    for name in (_failing, _unresponsive):
        failed_msg_ids = _get_failed_msg_ids(name)
        assert len(failed_msg_ids) == _message_counts[name], (name, failed_msg_ids)

# ################################################################################################################################
# ################################################################################################################################

def test_failing_partners(stability_env:'strstrdict') -> 'None':
    """ Push partners that respond slowly, fail some requests, fail all of them or never respond receive what
    their retry settings allow, the messages they never accept are given up with an audit event each,
    and the healthy partner receives its messages without delay throughout.
    """
    work_dir = os.path.dirname(stability_env['Zato_PubSub_Generation_File'])

    audit_env:'strstrdict' = {'Zato_Audit_Log_DB_Name': os.path.join(work_dir, 'audit.db')}

    with pubsub_db_env(audit_env):
        _run_partners()

# ################################################################################################################################
# ################################################################################################################################
