# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Africa's Talking provider class against the requests, responses and callbacks the provider documents.

# stdlib
from unittest import main, TestCase
from urllib.parse import urlencode

# Zato
from zato.common.sms.model import Kind_Message, Kind_Status, Status_Delivered, Status_Failed
from zato.server.connection.sms.africas_talking import AfricasTalkingProvider
from zato.server.connection.sms.base import Method_GET, Method_POST, ProviderError

# Test support
from test.zato.connection.sms.common import Body, Callback_URL, ctx, Host, new_provider, Password, Response, Sender, To, \
    Username, Webhook_URL

# ################################################################################################################################
# ################################################################################################################################

class AfricasTalkingTestCase(TestCase):

    def setUp(self) -> 'None':
        self.provider = new_provider(AfricasTalkingProvider)

# ################################################################################################################################

    def test_send_request(self) -> 'None':

        method, url, headers, data = self.provider.build_send_request(To, Body, Sender, Callback_URL)

        self.assertEqual(method, Method_POST)
        self.assertEqual(url, Host + '/version1/messaging')
        self.assertEqual(headers['apiKey'], Password)
        self.assertEqual(headers['Accept'], 'application/json')

        self.assertEqual(data, {
            'username': Username,
            'to': To,
            'message': Body,
            'from': Sender,
        })

# ################################################################################################################################

    def test_send_request_without_a_sender(self) -> 'None':

        _, _, _, data = self.provider.build_send_request(To, Body, '', None)
        self.assertNotIn('from', data)

# ################################################################################################################################

    def test_send_response(self) -> 'None':

        payload = {
            'SMSMessageData': {
                'Message': 'Sent to 1/1 Total Cost: KES 0.8000',
                'Recipients': [{
                    'statusCode': 101,
                    'number': To,
                    'status': 'Success',
                    'cost': 'KES 0.8000',
                    'messageId': 'ATXid_0123456789abcdef0123456789abcdef',
                }],
            },
        }

        result = self.provider.read_send_response(Response(201, payload))

        self.assertEqual(result.id, 'ATXid_0123456789abcdef0123456789abcdef')
        self.assertEqual(result.status, Status_Delivered)
        self.assertEqual(result.raw, payload)

# ################################################################################################################################

    def test_send_rejected_recipient(self) -> 'None':

        payload = {
            'SMSMessageData': {
                'Message': 'Sent to 0/1 Total Cost: KES 0.0000',
                'Recipients': [{
                    'statusCode': 403,
                    'number': To,
                    'status': 'InvalidPhoneNumber',
                    'cost': 'KES 0.0000',
                    'messageId': 'None',
                }],
            },
        }

        with self.assertRaises(ProviderError) as ctx:
            self.provider.read_send_response(Response(201, payload))

        self.assertIn('403', str(ctx.exception))
        self.assertIn('InvalidPhoneNumber', str(ctx.exception))

# ################################################################################################################################

    def test_send_no_recipients(self) -> 'None':

        payload = {'SMSMessageData': {'Message': 'InvalidSenderId', 'Recipients': []}}

        with self.assertRaises(ProviderError) as ctx:
            self.provider.read_send_response(Response(201, payload))

        self.assertIn('InvalidSenderId', str(ctx.exception))

# ################################################################################################################################

    def test_send_error(self) -> 'None':

        with self.assertRaises(ProviderError) as ctx:
            self.provider.read_send_response(Response(401, 'The supplied authentication is invalid'))

        self.assertIn('401', str(ctx.exception))

# ################################################################################################################################

    def test_ping_request(self) -> 'None':

        method, url, headers, params = self.provider.build_ping_request()

        self.assertEqual(method, Method_GET)
        self.assertEqual(url, Host + '/version1/user')
        self.assertEqual(headers['apiKey'], Password)
        self.assertEqual(params, {'username': Username})

# ################################################################################################################################

    def test_callbacks_are_not_signed(self) -> 'None':

        # A provider that signs nothing accepts every callback
        self.provider.verify_callback(ctx({}), b'id=1&status=Success', Webhook_URL)

# ################################################################################################################################

    def test_delivery_report_callback(self) -> 'None':

        params = {
            'id': 'ATXid_0123456789abcdef0123456789abcdef',
            'status': 'Failed',
            'phoneNumber': To,
            'networkCode': '63902',
            'failureReason': 'InsufficientCredit',
            'retryCount': '0',
        }

        events = self.provider.read_callback(ctx({}), urlencode(params).encode('utf8'))
        self.assertEqual(len(events), 1)

        event = events[0]
        self.assertEqual(event.kind, Kind_Status)
        self.assertEqual(event.id, 'ATXid_0123456789abcdef0123456789abcdef')
        self.assertEqual(event.status, Status_Failed)
        self.assertEqual(event.error_code, 'InsufficientCredit')
        self.assertEqual(event.from_, Sender)
        self.assertEqual(event.to, To)
        self.assertTrue(event.received_at)

# ################################################################################################################################

    def test_incoming_text_callback(self) -> 'None':

        params = {
            'id': '1001',
            'from': To,
            'to': Sender,
            'text': 'Thanks',
            'date': '2026-07-07 10:05:00',
            'linkId': 'c2f8a6e1-0001',
            'networkCode': '63902',
        }

        event = self.provider.read_callback(ctx({}), urlencode(params).encode('utf8'))[0]

        self.assertEqual(event.kind, Kind_Message)
        self.assertEqual(event.id, '1001')
        self.assertEqual(event.from_, To)
        self.assertEqual(event.to, Sender)
        self.assertEqual(event.body, 'Thanks')
        self.assertEqual(event.received_at, '2026-07-07 10:05:00')

# ################################################################################################################################

    def test_callback_response(self) -> 'None':

        status, content_type, body = self.provider.callback_response()

        self.assertEqual(status, 200)
        self.assertEqual(content_type, 'text/plain')
        self.assertEqual(body, 'OK')

# ################################################################################################################################

    def test_poll(self) -> 'None':

        # The first fetch starts at the beginning ..
        requests = self.provider.build_poll_requests({})
        self.assertEqual(len(requests), 1)

        request = requests[0]
        self.assertEqual(request.method, Method_GET)
        self.assertEqual(request.url, Host + '/version1/messaging')
        self.assertEqual(request.params, {'username': Username, 'lastReceivedId': '0'})

        # .. the fetch has two texts ..
        page = {
            'SMSMessageData': {
                'Messages': [
                    {'id': 1001, 'from': To, 'to': Sender, 'text': 'Thanks', 'date': '2026-07-07 10:05:00', 'linkId': 'a'},
                    {'id': 1002, 'from': To, 'to': Sender, 'text': 'Bye', 'date': '2026-07-07 10:06:00', 'linkId': 'b'},
                ],
            },
        }

        events, state = self.provider.read_poll_response(request, Response(200, page), {})

        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].kind, Kind_Message)
        self.assertEqual(events[0].id, '1001')
        self.assertEqual(events[1].body, 'Bye')
        self.assertEqual(state['last_received_id'], 1002)
        self.assertFalse(self.provider.has_more_pages(state))

        # .. and the next fetch starts after the highest ID seen.
        request = self.provider.build_poll_requests(state)[0]
        self.assertEqual(request.params['lastReceivedId'], '1002')

        empty = {'SMSMessageData': {'Messages': []}}
        events, state = self.provider.read_poll_response(request, Response(200, empty), state)

        self.assertEqual(events, [])
        self.assertEqual(state['last_received_id'], 1002)

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
