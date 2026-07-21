# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from unittest.mock import MagicMock

# Zato
from zato.common.api import CHANNEL
from zato.server.service import Service
from zato.server.service.reqresp import Request

# ################################################################################################################################
# ################################################################################################################################

_test_cid = 'test-cid-0001'

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
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
