# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A REST or SOAP channel whose queue is on - what the caller receives, what the queue stores and what the service
# runs with when the stored request is delivered.

# stdlib
from base64 import b64encode
from http.client import OK, UNAUTHORIZED
from json import loads
from unittest import main, TestCase
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs

# Zato
from zato.common.api import CHANNEL, CONTENT_TYPE, DATA_FORMAT, HTTP_SOAP, URL_TYPE
from zato.common.pubsub.outgoing import has_queue, InboundType, is_inbound, Key_Data, Key_Data_Format, Key_Headers, \
    Key_Is_Base64, Key_Method, Key_Params, Key_Path, Key_Path_Params, Key_Service, Key_Transport
from zato.common.pubsub.sql.backend import PublishResult
from zato.common.soap.addressing import AddressingInfo
from zato.common.soap.envelope import parse_body, parse_envelope
from zato.common.typing_ import cast_
from zato.server.connection.http_soap.channel_queue import build_channel_request, QueuedChannelHandler
from zato.server.connection.http_soap.channel_soap import SOAPRequestContext
from zato.server.connection.outgoing_delivery import register_delivery_handlers
from zato.server.connection.outgoing_delivery.http import deliver_to_http_channel
from zato.server.reqresp.response import Response
from zato.server.service import Invoke_Mode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict, strlist

# ################################################################################################################################
# ################################################################################################################################

_queue = HTTP_SOAP.Queue

_cid = '20260115-101500-1234-abcdef012-server1'
_pub_cid = '20260115-101500-1234-abcdef012'
_msg_id = 'zpsm-0000000000000001'

_channel_id = 17
_channel_name = 'Order Intake'
_service_name = 'orders.intake'
_service_impl_name = 'orders.intake.OrderIntake'

# The moments the handler records, in the order they happened
_event_published = 'published'
_event_hook_started = 'hook-started'

# The target of the publisher patch - the handler stores a request through this name
_publisher_target = 'zato.server.connection.http_soap.channel_queue.OutgoingPublisher'

# The JSON of a request as it arrives and as the queue stores it
_json_body = b'{"order_id": 1234, "items": ["a", "b"]}'

# A payload that is not text, so it travels through the queue as base64
_binary_body = b'\x00\x01\x02\xff\xfe\xfd'

_soap_operation = 'SubmitOrder'
_soap_response_element = _soap_operation + 'Response'

# ################################################################################################################################
# ################################################################################################################################

class _Publisher:
    """ Stands in for the channel's publisher, recording when it was called and what it stored.
    """
    events:'strlist' = []
    requests:'anylist' = []

    def __init__(self, server:'any_', conn_type:'str', conn_id:'int') -> 'None':
        self.conn_type = conn_type
        self.conn_id = conn_id

    def publish_request(self, cid:'str', attempts:'int', request:'stranydict') -> 'PublishResult':
        _Publisher.events.append(_event_published)
        _Publisher.requests.append((self.conn_type, self.conn_id, cid, request))

        out = PublishResult()
        out.msg_id = _msg_id

        return out

# ################################################################################################################################
# ################################################################################################################################

class _HookService:
    """ Stands in for a service with the get_queue_response hook - what update_handle returns is what the hook shaped.
    """
    has_get_queue_response = True

    def __init__(self, response:'Response | None'=None, error:'Exception | None'=None) -> 'None':
        self.response = response
        self.error = error
        self.kwargs:'anydict' = {}

    def update_handle(self, *args:'any_', **kwargs:'any_') -> 'Response':
        _Publisher.events.append(_event_hook_started)
        self.kwargs = kwargs

        if self.error:
            raise self.error

        return cast_('Response', self.response)

# ################################################################################################################################

class _PlainService:
    """ Stands in for a service without the hook.
    """
    has_get_queue_response = False

    def update_handle(self, *args:'any_', **kwargs:'any_') -> 'None':
        raise AssertionError('A service without the hook is never invoked by the channel')

# ################################################################################################################################
# ################################################################################################################################

