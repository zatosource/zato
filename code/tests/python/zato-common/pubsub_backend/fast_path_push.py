# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
from gevent.event import Event

# Zato
from common import delete_all_rows, delete_audit_rows, get_delivery_rows, get_message_rows
from fast_path_common import ClaimFailed, HookedFastPath, install_hooked_fast_path, wait_until
from zato.common.api import PubSub
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.fast_path import State_Waiting
from zato.common.test.audit_log_ import new_test_audit_log
from zato.common.typing_ import cast_
from zato.server.base.parallel.delivery import PushDelivery

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, intlist, intset
    from zato.server.base.parallel import ParallelServer

    # Dummy assignments to satisfy type checkers
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

# The topic, the subscribers and the target service of the scenario
_topic = 'pubsub.backend.test.fast-path-push'
_sub_key = 'zpsk.test.fast-path-push.1'
_sub_key_outgoing = PubSub.Outgoing.Sub_Key_Prefix + 'test.fast-path-push'
_service_name = 'test.fast-path-push.target'

# The payloads of the scenario
_data_first = 'Order ORD-3001 for John Smith'
_data_second = 'Order ORD-3002 for Maria Johnson'

# ################################################################################################################################
# ################################################################################################################################

class _StubQueueDepth:
    """ Carries the depths of the queues of outgoing connections the way the config manager does.
    """
    def lower(self, sub_key:'str', count:'int') -> 'None':
        pass

# ################################################################################################################################

class _StubConfigManager:
    """ Carries the push subscriptions the way the config manager of the server does.
    """
    def __init__(self) -> 'None':
        self._push_subs:'anydict' = {}
        self.outgoing_queue_depth = _StubQueueDepth()

# ################################################################################################################################

class _StubServer:
    """ Stands in for the server - records each invocation with the attempts of the delivery rows of its subscriber
    at that time, fails the requested number of invocations first and blocks the first one while asked to.
    """
    def __init__(self) -> 'None':
        self.config_manager = _StubConfigManager()
        self.sub_key = _sub_key
        self.invoked:'anylist' = []
        self.attempts:'intlist' = []
        self.fail_count = 0
        self.block_event:'Event | None' = None

    def invoke(self, service_name:'str', payload:'any_', data_format:'str', request_ctx:'any_'=None) -> 'None':

        for row in get_delivery_rows(self.sub_key):
            self.attempts.append(row.attempt)

        if self.block_event:
            block_event = self.block_event
            self.block_event = None
            _ = block_event.wait()

        if self.fail_count > 0:
            self.fail_count -= 1
            raise Exception('Simulated delivery failure')

        self.invoked.append(payload)

# ################################################################################################################################
# ################################################################################################################################

class _CountingBackend(SQLPubSubBackend):
    """ A backend that counts the transactions that record the attempts of push deliveries.
    """
    record_attempts_count: 'int'
    record_attempt_count: 'int'

    def record_attempts(self, messages:'anylist') -> 'intset':
        self.record_attempts_count += 1

        out = super().record_attempts(messages)
        return out

    def record_attempt(self, message:'anydict') -> 'bool':
        self.record_attempt_count += 1

        out = super().record_attempt(message)
        return out

# ################################################################################################################################
# ################################################################################################################################

def _new_backend(sub_key:'str') -> 'tuple[_CountingBackend, HookedFastPath, _StubServer, PushDelivery]':
    """ Returns a backend with one push subscriber, its observed fast path, the stub server and the delivery,
    starting from empty tables.
    """
    delete_all_rows()
    delete_audit_rows()

    backend = _CountingBackend(audit_log=new_test_audit_log())
    backend.record_attempts_count = 0
    backend.record_attempt_count = 0

    fast_path = install_hooked_fast_path(backend)

    server = _StubServer()
    server.sub_key = sub_key
    server.config_manager._push_subs[sub_key] = [{
        'topic_name': _topic,
        'push_type': PubSub.Push_Type.Service,
        'push_service_name': _service_name,
    }]

    backend.subscribe(sub_key, _topic)

    delivery = PushDelivery(cast_('ParallelServer', server), backend)

    out = (backend, fast_path, server, delivery)
    return out

# ################################################################################################################################

def _wait_until_idle(backend:'SQLPubSubBackend', sub_key:'str') -> 'None':
    """ Waits until the delivery greenlet of the subscriber waits for a publication as a target of the fast path.
    """
    def _is_idle() -> 'bool':
        if target := backend.fast_path._push_targets.get(sub_key):
            out = target.state == State_Waiting
        else:
            out = False

        return out

    wait_until(_is_idle, 'the delivery greenlet waits for a publication')

# ################################################################################################################################

def _wait_until_delivered(server:'_StubServer', count:'int', sub_key:'str') -> 'None':
    """ Waits until the given number of messages was delivered and acknowledged.
    """
    def _is_delivered() -> 'bool':
        if len(server.invoked) == count:
            out = get_delivery_rows(sub_key) == []
        else:
            out = False

        return out

    wait_until(_is_delivered, f'{count} messages are delivered and acknowledged')

# ################################################################################################################################
# ################################################################################################################################

