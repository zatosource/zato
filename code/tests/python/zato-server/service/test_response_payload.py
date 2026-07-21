# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from unittest.mock import MagicMock

# Bunch
from zato.common.ext.bunch import Bunch

# Zato
from zato.common.json_internal import loads
from zato.common.util.json_ import BasicParser
from zato.common.util.message import Message
from zato.server.connection.http_soap.channel import RequestHandler
from zato.server.reqresp.payload import IOPayload
from zato.server.reqresp.response import Response
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_test_cid = 'test-cid-0001'

# ################################################################################################################################
# ################################################################################################################################

class TestResponseFreeFormPayload(unittest.TestCase):
    """ Without any output declaration, self.response.payload is a free-form message
    that builds nested trees through plain dot access.
    """

    def _make_response(self) -> 'Response':
        out = Response()
        out.init(_test_cid, None, 'json')
        return out

# ################################################################################################################################

    def test_payload_is_a_message_without_io(self) -> 'None':
        response = self._make_response()

        self.assertIsInstance(response.payload, Message)

# ################################################################################################################################

    def test_nested_vivification_builds_the_expected_dict(self) -> 'None':
        response = self._make_response()
        response.payload.abc.hello.world = 123

        self.assertEqual(response.payload.getvalue(), {'abc': {'hello': {'world': 123}}})

# ################################################################################################################################

    def test_assignment_order_is_preserved(self) -> 'None':
        response = self._make_response()
        response.payload.customer = 'C-1001'
        response.payload.status = 'confirmed'
        response.payload.details.city = 'Amsterdam'

        expected = {'customer': 'C-1001', 'status': 'confirmed', 'details': {'city': 'Amsterdam'}}
        self.assertEqual(response.payload.getvalue(), expected)

# ################################################################################################################################

    def test_empty_payload_has_no_content(self) -> 'None':
        response = self._make_response()

        self.assertFalse(response.payload)
        self.assertEqual(len(response), 0)

# ################################################################################################################################

    def test_string_assignment_replaces_the_message(self) -> 'None':
        response = self._make_response()
        response.payload = 'MSH|^~\\&|IIS|STATE|MYAPP|MYFAC|20260115||ACK^V04^ACK|CTRL-0001|P|2.5.1'

        self.assertEqual(response.payload, 'MSH|^~\\&|IIS|STATE|MYAPP|MYFAC|20260115||ACK^V04^ACK|CTRL-0001|P|2.5.1')

# ################################################################################################################################

    def test_dict_assignment_replaces_the_message(self) -> 'None':
        response = self._make_response()
        response.payload = {'customer': 'C-1001'}

        self.assertEqual(response.payload, {'customer': 'C-1001'})

# ################################################################################################################################

    def test_list_assignment_replaces_the_message(self) -> 'None':
        response = self._make_response()
        response.payload = [{'customer': 'C-1001'}, {'customer': 'C-1002'}]

        self.assertEqual(response.payload, [{'customer': 'C-1001'}, {'customer': 'C-1002'}])

# ################################################################################################################################

    def test_message_assignment_is_stored_as_is(self) -> 'None':
        response = self._make_response()

        message = Message()
        message.status = 'Accepted'
        response.payload = message

        self.assertIs(response.payload, message)

# ################################################################################################################################

    def test_generator_payload_is_stored_directly(self) -> 'None':
        response = self._make_response()

        def stream_events() -> 'any_':
            yield 'event: update\n'

        events = stream_events()
        response.payload = events

        self.assertIs(response.payload, events)

# ################################################################################################################################

    def test_declared_output_still_uses_io_payload(self) -> 'None':
        io_processor = MagicMock()
        io_processor.is_dataclass = False
        io_processor.has_output_declared = True
        io_processor.all_output_elem_names = ['customer_id', 'status']

        response = Response()
        response.init(_test_cid, io_processor, 'json')

        self.assertIsInstance(response.payload, IOPayload)

# ################################################################################################################################

    def test_io_without_output_gives_a_free_form_message(self) -> 'None':
        io_processor = MagicMock()
        io_processor.is_dataclass = False
        io_processor.has_output_declared = False

        response = Response()
        response.init(_test_cid, io_processor, 'json')

        self.assertIsInstance(response.payload, Message)

# ################################################################################################################################

    def test_dataclass_io_without_output_gives_a_free_form_message(self) -> 'None':
        io_processor = MagicMock()
        io_processor.is_dataclass = True
        io_processor.has_output_declared = False

        response = Response()
        response.init(_test_cid, io_processor, 'json')

        self.assertIsInstance(response.payload, Message)