def _flatten(query_string:'str') -> 'anydict':
    """ A query string as the service reads it - a repeated parameter is a list, any other a single value.
    """
    out:'anydict' = {}

    for key, values in parse_qs(query_string).items():
        if len(values) > 1:
            out[key] = values
        else:
            out[key] = values[0]

    return out

# ################################################################################################################################

def _new_channel_item(transport:'str'=URL_TYPE.PLAIN_HTTP, queue_response:'str'='') -> 'anydict':
    out = {
        'id': _channel_id,
        'name': _channel_name,
        'service_name': _service_name,
        'service_impl_name': _service_impl_name,
        'data_format': DATA_FORMAT.JSON,
        'transport': transport,
        'merge_url_params_req': True,
        'params_pri': 'channel-params-over-msg',
        _queue.Field_Use_Queue: True,
        _queue.Field_Queue_Response: queue_response,
    }
    return out

# ################################################################################################################################

def _new_request_ctx() -> 'stranydict':
    out = {
        'REQUEST_METHOD': 'POST',
        'PATH_INFO': '/orders/1234',
        'QUERY_STRING': 'status=new&tag=a&tag=b',
        'HTTP_X_REQUEST_ID': 'req-001',
        'HTTP_USER_AGENT': 'test-agent',
        'CONTENT_TYPE': 'application/json',
        'CONTENT_LENGTH': str(len(_json_body)),
    }
    return out

# ################################################################################################################################

def _new_soap_context() -> 'SOAPRequestContext':
    """ The context of a SOAP 1.1 request without WS-Addressing, which is all the acknowledgement needs.
    """
    out = SOAPRequestContext()
    out.operation = _soap_operation
    out.addressing = AddressingInfo()
    out.use_mtom = False

    return out

# ################################################################################################################################
# ################################################################################################################################

class _QueuedChannelTestCase(TestCase):
    """ What the two test cases below share - a handler with a recording publisher.
    """

    def setUp(self) -> 'None':
        _Publisher.events = []
        _Publisher.requests = []

        self.server = MagicMock()
        self.config_manager = MagicMock()

        self.handler = QueuedChannelHandler(self.server, self._set_response, _flatten)

        self.publisher_patch = patch(_publisher_target, _Publisher)
        _ = self.publisher_patch.start()
        self.addCleanup(self.publisher_patch.stop)

# ################################################################################################################################

    def _set_response(self, service:'any_', **kwargs:'any_') -> 'Response':
        out = service.response
        return out

# ################################################################################################################################

    def _handle(self, service:'any_', channel_item:'anydict', request_ctx:'stranydict | None'=None) -> 'Response':
        """ Runs the handler the way the request handler does - with the service's class, the instance is what
        the service store would hand out if the handler asked for one.
        """
        if request_ctx is None:
            request_ctx = _new_request_ctx()

        self.server.service_store.new_instance.return_value = (service, True)

        out = self.handler.handle(_cid, type(service), {}, _json_body, {'order_id': '1234'}, channel_item, request_ctx,
            self.config_manager, {}, {})

        return out

# ################################################################################################################################
# ################################################################################################################################

class ResponsePrecedenceTestCase(_QueuedChannelTestCase):
    """ Which response the caller receives - the hook's, the channel's static one or the default acknowledgement.
    """

    def test_the_hook_response_wins(self) -> 'None':

        hook_response = Response()
        hook_response.status_code = OK
        hook_response.payload = '{"ticket": "T-1"}'

        service = _HookService(hook_response)
        channel_item = _new_channel_item(queue_response='{"static": true}')

        response = self._handle(service, channel_item)

        self.assertIs(response, hook_response)
        self.assertEqual(_Publisher.events, [_event_published, _event_hook_started])

# ################################################################################################################################

    def test_the_hook_runs_in_the_queue_response_mode_with_the_message_id(self) -> 'None':

        service = _HookService(Response())
        _ = self._handle(service, _new_channel_item())

        self.assertEqual(service.kwargs['invoke_mode'], Invoke_Mode.Queue_Response_Only)
        self.assertEqual(service.kwargs['queue_msg_id'], _msg_id)

        # The instance the hook ran on is the one the service store built for the channel's service
        self.server.service_store.new_instance.assert_called_once_with(_service_impl_name)

