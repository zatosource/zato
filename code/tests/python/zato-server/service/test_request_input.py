# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from dataclasses import dataclass
from decimal import Decimal as stdlib_Decimal
from unittest.mock import MagicMock

# Zato
from zato.common.api import CHANNEL, DATA_FORMAT
from zato.common.marshal_.api import Model
from zato.common.soap.message import parse as parse_soap
from zato.common.util.api import payload_from_request
from zato.common.util.json_ import BasicParser
from zato.hl7v2 import parse_hl7
from zato.input_output import Decimal, Dict, Float, Int, IOProcessor, List, ServiceInput
from zato.server.service import Service
from zato.server.service.reqresp import Request

# ################################################################################################################################
# ################################################################################################################################

_test_cid = 'test-cid-0001'

# An admission an MLLP channel receives, as the channel parses it when it parses on input
_adt_a01_message = (
    'MSH|^~\\&|ADMIT_SYS|NORTH_WING|LAB_SYS|CENTRAL_LAB|20260315083000||ADT^A01^ADT_A01|CTL00001|P|2.6\r'
    'EVN|A01|20260315083000\r'
    'PID|||PT7890^^^NORTH_WING||Castellano^Marisol||19830214|F\r'
)

# The operation element of a SOAP body, as a SOAP channel hands it to a service
_soap_order = (
    b'<SubmitOrder xmlns="urn:orders">'
    b'<customer>C-1001</customer>'
    b'<quantity>3</quantity>'
    b'<weight>2.5</weight>'
    b'<unit_price>19.99</unit_price>'
    b'<tags>express</tags><tags>fragile</tags>'
    b'<address><city>Springfield</city><postal_code>62701</postal_code></address>'
    b'</SubmitOrder>'
)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class OrderEvent(Model):
    order_id: str = ''
    status: str = ''
    amount: float = 0.0

# ################################################################################################################################
# ################################################################################################################################

class TestRequestInputNoDeclaration(unittest.TestCase):
    """ Without an I/O declaration, self.request.input carries the parsed payload -
    a dict for JSON, the raw value for text and bytes, channel params otherwise.
    """

    def _make_request(self, payload:'object', channel_params:'dict | None'=None, merge_channel_params:'bool'=True) -> 'Request':
        service = MagicMock()

        out = Request(service)
        out.payload = payload
        out.merge_channel_params = merge_channel_params

        if channel_params:
            out.channel_params.update(channel_params)

        out.init(False, _test_cid, None, 'json', 'plain_http', {}, MagicMock())
        return out

# ################################################################################################################################

    def test_dict_payload_becomes_input(self) -> 'None':
        request = self._make_request({'customer': 'C-1001', 'quantity': 3})

        self.assertEqual(request.input['customer'], 'C-1001')
        self.assertEqual(request.input['quantity'], 3)

# ################################################################################################################################

    def test_dict_payload_allows_attribute_access(self) -> 'None':
        request = self._make_request({'customer': 'C-1001'})

        self.assertEqual(request.input.customer, 'C-1001')

# ################################################################################################################################

    def test_channel_params_merge_without_overriding_payload(self) -> 'None':
        payload = {'customer': 'C-1001'}
        channel_params = {'customer': 'from-channel', 'region': 'north'}

        request = self._make_request(payload, channel_params)

        self.assertEqual(request.input['customer'], 'C-1001')
        self.assertEqual(request.input['region'], 'north')

# ################################################################################################################################

    def test_channel_params_are_not_merged_when_disabled(self) -> 'None':
        payload = {'customer': 'C-1001'}
        channel_params = {'region': 'north'}

        request = self._make_request(payload, channel_params, merge_channel_params=False)

        self.assertEqual(request.input['customer'], 'C-1001')
        self.assertNotIn('region', request.input)

# ################################################################################################################################

    def test_list_payload_becomes_input(self) -> 'None':
        payload = [{'customer': 'C-1001'}, {'customer': 'C-1002'}]

        request = self._make_request(payload)

        self.assertIs(request.input, payload)

# ################################################################################################################################

    def test_text_payload_becomes_input(self) -> 'None':
        payload = 'UNB+UNOC:3+SENDER+RECIPIENT+260721:0130+REF-0001'

        request = self._make_request(payload)

        self.assertEqual(request.input, payload)

