# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The push engine as the delivery greenlets use it - the eventfd that hands each completed job to its greenlet,
# a greenlet killed while its job is in flight, an internal error of a job and a stop of the engine with jobs in flight.

# stdlib
import subprocess
import sys
from time import monotonic

# gevent
from gevent import sleep, spawn

# Zato
from common import delete_all_rows, delete_audit_rows, get_delivery_rows, get_event_rows
from fast_path_common import wait_until
from zato.common.api import PubSub
from zato.common.audit_log.api import AuditEvent
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.test.audit_log_ import new_test_audit_log
from zato.common.test.expected_records import expected_records
from zato.common.typing_ import cast_
from zato.server.base.parallel.delivery import PushDelivery
from zato.server.base.parallel.delivery_rest import logger as delivery_rest_logger, Push_Timeout
from zato.server.base.parallel.push_engine_client import PushEngineClient, PushEngineStopped

# Test support
from rest_outgoing_stub.connection import new_connection, ServerStub

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import TextIO
    from gevent import Greenlet
    from zato.common.typing_ import anydict, anylist, anytuple, strlist
    from zato.server.base.parallel import ParallelServer
    from zato.server.base.parallel.push_engine_client import job_outcome

    Greenlet = Greenlet
    ParallelServer = ParallelServer
    TextIO = TextIO

# ################################################################################################################################
# ################################################################################################################################

# The topic and the subscriber of the scenarios
_topic = 'pubsub.backend.test.push-engine'
_sub_key = 'zpsk.test.push-engine.1'

# The ID of the outgoing REST connection of the endpoint of the subscriber
_endpoint_id = 1

# The address of the receiver
_host = '127.0.0.1'

# The payload of the scenarios
_data = 'Order ORD-6001 for John Smith'

# The retry settings of the messages of the scenarios
_retry_sleep_time = 1
_max_retries = 5

# How long the receiver takes to answer each request of each scenario, in seconds
_delay_concurrent = 0.3
_delay_killed = 1.5
_delay_in_flight = 2.0
_delay_none = 0.0

# How many jobs run at once in the scenario of the eventfd, on how many threads
_concurrent_job_count = 8
_concurrent_thread_count = 4

# The description of the internal error that a scenario reports for a job
_internal_error_message = 'Push job of sub_key zpsk.test.push-engine.1 ended by an internal error'

# How long the reader greenlet of the engine is given to hand out an outcome that arrived, in seconds
_handout_seconds = 0.2

# The headers of a push that identify the message and its attempt
_header_msg_id = 'X-Zato-Msg-ID'
_header_attempt = 'X-Zato-Delivery-Attempt'

# What the receiver prints once it listens, once it receives a request and once it answers it
_marker_received = 'received'
_marker_replied = 'replied'

# The receiver, a process of its own, so that it answers while a stop of the engine holds the hub of this process.
# It waits for the number of seconds in the path of each request, answers with HTTP 200 and prints both events.
_receiver_code = """
import sys, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class Handler(BaseHTTPRequestHandler):

    def do_POST(self):
        self.rfile.read(int(self.headers['Content-Length']))
        msg_id = self.headers['X-Zato-Msg-ID']
        attempt = self.headers['X-Zato-Delivery-Attempt']

        print('received', msg_id, attempt, flush=True)
        time.sleep(float(self.path.rsplit('/', 1)[1]))

        self.send_response(200)
        self.send_header('Content-Length', '0')
        self.end_headers()
        print('replied', msg_id, attempt, flush=True)

    def log_message(self, *args):
        pass

server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
print(server.server_port, flush=True)
server.serve_forever()
"""

# ################################################################################################################################
# ################################################################################################################################

class _Receiver:
    """ The receiver process and the events that it printed, each as its marker, the message ID and the attempt.
    """

    def __init__(self) -> 'None':
        self.events:'anylist' = []
        self._process = subprocess.Popen([sys.executable, '-c', _receiver_code], stdout=subprocess.PIPE, text=True)
        self._stdout = cast_('TextIO', self._process.stdout)

        port = self._stdout.readline().strip()
        self.base = f'http://{_host}:{port}'

        self._reader = spawn(self._read_events)

    def _read_events(self) -> 'None':
        for line in self._stdout:
            marker, msg_id, attempt = line.split()
            self.events.append((marker, msg_id, int(attempt)))

    def get_events(self, marker:'str') -> 'anylist':
        """ Returns the message ID and the attempt of each event with the marker, in their order.
        """
        out:'anylist' = []

        for event_marker, msg_id, attempt in self.events:
            if event_marker == marker:
                out.append((msg_id, attempt))

        return out

    def stop(self) -> 'None':
        self._process.terminate()
        _ = self._process.wait()
        self._reader.kill()

# ################################################################################################################################

class _OutconnItem:
    """ An outgoing REST connection as the config store holds it, with its address and its connection.
    """
    def __init__(self, base:'str', path:'str') -> 'None':
        self.config = {'host': base, 'url_path': path}
        self.conn = new_connection(ServerStub(), base, path)