# ################################################################################################################################

    def test_a_service_without_the_hook_is_not_instantiated_by_the_channel(self) -> 'None':
        """ The shortcut - the channel side costs a service without the hook nothing, not even an instance.
        """
        _ = self._handle(_PlainService(), _new_channel_item())

        self.server.service_store.new_instance.assert_not_called()

# ################################################################################################################################

    def test_the_hook_may_refuse_the_request_the_queue_already_holds(self) -> 'None':
        """ A 401 from the hook goes to the caller as any other response, the message stays queued all the same.
        """
        hook_response = Response()
        hook_response.status_code = UNAUTHORIZED
        hook_response.payload = ''

        response = self._handle(_HookService(hook_response), _new_channel_item())

        self.assertEqual(response.status_code, UNAUTHORIZED)
        self.assertEqual(len(_Publisher.requests), 1)

# ################################################################################################################################

    def test_a_hook_that_raises_surfaces_after_the_publication(self) -> 'None':

        service = _HookService(error=ValueError('The hook could not build a response'))

        with self.assertRaises(ValueError):
            _ = self._handle(service, _new_channel_item())

        self.assertEqual(_Publisher.events, [_event_published, _event_hook_started])

# ################################################################################################################################

    def test_a_static_json_response(self) -> 'None':

        channel_item = _new_channel_item(queue_response='{"accepted": true}')
        response = self._handle(_PlainService(), channel_item)

        self.assertEqual(response.status_code, OK)
        self.assertEqual(response.payload, '{"accepted": true}')
        self.assertEqual(response.content_type, CONTENT_TYPE['JSON'])

# ################################################################################################################################

    def test_a_static_xml_response(self) -> 'None':

        channel_item = _new_channel_item(queue_response='<ack>ok</ack>')
        response = self._handle(_PlainService(), channel_item)

        self.assertEqual(response.payload, '<ack>ok</ack>')
        self.assertEqual(response.content_type, CONTENT_TYPE['PLAIN_XML'])

# ################################################################################################################################

    def test_a_static_text_response(self) -> 'None':

        channel_item = _new_channel_item(queue_response='ACCEPTED\nthank you')
        response = self._handle(_PlainService(), channel_item)

        self.assertEqual(response.payload, 'ACCEPTED\nthank you')
        self.assertEqual(response.content_type, 'text/plain')

# ################################################################################################################################

    def test_a_static_response_on_a_soap_channel_is_xml(self) -> 'None':

        channel_item = _new_channel_item(URL_TYPE.SOAP, queue_response='<ack>ok</ack>')
        request_ctx = _new_request_ctx()
        request_ctx['zato.request.soap'] = _new_soap_context()

        response = self._handle(_PlainService(), channel_item, request_ctx)

        self.assertEqual(response.payload, '<ack>ok</ack>')
        self.assertEqual(response.content_type, 'text/xml')

# ################################################################################################################################

    def test_the_default_ack_on_a_rest_channel(self) -> 'None':

        response = self._handle(_PlainService(), _new_channel_item())

        self.assertEqual(response.status_code, OK)
        self.assertEqual(response.content_type, CONTENT_TYPE['JSON'])
        self.assertEqual(loads(response.payload), {_queue.Ack_Is_OK: True, _queue.Ack_CID: _pub_cid})

# ################################################################################################################################

    def test_the_default_ack_on_a_soap_channel(self) -> 'None':

        channel_item = _new_channel_item(URL_TYPE.SOAP)
        request_ctx = _new_request_ctx()
        request_ctx['zato.request.soap'] = _new_soap_context()

        response = self._handle(_PlainService(), channel_item, request_ctx)

        self.assertEqual(response.status_code, OK)
        self.assertTrue(response.content_type.startswith('text/xml'))

        # The acknowledgement is the operation's response element in an envelope of the request's version
        envelope = parse_envelope(response.payload)
        body = parse_body(envelope)
        operation_response = getattr(body, _soap_response_element)

        self.assertEqual(getattr(operation_response, _queue.Ack_CID), _pub_cid)
        self.assertEqual(str(getattr(operation_response, _queue.Ack_Is_OK)).lower(), 'true')