def _run_handover() -> 'None':
    """ An idle delivery greenlet is handed a publication with its first attempt recorded in the transaction
    of the publication, so no transaction of its own records it.
    """
    backend, _, server, delivery = _new_backend(_sub_key)

    try:
        delivery.start_sub_key(_sub_key)
        _wait_until_idle(backend, _sub_key)

        _ = backend.publish(_topic, _data_first)
        _wait_until_delivered(server, 1, _sub_key)

        assert server.attempts == [1], server.attempts
        assert backend.record_attempts_count == 0, backend.record_attempts_count
        assert backend.record_attempt_count == 0, backend.record_attempt_count

    finally:
        delivery.stop()

# ################################################################################################################################

def _run_retry() -> 'None':
    """ A message handed over whose first push fails is pushed again with the second attempt, which its own
    transaction records.
    """
    backend, _, server, delivery = _new_backend(_sub_key)
    server.fail_count = 1

    try:
        delivery.start_sub_key(_sub_key)
        _wait_until_idle(backend, _sub_key)

        _ = backend.publish(_topic, _data_first)
        _wait_until_delivered(server, 1, _sub_key)

        assert server.attempts == [1, 2], server.attempts
        assert backend.record_attempts_count == 0, backend.record_attempts_count
        assert backend.record_attempt_count == 1, backend.record_attempt_count

    finally:
        delivery.stop()

# ################################################################################################################################

def _run_rolled_back() -> 'None':
    """ A publication whose transaction does not commit hands nothing over, and the greenlet that it claimed
    waits on as a target and is handed the next publication.
    """
    backend, fast_path, server, delivery = _new_backend(_sub_key)
    fast_path.fail_count = 1

    try:
        delivery.start_sub_key(_sub_key)
        _wait_until_idle(backend, _sub_key)

        try:
            _ = backend.publish(_topic, _data_first)
        except ClaimFailed:
            pass
        else:
            raise Exception('Expected ClaimFailed')

        assert get_message_rows(_topic) == []
        assert get_delivery_rows(_sub_key) == []

        _wait_until_idle(backend, _sub_key)

        _ = backend.publish(_topic, _data_second)
        _wait_until_delivered(server, 1, _sub_key)

        assert server.attempts == [1], server.attempts
        assert backend.record_attempts_count == 0, backend.record_attempts_count

    finally:
        delivery.stop()

# ################################################################################################################################

def _run_paused() -> 'None':
    """ A subscriber paused between the claim and the handover discards the handover, and its row, with the first attempt
    recorded, is pushed with the second attempt once the subscriber resumes.
    """
    backend, fast_path, server, delivery = _new_backend(_sub_key)

    def _pause() -> 'None':
        delivery._paused.add(_sub_key)

    fast_path.on_claimed = _pause

    try:
        delivery.start_sub_key(_sub_key)
        _wait_until_idle(backend, _sub_key)

        _ = backend.publish(_topic, _data_first)
        fast_path.on_claimed = None

        delivery.pause_sub_key(_sub_key)

        assert server.invoked == []

        [row] = get_delivery_rows(_sub_key)
        assert row.attempt == 1, row

        delivery.resume_sub_key(_sub_key)
        _wait_until_delivered(server, 1, _sub_key)

        assert server.attempts == [2], server.attempts

    finally:
        delivery.stop()

# ################################################################################################################################

def _run_busy() -> 'None':
    """ A publication that finds the delivery greenlet busy inserts its row as before, and the greenlet reads it
    and records its attempt itself once it is idle again.
    """
    backend, _, server, delivery = _new_backend(_sub_key)

    block_event = Event()
    server.block_event = block_event

    try:
        delivery.start_sub_key(_sub_key)
        _wait_until_idle(backend, _sub_key)

        _ = backend.publish(_topic, _data_first)

        def _is_busy() -> 'bool':
            return len(server.attempts) == 1

        wait_until(_is_busy, 'the first message is being pushed')

        assert _sub_key not in backend.fast_path._push_targets

        _ = backend.publish(_topic, _data_second)

        attempts:'intlist' = []

        for row in get_delivery_rows(_sub_key):
            attempts.append(row.attempt)

        assert attempts == [1, 0], attempts

        block_event.set()
        _wait_until_delivered(server, 2, _sub_key)

        assert backend.record_attempts_count == 1, backend.record_attempts_count

    finally:
        delivery.stop()

# ################################################################################################################################

def _run_outgoing() -> 'None':
    """ The queue of an outgoing connection acknowledges each message on its own, so its greenlet never waits
    as a target of the fast path and records each attempt itself.
    """
    backend, fast_path, server, delivery = _new_backend(_sub_key_outgoing)

    try:
        delivery.start_sub_key(_sub_key_outgoing)

        _ = backend.publish(_topic, _data_first)
        _wait_until_delivered(server, 1, _sub_key_outgoing)

        assert fast_path.registered_push_keys == [], fast_path.registered_push_keys
        assert backend.record_attempts_count == 0, backend.record_attempts_count
        assert backend.record_attempt_count == 1, backend.record_attempt_count

    finally:
        delivery.stop()

# ################################################################################################################################
# ################################################################################################################################

def run_fast_path_push_scenario() -> 'None':
    """ Push greenlets that wait for publications and are handed their messages in the transactions of the publications.
    """
    _run_handover()
    _run_retry()
    _run_rolled_back()
    _run_paused()
    _run_busy()
    _run_outgoing()

# ################################################################################################################################
# ################################################################################################################################