# ################################################################################################################################

class _OutconnStore:
    """ The outgoing REST connections of the config store, which hold the connection of the subscriber.
    """
    def __init__(self, item:'_OutconnItem') -> 'None':
        self._item = item

    def get_by_id(self, endpoint_id:'int') -> '_OutconnItem':
        return self._item

# ################################################################################################################################

class _StubConfigStore:
    """ The part of the config store that a delivery reads.
    """
    def __init__(self, item:'_OutconnItem') -> 'None':
        self.out_plain_http = _OutconnStore(item)

# ################################################################################################################################

class _StubConfigManager:
    """ Carries the push subscriptions and the config store the way the config manager of the server does.
    """
    def __init__(self, config_store:'_StubConfigStore') -> 'None':
        self._push_subs:'anydict' = {}
        self.config_store = config_store

# ################################################################################################################################

class _StubServer:
    """ Stands in for the server, of which a delivery reads the push subscriptions and the config store.
    """
    def __init__(self, config_store:'_StubConfigStore') -> 'None':
        self.config_manager = _StubConfigManager(config_store)

# ################################################################################################################################

class _InternalErrorOnceClient(PushEngineClient):
    """ A client of the push engine that reports the outcome of its first job as an internal error.
    """
    internal_error_count: 'int'

    def run(self, requests:'anylist', timeout:'float | None', tls:'anytuple') -> 'job_outcome':

        out = super().run(requests, timeout, tls)

        if self.internal_error_count > 0:
            self.internal_error_count -= 1
            out = (_internal_error_message, [])

        return out

# ################################################################################################################################
# ################################################################################################################################

def _get_path(delay:'float') -> 'str':
    """ Returns the path under which the receiver answers each request after the given number of seconds.
    """
    out = f'/delay/{delay}'
    return out

# ################################################################################################################################

def _new_request(base:'str', delay:'float', msg_id:'str') -> 'anytuple':
    """ Returns one push request of one message, as the push engine takes it.
    """
    url = base + _get_path(delay)

    headers = {
        'Content-Type': 'application/json',
        _header_msg_id: msg_id,
        _header_attempt: '1',
    }

    parts = (f'{{"msg_id":"{msg_id}"}}'.encode('utf8'),)

    out = (url, headers, parts, [msg_id], False)
    return out

# ################################################################################################################################

def _get_tls(base:'str') -> 'anytuple':
    """ Returns the TLS settings of the pushes to the receiver.
    """
    conn = new_connection(ServerStub(), base, _get_path(_delay_none))

    out = conn.get_push_tls()
    return out

# ################################################################################################################################

def _get_concluded(outcome:'job_outcome') -> 'strlist':
    """ Returns the IDs of the messages that the only request of a job concluded.
    """
    internal_error, outcomes = outcome
    assert internal_error is None, internal_error

    [request_outcome] = outcomes
    out = request_outcome[3]

    return out

# ################################################################################################################################

def _new_delivery(receiver:'_Receiver', delay:'float') -> 'tuple[SQLPubSubBackend, PushDelivery, str]':
    """ Returns a backend over empty tables, the delivery of its subscriber to the receiver, one message at a time,
    and the ID of the message published for it. The receiver forgets the events of the scenarios before.
    """
    delete_all_rows()
    delete_audit_rows()

    receiver.events.clear()

    backend = SQLPubSubBackend(audit_log=new_test_audit_log())
    backend.subscribe(_sub_key, _topic)

    config_store = _StubConfigStore(_OutconnItem(receiver.base, _get_path(delay)))

    server = _StubServer(config_store)
    server.config_manager._push_subs[_sub_key] = [{
        'sub_key': _sub_key,
        'topic_name': _topic,
        'push_type': PubSub.Push_Type.REST,
        'rest_push_endpoint_id': _endpoint_id,
        'push_batch_size': 1,
    }]

    delivery = PushDelivery(cast_('ParallelServer', server), backend)

    msg_id = backend.publish(_topic, _data, max_retries=_max_retries, retry_sleep_time=_retry_sleep_time).msg_id

    out = (backend, delivery, msg_id)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _run_eventfd(receiver:'_Receiver') -> 'None':
    """ The jobs of several greenlets that run at once each wake their own greenlet up with their own outcome.
    """
    client = PushEngineClient(_concurrent_thread_count, _concurrent_thread_count, Push_Timeout)
    tls = _get_tls(receiver.base)

    def _run(msg_id:'str') -> 'strlist':
        request = _new_request(receiver.base, _delay_concurrent, msg_id)
        outcome = client.run([request], Push_Timeout, tls)

        out = _get_concluded(outcome)
        return out

    try:
        jobs:'anylist' = []

        for idx in range(_concurrent_job_count):
            msg_id = f'zpsm.test.push-engine.concurrent.{idx}'
            job = spawn(_run, msg_id)
            jobs.append((msg_id, job))

        for msg_id, job in jobs:
            concluded = job.get()
            assert concluded == [msg_id], (msg_id, concluded)

    finally:
        _ = client.stop()

    assert client._results == {}, client._results