# ################################################################################################################################

    def test_the_message_is_published_to_the_channel_queue(self) -> 'None':

        _ = self._handle(_PlainService(), _new_channel_item())

        conn_type, conn_id, cid, request = _Publisher.requests[0]

        self.assertEqual(conn_type, InboundType.REST)
        self.assertEqual(conn_id, _channel_id)
        self.assertEqual(cid, _cid)
        self.assertEqual(request[Key_Service], _service_name)

# ################################################################################################################################

    def test_a_soap_channel_publishes_to_its_own_queue_type(self) -> 'None':

        channel_item = _new_channel_item(URL_TYPE.SOAP)
        request_ctx = _new_request_ctx()
        request_ctx['zato.request.soap'] = _new_soap_context()

        _ = self._handle(_PlainService(), channel_item, request_ctx)

        conn_type, _, _, request = _Publisher.requests[0]

        self.assertEqual(conn_type, InboundType.SOAP)
        self.assertEqual(request[Key_Transport], URL_TYPE.SOAP)

# ################################################################################################################################
# ################################################################################################################################

class EnvelopeRoundTripTestCase(TestCase):
    """ A request stored by the channel is delivered to the service as the request it was.
    """

    def setUp(self) -> 'None':
        register_delivery_handlers()

        self.server = MagicMock()
        self.channel_item = _new_channel_item()

        # The channel's parameters are built by the request handler, which is not under test here
        self.channel_item['merge_url_params_req'] = False

# ################################################################################################################################

    def _round_trip(self, body:'bytes') -> 'anydict':
        """ Builds the request the queue stores and delivers it, returning what server.invoke was called with.
        """
        request_ctx = _new_request_ctx()
        request_ctx['CONTENT_LENGTH'] = str(len(body))

        query_params = _flatten(request_ctx['QUERY_STRING'])
        request = build_channel_request(self.channel_item, request_ctx, body, query_params, {'order_id': '1234'})

        deliver_to_http_channel(self.server, _cid, self.channel_item, request)

        self.server.invoke.assert_called_once()
        out = {
            'request': request,
            'args': self.server.invoke.call_args.args,
            'kwargs': self.server.invoke.call_args.kwargs,
        }
        return out

# ################################################################################################################################

    def test_a_text_payload_is_stored_as_text(self) -> 'None':

        request_ctx = _new_request_ctx()
        request = build_channel_request(self.channel_item, request_ctx, _json_body, {}, {})

        self.assertEqual(request[Key_Data], _json_body.decode('utf8'))
        self.assertFalse(request[Key_Is_Base64])

# ################################################################################################################################

    def test_a_binary_payload_is_stored_as_base64(self) -> 'None':

        request_ctx = _new_request_ctx()
        request = build_channel_request(self.channel_item, request_ctx, _binary_body, {}, {})

        self.assertEqual(request[Key_Data], b64encode(_binary_body).decode('ascii'))
        self.assertTrue(request[Key_Is_Base64])

# ################################################################################################################################

    def test_the_request_describes_the_call(self) -> 'None':

        request_ctx = _new_request_ctx()
        query_params = _flatten(request_ctx['QUERY_STRING'])
        request = build_channel_request(self.channel_item, request_ctx, _json_body, query_params, {'order_id': '1234'})

        self.assertEqual(request[Key_Service], _service_name)
        self.assertEqual(request[Key_Method], 'POST')
        self.assertEqual(request[Key_Path], '/orders/1234')
        self.assertEqual(request[Key_Path_Params], {'order_id': '1234'})
        self.assertEqual(request[Key_Params], {'status': 'new', 'tag': ['a', 'b']})
        self.assertEqual(request[Key_Data_Format], DATA_FORMAT.JSON)
        self.assertEqual(request[Key_Transport], URL_TYPE.PLAIN_HTTP)

