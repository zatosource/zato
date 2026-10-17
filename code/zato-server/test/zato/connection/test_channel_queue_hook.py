# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The get_queue_response hook of a channel whose queue is on - it runs in a greenlet of its own, after the request
# is in the queue, and the channel waits for it without holding up any other request.

# stdlib
from time import monotonic
from unittest import main, TestCase
from unittest.mock import MagicMock, patch

# gevent
from gevent import getcurrent, sleep, spawn
from gevent.event import Event

# Zato
from zato.common.api import DATA_FORMAT, HTTP_SOAP, URL_TYPE
from zato.common.pubsub.sql.backend import PublishResult
from zato.server.connection.http_soap.channel_queue import QueuedChannelHandler
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

_queue = HTTP_SOAP.Queue

_cid_1 = '20260115-101500-0001-abcdef012-server1'
_cid_2 = '20260115-101500-0002-abcdef012-server1'

_msg_id_prefix = 'zpsm-'

# How long the slow hook takes, and how long a request waiting on a blocked one is given to finish
_hook_delay = 0.1
_join_timeout = 2.0

# The targets of the patches - the handler stores a request and starts the hook through these names
_publisher_target = 'zato.server.connection.http_soap.channel_queue.OutgoingPublisher'
_spawn_target = 'zato.server.connection.http_soap.channel_queue.spawn'

# ################################################################################################################################
# ################################################################################################################################

class _Publisher:
    """ Stands in for the channel's publisher - the message id is derived from the cid, so each request gets its own.
    """
    called_at:'float | None' = None
    requests:'anylist' = []

    def __init__(self, server:'any_', conn_type:'str', conn_id:'int') -> 'None':
        pass

    def publish_request(self, cid:'str', attempts:'int', request:'stranydict') -> 'PublishResult':
        _Publisher.called_at = monotonic()
        _Publisher.requests.append(cid)

        out = PublishResult()
        out.msg_id = _msg_id_prefix + cid

        return out

# ################################################################################################################################
# ################################################################################################################################

class _TestService(Service):
    """ The class-level boilerplate a deployed service carries, which ServiceStore would otherwise set up.
    """
    _config_manager = MagicMock()
    _config_store = MagicMock()
    amqp = MagicMock()

    has_io = False
    component_enabled_email = False
    component_enabled_odoo = False

    def handle(self) -> 'None':
        raise AssertionError('handle never runs while the response of a queued request is being shaped')

# ################################################################################################################################

class _HookService(_TestService):
    """ A service with the hook - each instance records what the hook saw and may wait before returning.
    """
    _Service__service_name = 'orders.queued'
    _Service__service_impl_name = 'orders.api.QueuedService'

    has_get_queue_response = True

    def __init__(self) -> 'None':
        super().__init__()

        self.record:'anydict' = {}

        # What the hook waits on before it returns - a gate another greenlet opens, or a delay, or nothing
        self.gate:'Event | None' = None
        self.delay = 0.0
        self.error:'Exception | None' = None

    def get_queue_response(self) -> 'None':

        self.record['greenlet'] = getcurrent()
        self.record['started_at'] = monotonic()
        self.record['publisher_called_at'] = _Publisher.called_at
        self.record['msg_id'] = self.request.queue.msg_id
        self.record['cid'] = self.cid

        if self.error:
            raise self.error

        if self.gate:
            _ = self.gate.wait()

        if self.delay:
            sleep(self.delay)

        self.record['finished_at'] = monotonic()
        self.response.payload = {'cid': self.cid, 'msg_id': self.request.queue.msg_id}

# ################################################################################################################################

class _PlainService(_TestService):
    """ A service without the hook.
    """
    _Service__service_name = 'orders.plain'
    _Service__service_impl_name = 'orders.api.PlainService'

# ################################################################################################################################
# ################################################################################################################################

def _new_channel_item() -> 'anydict':
    out = {
        'id': 17,
        'name': 'Order Intake',
        'service_name': 'orders.queued',
        'service_impl_name': 'orders.api.QueuedService',
        'data_format': DATA_FORMAT.JSON,
        'transport': URL_TYPE.PLAIN_HTTP,
        'merge_url_params_req': True,
        'params_pri': 'channel-params-over-msg',
        _queue.Field_Use_Queue: True,
        _queue.Field_Queue_Response: '',
    }
    return out

# ################################################################################################################################

def _new_request_ctx(channel_item:'anydict') -> 'stranydict':
    out = {
        'REQUEST_METHOD': 'POST',
        'PATH_INFO': '/orders',
        'QUERY_STRING': '',
        'zato.channel_item': channel_item,
    }
    return out

# ################################################################################################################################

def _flatten(query_string:'str') -> 'anydict':
    out:'anydict' = {}
    return out

# ################################################################################################################################

def _set_response(service:'any_', **kwargs:'any_') -> 'any_':
    out = service.response
    return out

# ################################################################################################################################
# ################################################################################################################################