# ################################################################################################################################

    def test_bytes_payload_becomes_input(self) -> 'None':
        payload = b'MSH|^~\\&|SENDING_APP|SENDING_FACILITY'

        request = self._make_request(payload)

        self.assertEqual(request.input, payload)

# ################################################################################################################################

    def test_empty_payload_leaves_channel_params_only(self) -> 'None':
        request = self._make_request('', {'region': 'north'})

        self.assertEqual(request.input['region'], 'north')

# ################################################################################################################################

    def test_empty_payload_without_channel_params_gives_empty_input(self) -> 'None':
        request = self._make_request('')

        self.assertNotIn('region', request.input)

# ################################################################################################################################

    def test_model_payload_becomes_input(self) -> 'None':
        event = OrderEvent()
        event.order_id = 'ORD-001'
        event.status = 'completed'
        event.amount = 99.95

        request = self._make_request(event)

        self.assertIs(request.input, event)
        self.assertEqual(request.input.order_id, 'ORD-001')

# ################################################################################################################################

    def test_hl7_message_payload_becomes_input(self) -> 'None':
        message = parse_hl7(_adt_a01_message, validate=False)

        request = self._make_request(message)

        self.assertIs(request.input, message)
        self.assertEqual(request.input.get('MSH.10'), 'CTL00001')

# ################################################################################################################################

    def test_service_input_payload_becomes_input(self) -> 'None':
        forwarded = ServiceInput({'customer': 'C-1001', 'quantity': 3})

        request = self._make_request(forwarded)

        self.assertEqual(request.input['customer'], 'C-1001')
        self.assertEqual(request.input.quantity, 3)
        self.assertEqual(request.payload, {'customer': 'C-1001', 'quantity': 3})

# ################################################################################################################################

    def test_service_input_payload_keeps_channel_params(self) -> 'None':
        forwarded = ServiceInput({'customer': 'C-1001'})

        request = self._make_request(forwarded, {'customer': 'from-channel', 'region': 'north'})

        self.assertEqual(request.input['customer'], 'C-1001')
        self.assertEqual(request.input['region'], 'north')

# ################################################################################################################################

    def test_soap_body_becomes_input(self) -> 'None':
        message = parse_soap(_soap_order)

        request = self._make_request(message)

        self.assertEqual(request.input['customer'], 'C-1001')
        self.assertEqual(request.input['address'], {'city': 'Springfield', 'postal_code': '62701'})
        self.assertEqual(request.input['tags'], ['express', 'fragile'])

        # The payload keeps the message, which a service reads with dot access
        self.assertIs(request.payload, message)
        self.assertEqual(request.payload.address.city, 'Springfield')

# ################################################################################################################################
# ################################################################################################################################

class TestRequestInputDeclared(unittest.TestCase):
    """ With an I/O declaration, self.request.input carries each declared element converted to its type,
    whether the channel delivered a number or its text.
    """

    def _make_request(self, payload:'object', transport:'str'='plain_http') -> 'Request':

        class OrderInput:
            input = 'customer', Int('quantity'), Float('weight'), Decimal('unit_price'), List('tags'), Dict('address'), \
                '-notes'

        _ = IOProcessor.attach_io(MagicMock(), OrderInput)
        io_processor = OrderInput._io # type: ignore

        service = MagicMock()

        out = Request(service)
        out.payload = payload

        out.init(True, _test_cid, io_processor, 'json', transport, {}, MagicMock())
        return out

# ################################################################################################################################

    def _assert_order_input(self, request:'Request') -> 'None':

        self.assertEqual(request.input.customer, 'C-1001')
        self.assertEqual(request.input.quantity, 3)
        self.assertEqual(request.input.weight, 2.5)
        self.assertEqual(request.input.unit_price, stdlib_Decimal('19.99'))
        self.assertEqual(request.input.tags, ['express', 'fragile'])
        self.assertEqual(request.input.address, {'city': 'Springfield', 'postal_code': '62701'})
        self.assertIsNone(request.input.notes)

        self.assertIs(type(request.input.quantity), int)
        self.assertIs(type(request.input.weight), float)
        self.assertIs(type(request.input.unit_price), stdlib_Decimal)

# ################################################################################################################################

    def test_numbers_are_converted(self) -> 'None':
        payload = {
            'customer': 'C-1001',
            'quantity': 3,
            'weight': 2.5,
            'unit_price': 19.99,
            'tags': ['express', 'fragile'],
            'address': {'city': 'Springfield', 'postal_code': '62701'},
        }

        request = self._make_request(payload)

        self._assert_order_input(request)