# ################################################################################################################################

def _run_killed(receiver:'_Receiver') -> 'None':
    """ A delivery greenlet killed while its job is in flight discards the outcome of the job, and the message,
    which nothing acknowledged, is delivered again with its next attempt.
    """
    _, delivery, msg_id = _new_delivery(receiver, _delay_killed)

    try:
        delivery.start_sub_key(_sub_key)

        # The greenlet is killed while the endpoint holds its request ..
        wait_until(lambda: len(receiver.get_events(_marker_received)) == 1, 'the first push is received')
        delivery.stop_sub_key(_sub_key)

        # .. and the next one delivers the message again ..
        delivery.start_sub_key(_sub_key)

        wait_until(lambda: len(receiver.get_events(_marker_replied)) == 2, 'both pushes are answered')
        wait_until(lambda: get_delivery_rows(_sub_key) == [], 'the message is acknowledged')

        # .. while the outcome of the killed job, which arrived as well, had no greenlet to go to.
        sleep(_handout_seconds)

        reader = cast_('Greenlet', delivery.push_engine._reader)

        assert not reader.dead
        assert delivery.push_engine._results == {}, delivery.push_engine._results

    finally:
        delivery.stop()

    received = receiver.get_events(_marker_received)
    assert received == [(msg_id, 1), (msg_id, 2)], received

# ################################################################################################################################

def _run_internal_error(receiver:'_Receiver') -> 'None':
    """ A job ended by an internal error fails its attempt with that error, and the engine serves the next attempt.
    """
    _, delivery, msg_id = _new_delivery(receiver, _delay_none)

    client = _InternalErrorOnceClient(_concurrent_thread_count, _concurrent_thread_count, Push_Timeout)
    client.internal_error_count = 1
    delivery.push_engine = client

    try:
        with expected_records(delivery_rest_logger.name):
            delivery.start_sub_key(_sub_key)

            wait_until(lambda: len(receiver.get_events(_marker_replied)) == 2, 'both pushes are answered')
            wait_until(lambda: get_delivery_rows(_sub_key) == [], 'the message is acknowledged')

    finally:
        delivery.stop()

    received = receiver.get_events(_marker_received)
    assert received == [(msg_id, 1), (msg_id, 2)], received

    delivered:'strlist' = []

    for row in get_event_rows(_topic, AuditEvent.Delivered):
        delivered.append(row['msg_id'])

    assert delivered == [msg_id], delivered

# ################################################################################################################################

def _run_stop_in_flight(receiver:'_Receiver') -> 'None':
    """ A stop of the engine waits for the job in flight, which completes with its outcome, within the push timeout,
    while a job not yet started fails with PushEngineStopped, and so does any job submitted after the stop.
    """
    client = PushEngineClient(1, 1, Push_Timeout)
    tls = _get_tls(receiver.base)

    msg_id_in_flight = 'zpsm.test.push-engine.in-flight'
    msg_id_queued = 'zpsm.test.push-engine.queued'

    request_in_flight = _new_request(receiver.base, _delay_in_flight, msg_id_in_flight)
    request_queued = _new_request(receiver.base, _delay_none, msg_id_queued)

    # The only thread of the engine takes the first job ..
    in_flight = spawn(client.run, [request_in_flight], Push_Timeout, tls)

    def _is_in_flight() -> 'bool':
        for msg_id, _ in receiver.get_events(_marker_received):
            if msg_id == msg_id_in_flight:
                return True
        return False

    wait_until(_is_in_flight, 'the first job is in flight')

    # .. while the second one waits behind it ..
    queued = spawn(client.run, [request_queued], Push_Timeout, tls)
    wait_until(lambda: len(client._results) == 2, 'the second job is submitted')

    # .. and the stop waits for the first one alone.
    start = monotonic()
    is_stopped = client.stop()
    elapsed = monotonic() - start

    assert is_stopped
    assert elapsed < Push_Timeout, elapsed

    concluded = _get_concluded(in_flight.get())
    assert concluded == [msg_id_in_flight], concluded

    try:
        _ = queued.get()
    except PushEngineStopped:
        pass
    else:
        raise Exception('Expected PushEngineStopped for the queued job')

    try:
        _ = client.run([request_queued], Push_Timeout, tls)
    except PushEngineStopped:
        pass
    else:
        raise Exception('Expected PushEngineStopped after the stop')

    for msg_id, _ in receiver.get_events(_marker_received):
        assert msg_id != msg_id_queued, msg_id

# ################################################################################################################################
# ################################################################################################################################

def run_push_engine_scenario() -> 'None':
    """ The push engine under concurrent jobs, killed greenlets, internal errors and a stop with jobs in flight.
    """
    receiver = _Receiver()

    try:
        _run_eventfd(receiver)
        _run_killed(receiver)
        _run_internal_error(receiver)
        _run_stop_in_flight(receiver)

    finally:
        receiver.stop()

# ################################################################################################################################
# ################################################################################################################################