# ################################################################################################################################

    def test_the_headers_are_stored_as_the_service_reads_them(self) -> 'None':

        request_ctx = _new_request_ctx()
        request = build_channel_request(self.channel_item, request_ctx, _json_body, {}, {})

        headers = request[Key_Headers]

        self.assertEqual(headers['x-request-id'], 'req-001')
        self.assertEqual(headers['user-agent'], 'test-agent')
        self.assertEqual(headers['content-type'], 'application/json')
        self.assertEqual(headers['content-length'], str(len(_json_body)))

# ################################################################################################################################

    def test_the_service_is_invoked_with_the_request_as_it_was(self) -> 'None':

        result = self._round_trip(_json_body)
        args = result['args']
        kwargs = result['kwargs']

        self.assertEqual(args[0], _service_name)
        self.assertEqual(args[1], _json_body)

        self.assertEqual(kwargs['channel'], CHANNEL.HTTP_SOAP)
        self.assertEqual(kwargs['data_format'], DATA_FORMAT.JSON)
        self.assertEqual(kwargs['transport'], URL_TYPE.PLAIN_HTTP)
        self.assertEqual(kwargs['cid'], _cid)
        self.assertEqual(kwargs['url_match'], {'order_id': '1234'})
        self.assertIs(kwargs['channel_item'], self.channel_item)

# ################################################################################################################################

    def test_the_request_context_is_rebuilt(self) -> 'None':

        result = self._round_trip(_json_body)
        request_ctx = result['kwargs']['request_ctx']

        self.assertEqual(request_ctx['REQUEST_METHOD'], 'POST')
        self.assertEqual(request_ctx['PATH_INFO'], '/orders/1234')
        self.assertEqual(request_ctx['zato.http.GET'], {'status': 'new', 'tag': ['a', 'b']})
        self.assertEqual(request_ctx['zato.http.path_params'], {'order_id': '1234'})
        self.assertIs(request_ctx['zato.channel_item'], self.channel_item)

        # The query string is the one the parameters came from, with the repeated parameter repeated
        self.assertEqual(_flatten(request_ctx['QUERY_STRING']), {'status': 'new', 'tag': ['a', 'b']})

# ################################################################################################################################

    def test_the_headers_come_back_under_their_wsgi_keys(self) -> 'None':

        result = self._round_trip(_json_body)
        request_ctx = result['kwargs']['request_ctx']

        self.assertEqual(request_ctx['HTTP_X_REQUEST_ID'], 'req-001')
        self.assertEqual(request_ctx['HTTP_USER_AGENT'], 'test-agent')
        self.assertEqual(request_ctx['CONTENT_TYPE'], 'application/json')
        self.assertEqual(request_ctx['CONTENT_LENGTH'], str(len(_json_body)))

        # What the service reads as self.request.headers is the stored form
        self.assertEqual(request_ctx['zato.request.headers'], result['request'][Key_Headers])

# ################################################################################################################################

    def test_a_binary_payload_comes_back_as_the_bytes_it_was(self) -> 'None':

        result = self._round_trip(_binary_body)

        self.assertEqual(result['args'][1], _binary_body)

# ################################################################################################################################
# ################################################################################################################################

class RegistryTestCase(TestCase):
    """ The two channel types next to the Kafka one - all three are channels, only the two have a queue of their own.
    """

    def setUp(self) -> 'None':
        register_delivery_handlers()

# ################################################################################################################################

    def test_the_channel_types_have_a_queue(self) -> 'None':
        self.assertTrue(has_queue(InboundType.REST))
        self.assertTrue(has_queue(InboundType.SOAP))

# ################################################################################################################################

    def test_the_kafka_channel_has_no_queue(self) -> 'None':
        self.assertFalse(has_queue(InboundType.KAFKA))

# ################################################################################################################################

    def test_all_three_are_inbound(self) -> 'None':
        self.assertTrue(is_inbound(InboundType.REST))
        self.assertTrue(is_inbound(InboundType.SOAP))
        self.assertTrue(is_inbound(InboundType.KAFKA))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