# ################################################################################################################################

    def test_text_is_converted(self) -> 'None':
        payload = {
            'customer': 'C-1001',
            'quantity': '3',
            'weight': '2.5',
            'unit_price': '19.99',
            'tags': ['express', 'fragile'],
            'address': {'city': 'Springfield', 'postal_code': '62701'},
        }

        request = self._make_request(payload)

        self._assert_order_input(request)

# ################################################################################################################################

    def test_soap_body_is_converted(self) -> 'None':
        message = parse_soap(_soap_order)

        request = self._make_request(message, 'soap')

        self._assert_order_input(request)

# ################################################################################################################################
# ################################################################################################################################

class TestPayloadFromRequest(unittest.TestCase):
    """ What the parsing step hands over for the JSON data format, before the request object reads it.
    """

    def _parse(self, request:'object') -> 'object':
        out = payload_from_request(BasicParser(), _test_cid, request, DATA_FORMAT.JSON, 'plain_http')
        return out

# ################################################################################################################################

    def test_json_text_is_parsed(self) -> 'None':
        payload = self._parse('{"customer":"C-1001", "quantity":3}')

        self.assertEqual(payload, {'customer': 'C-1001', 'quantity': 3})

# ################################################################################################################################

    def test_json_bytes_are_parsed(self) -> 'None':
        payload = self._parse(b'[{"customer":"C-1001"}, {"customer":"C-1002"}]')

        self.assertEqual(payload, [{'customer': 'C-1001'}, {'customer': 'C-1002'}])

# ################################################################################################################################

    def test_text_that_is_not_json_stays_text(self) -> 'None':
        request = 'UNB+UNOC:3+SENDER+RECIPIENT+260721:0130+REF-0001'

        payload = self._parse(request)

        self.assertIs(payload, request)

# ################################################################################################################################

    def test_bytes_that_are_not_json_stay_bytes(self) -> 'None':
        request = b'MSH|^~\\&|SENDING_APP|SENDING_FACILITY'

        payload = self._parse(request)

        self.assertIs(payload, request)

# ################################################################################################################################
# ################################################################################################################################

class TestServiceUpdateInput(unittest.TestCase):
    """ The same behavior end to end - Service.update initializes the request
    for a service that declares no input or output at all.
    """

    def _make_service(self) -> 'Service':

        class EchoDetails(Service):
            _Service__service_name = 'test.echo-details'
            _Service__service_impl_name = 'test.module.EchoDetails'

            _config_manager = MagicMock()
            _config_store = MagicMock()
            amqp = MagicMock()

            has_io = False
            component_enabled_email = False
            component_enabled_odoo = False

            def handle(self) -> 'None':
                pass

        out = EchoDetails()
        return out

# ################################################################################################################################

    def test_update_populates_input_from_dict_payload(self) -> 'None':
        service = self._make_service()
        server = MagicMock()

        payload = {'customer': 'C-1001', 'quantity': 3}
        raw_request = '{"customer":"C-1001", "quantity":3}'

        service.update(service, CHANNEL.INVOKE, server, None, None, _test_cid, payload, raw_request, data_format='json')

        self.assertEqual(service.request.input['customer'], 'C-1001')
        self.assertEqual(service.request.input['quantity'], 3)
        self.assertEqual(service.request.raw, raw_request)

# ################################################################################################################################

    def test_update_exposes_raw_text_as_input(self) -> 'None':
        service = self._make_service()
        server = MagicMock()

        payload = 'UNB+UNOC:3+SENDER+RECIPIENT+260721:0130+REF-0001'

        service.update(service, CHANNEL.INVOKE, server, None, None, _test_cid, payload, payload)

        self.assertEqual(service.request.input, payload)
        self.assertEqual(service.request.raw, payload)

# ################################################################################################################################

    def test_update_reads_forwarded_service_input(self) -> 'None':
        """ A service that invokes another one with its own self.request.input hands over a ServiceInput,
        and the invoked service reads the same fields from its own input.
        """
        service = self._make_service()
        server = MagicMock()

        forwarded = ServiceInput({'customer': 'C-1001', 'quantity': 3})

        service.update(service, CHANNEL.INVOKE, server, None, None, _test_cid, forwarded, forwarded)

        self.assertEqual(service.request.input['customer'], 'C-1001')
        self.assertEqual(service.request.input['quantity'], 3)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