# ################################################################################################################################

    def test_dataclass_io_with_output_keeps_an_empty_payload(self) -> 'None':
        io_processor = MagicMock()
        io_processor.is_dataclass = True
        io_processor.has_output_declared = True

        response = Response()
        response.init(_test_cid, io_processor, 'json')

        self.assertEqual(response.payload, '')

# ################################################################################################################################
# ################################################################################################################################

class TestSetResponseData(unittest.TestCase):
    """ The generic serialization funnel that all non-HTTP channels go through.
    """

    def _make_service(self) -> 'Service':
        out = Service.__new__(Service)
        out.response = Response()
        out.response.init(_test_cid, None, 'json')
        return out

# ################################################################################################################################

    def test_free_form_message_serializes_to_a_dict(self) -> 'None':
        service = self._make_service()
        service.response.payload.abc.hello.world = 123

        result = service.set_response_data(service, data_format='json', transport='')

        self.assertEqual(result, {'abc': {'hello': {'world': 123}}})
        self.assertEqual(service.response.payload, {'abc': {'hello': {'world': 123}}})

# ################################################################################################################################

    def test_empty_message_serializes_to_an_empty_string(self) -> 'None':
        service = self._make_service()

        result = service.set_response_data(service, data_format='json', transport='')

        self.assertEqual(result, '')
        self.assertEqual(service.response.payload, '')

# ################################################################################################################################

    def test_as_bunch_returns_a_bunch(self) -> 'None':
        service = self._make_service()
        service.response.payload.abc.hello.world = 123

        result = service.set_response_data(service, data_format='json', transport='', as_bunch=True)

        self.assertIsInstance(result, Bunch)
        self.assertEqual(result.abc.hello.world, 123)

# ################################################################################################################################
# ################################################################################################################################

class TestRESTChannelFreeFormPayload(unittest.TestCase):
    """ The same behavior end to end - a service with zero declarations invoked
    through RequestHandler.handle, the way REST channels do it.
    """

    def _invoke_rest_channel(self, service_class:'type', raw_request:'str') -> 'any_':
        server = MagicMock()
        server.json_parser = BasicParser()

        service = service_class()
        server.service_store.new_instance.return_value = (service, True)

        handler = RequestHandler(server)

        channel_item = Bunch({
            'id': 1,
            'name': 'test.rest.channel',
            'service_impl_name': 'test.module.TestService',
            'data_format': 'json',
            'transport': 'plain_http',
            'merge_url_params_req': True,
            'params_pri': 'channel-params-over-msg',
        })

        wsgi_environ = {
            'zato.http.response.headers': {},
        }

        out = handler.handle(_test_cid, {}, channel_item, wsgi_environ, raw_request,
            MagicMock(), None, '/test/path', {}, {})

        return out

# ################################################################################################################################

    def _make_service_class(self) -> 'type':

        class NestedPayloadService(Service):
            _Service__service_name = 'test.nested-payload'
            _Service__service_impl_name = 'test.module.NestedPayloadService'

            _config_manager = MagicMock()
            _config_store = MagicMock()
            amqp = MagicMock()

            has_io = False
            component_enabled_email = False
            component_enabled_odoo = False

            def handle(self) -> 'None':
                self.response.payload.abc.hello.world = 123

        return NestedPayloadService

# ################################################################################################################################

    def _make_empty_service_class(self) -> 'type':

        class NoResponseService(Service):
            _Service__service_name = 'test.no-response'
            _Service__service_impl_name = 'test.module.NoResponseService'

            _config_manager = MagicMock()
            _config_store = MagicMock()
            amqp = MagicMock()

            has_io = False
            component_enabled_email = False
            component_enabled_odoo = False

            def handle(self) -> 'None':
                pass

        return NoResponseService

# ################################################################################################################################

    def test_nested_payload_reaches_the_wire_as_json(self) -> 'None':
        service_class = self._make_service_class()

        response = self._invoke_rest_channel(service_class, '{"customer":"C-1001"}')

        self.assertEqual(loads(response.payload), {'abc': {'hello': {'world': 123}}})

# ################################################################################################################################

    def test_no_assignment_gives_an_empty_response(self) -> 'None':
        service_class = self._make_empty_service_class()

        response = self._invoke_rest_channel(service_class, '')

        self.assertEqual(response.payload, '')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