class HookGreenletTestCase(TestCase):

    def setUp(self) -> 'None':
        _Publisher.called_at = None
        _Publisher.requests = []

        self.server = MagicMock()
        self.config_manager = MagicMock()

        # The instances the service store hands out, in the order the handler asks for them
        self.instances:'list[Service]' = []
        self.server.service_store.new_instance.side_effect = self._new_instance

        self.handler = QueuedChannelHandler(self.server, _set_response, _flatten)

        self.publisher_patch = patch(_publisher_target, _Publisher)
        _ = self.publisher_patch.start()
        self.addCleanup(self.publisher_patch.stop)

# ################################################################################################################################

    def _new_instance(self, impl_name:'str') -> 'tuple[Service, bool]':
        """ What the service store answers when the handler needs an instance - the next one a test prepared.
        """
        out = (self.instances.pop(0), True)
        return out

# ################################################################################################################################

    def _handle(self, service:'Service', cid:'str') -> 'any_':
        """ Runs one request through the handler the way the channel does - with the service's class, the instance is
        what the service store hands out - returning the response the caller gets.
        """
        channel_item = _new_channel_item()
        request_ctx = _new_request_ctx(channel_item)

        self.instances.append(service)

        out = self.handler.handle(cid, type(service), {'order_id': 1234}, b'{"order_id": 1234}', {}, channel_item,
            request_ctx, self.config_manager, {}, {})

        return out

# ################################################################################################################################

    def test_the_hook_runs_in_a_greenlet_of_its_own(self) -> 'None':

        service = _HookService()
        _ = self._handle(service, _cid_1)

        self.assertIsNot(service.record['greenlet'], getcurrent())

# ################################################################################################################################

    def test_the_message_is_in_the_queue_before_the_hook_starts(self) -> 'None':

        service = _HookService()
        _ = self._handle(service, _cid_1)

        publisher_called_at = service.record['publisher_called_at']

        self.assertIsNotNone(publisher_called_at)
        self.assertLessEqual(publisher_called_at, service.record['started_at'])

# ################################################################################################################################

    def test_the_channel_waits_for_the_hook(self) -> 'None':

        service = _HookService()
        service.delay = _hook_delay

        response = self._handle(service, _cid_1)
        response_built_at = monotonic()

        self.assertEqual(response.payload, {'cid': _cid_1, 'msg_id': _msg_id_prefix + _cid_1})
        self.assertGreaterEqual(response_built_at, service.record['finished_at'])
        self.assertGreaterEqual(service.record['finished_at'] - service.record['started_at'], _hook_delay)

# ################################################################################################################################

    def test_a_hook_that_raises_surfaces_and_the_message_stays_queued(self) -> 'None':

        service = _HookService()
        service.error = ValueError('No response could be built')

        with self.assertRaises(ValueError):
            _ = self._handle(service, _cid_1)

        self.assertEqual(_Publisher.requests, [_cid_1])

# ################################################################################################################################

    def test_a_blocked_hook_does_not_block_another_request(self) -> 'None':

        gate = Event()

        first = _HookService()
        first.gate = gate

        second = _HookService()

        # Two requests arrive, each in a greenlet of its own, as they do in the server ..
        first_request = spawn(self._handle, first, _cid_1)
        second_request = spawn(self._handle, second, _cid_2)

        # .. the second completes while the first is still waiting at its gate ..
        second_response = second_request.get(timeout=_join_timeout)

        self.assertFalse(first_request.ready())
        self.assertEqual(second_response.payload, {'cid': _cid_2, 'msg_id': _msg_id_prefix + _cid_2})

        # .. and once the gate opens, the first completes with its own cid and its own message id.
        gate.set()
        first_response = first_request.get(timeout=_join_timeout)

        self.assertEqual(first_response.payload, {'cid': _cid_1, 'msg_id': _msg_id_prefix + _cid_1})

# ################################################################################################################################

    def test_each_hook_reads_its_own_message_id(self) -> 'None':

        gate = Event()

        first = _HookService()
        first.gate = gate

        second = _HookService()
        second.gate = gate

        first_request = spawn(self._handle, first, _cid_1)
        second_request = spawn(self._handle, second, _cid_2)

        # Both hooks are waiting at the gate with their message ids already read
        sleep(0)
        gate.set()

        _ = first_request.get(timeout=_join_timeout)
        _ = second_request.get(timeout=_join_timeout)

        self.assertEqual(first.record['msg_id'], _msg_id_prefix + _cid_1)
        self.assertEqual(second.record['msg_id'], _msg_id_prefix + _cid_2)

        self.assertEqual(first.record['cid'], _cid_1)
        self.assertEqual(second.record['cid'], _cid_2)

# ################################################################################################################################

    def test_a_service_without_the_hook_does_not_spawn(self) -> 'None':

        with patch(_spawn_target) as spawn_mock:
            response = self._handle(_PlainService(), _cid_1)

        spawn_mock.assert_not_called()
        self.server.service_store.new_instance.assert_not_called()

        # The caller gets the default acknowledgement and the message is in the queue
        self.assertEqual(_Publisher.requests, [_cid_1])
        self.assertIn(_queue.Ack_CID, response.payload)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
