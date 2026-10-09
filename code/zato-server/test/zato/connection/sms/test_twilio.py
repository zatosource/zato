# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Twilio provider class against Twilio's documented requests, responses and callbacks, with the signature
# algorithm checked against the documented test vector.

# stdlib
from unittest import main, TestCase
from urllib.parse import urlencode

# Zato
from zato.common.api import SMS
from zato.common.sms.model import Kind_Message, Kind_Status, Status_Delivered, Status_Failed, Status_Sent
from zato.server.connection.sms.base import CallbackRejected, Method_GET, Method_POST, ProviderError
from zato.server.connection.sms.twilio import compute_signature, TwilioProvider

# Test support
from test.zato.connection.sms.common import basic_auth, Body, Callback_URL, ctx, Host, new_provider, Password, Response, \
    Sender, To, Username, Webhook_URL

# ################################################################################################################################
# ################################################################################################################################

class TwilioTestCase(TestCase):

    # The documented signature test vector - URL, parameters, auth token and signature
    Documented_URL = 'https://mycompany.com/myapp.php?foo=1&bar=2'
    Documented_Auth_Token = '12345'
    Documented_Params = {
        'CallSid': 'CA1234567890ABCDE',
        'Caller': '+12349013030',
        'Digits': '1234',
        'From': '+12349013030',
        'To': '+18005551212',
    }
    Documented_Signature = '0/KCTR6DLpKmkAf8muzZqo1nDgQ='

    def setUp(self) -> 'None':
        self.provider = new_provider(TwilioProvider)

# ################################################################################################################################

    def test_send_request(self) -> 'None':

        method, url, headers, data = self.provider.build_send_request(To, Body, Sender, Callback_URL)

        self.assertEqual(method, Method_POST)
        self.assertEqual(url, f'{Host}/2010-04-01/Accounts/{Username}/Messages.json')
        self.assertEqual(headers['Authorization'], basic_auth(Username, Password))
        self.assertEqual(data, {
            'To': To,
            'From': Sender,
            'Body': Body,
            'StatusCallback': Callback_URL,
        })

# ################################################################################################################################

    def test_send_request_with_a_messaging_service(self) -> 'None':

        _, _, _, data = self.provider.build_send_request(To, Body, 'MG0123456789abcdef', None)

        self.assertEqual(data['MessagingServiceSid'], 'MG0123456789abcdef')
        self.assertNotIn('From', data)
        self.assertNotIn('StatusCallback', data)

# ################################################################################################################################

    def test_send_response(self) -> 'None':

        payload = {
            'sid': 'SM0123456789abcdef0123456789abcdef',
            'status': 'queued',
            'to': To,
            'from': Sender,
            'body': Body,
            'error_code': None,
        }

        result = self.provider.read_send_response(Response(201, payload))

        self.assertEqual(result.id, 'SM0123456789abcdef0123456789abcdef')
        self.assertEqual(result.status, Status_Sent)
        self.assertEqual(result.raw, payload)

# ################################################################################################################################

    def test_send_error(self) -> 'None':

        payload = {
            'code': 21211,
            'message': "The 'To' number +15005550001 is not a valid phone number.",
            'status': 400,
        }

        with self.assertRaises(ProviderError) as ctx:
            self.provider.read_send_response(Response(400, payload))

        self.assertIn('21211', str(ctx.exception))

# ################################################################################################################################

    def test_ping_request(self) -> 'None':

        method, url, headers, data = self.provider.build_ping_request()

        self.assertEqual(method, Method_GET)
        self.assertEqual(url, f'{Host}/2010-04-01/Accounts/{Username}.json')
        self.assertEqual(headers['Authorization'], basic_auth(Username, Password))
        self.assertIsNone(data)

# ################################################################################################################################

    def test_documented_signature_vector(self) -> 'None':

        signature = compute_signature(self.Documented_Auth_Token, self.Documented_URL, self.Documented_Params)
        self.assertEqual(signature, self.Documented_Signature)

# ################################################################################################################################

    def test_callback_verification(self) -> 'None':

        provider = new_provider(TwilioProvider, **{SMS.Field_Secret: self.Documented_Auth_Token})
        raw_body = urlencode(self.Documented_Params).encode('utf8')

        # The documented signature verifies ..
        provider.verify_callback(ctx({'X-Twilio-Signature': self.Documented_Signature}), raw_body, self.Documented_URL)

        # .. a signature over another URL does not ..
        with self.assertRaises(CallbackRejected):
            provider.verify_callback(ctx({'X-Twilio-Signature': self.Documented_Signature}), raw_body, Webhook_URL)

        # .. a modified body does not ..
        tampered = urlencode(dict(self.Documented_Params, Digits='9999')).encode('utf8')

        with self.assertRaises(CallbackRejected):
            provider.verify_callback(ctx({'X-Twilio-Signature': self.Documented_Signature}), tampered, self.Documented_URL)

        # .. and a callback without a signature does not.
        with self.assertRaises(CallbackRejected):
            provider.verify_callback(ctx({}), raw_body, self.Documented_URL)

# ################################################################################################################################

    def test_status_callback(self) -> 'None':

        params = {
            'MessageSid': 'SM0123456789abcdef0123456789abcdef',
            'MessageStatus': 'undelivered',
            'ErrorCode': '30003',
            'From': Sender,
            'To': To,
            'AccountSid': 'test-account-sid',
        }

        events = self.provider.read_callback(ctx({}), urlencode(params).encode('utf8'))
        self.assertEqual(len(events), 1)

        event = events[0]
        self.assertEqual(event.kind, Kind_Status)
        self.assertEqual(event.id, 'SM0123456789abcdef0123456789abcdef')
        self.assertEqual(event.status, Status_Failed)
        self.assertEqual(event.error_code, '30003')
        self.assertEqual(event.from_, Sender)
        self.assertEqual(event.to, To)
        self.assertEqual(event.body, '')
        self.assertTrue(event.received_at)
        self.assertEqual(event.raw, params)

# ################################################################################################################################

    def test_incoming_text_callback(self) -> 'None':

        params = {
            'MessageSid': 'SMfedcba9876543210fedcba9876543210',
            'From': To,
            'To': Sender,
            'Body': 'STOP',
            'NumMedia': '0',
        }

        events = self.provider.read_callback(ctx({}), urlencode(params).encode('utf8'))
        event = events[0]

        self.assertEqual(event.kind, Kind_Message)
        self.assertEqual(event.id, 'SMfedcba9876543210fedcba9876543210')
        self.assertEqual(event.from_, To)
        self.assertEqual(event.to, Sender)
        self.assertEqual(event.body, 'STOP')
        self.assertEqual(event.status, '')

# ################################################################################################################################

    def test_callback_response(self) -> 'None':

        status, content_type, body = self.provider.callback_response()

        self.assertEqual(status, 200)
        self.assertEqual(content_type, 'text/xml')
        self.assertEqual(body, '<?xml version="1.0" encoding="UTF-8"?><Response/>')

# ################################################################################################################################

    def test_poll(self) -> 'None':

        # The first poll starts a listing ..
        requests = self.provider.build_poll_requests({})
        self.assertEqual(len(requests), 1)

        request = requests[0]
        self.assertEqual(request.method, Method_GET)
        self.assertEqual(request.url, f'{Host}/2010-04-01/Accounts/{Username}/Messages.json')
        self.assertEqual(request.params['PageSize'], '1000')
        self.assertIn('DateSent>', request.params)

        # .. whose first page has an outbound report and an inbound text and a next page ..
        page_one = {
            'messages': [
                {
                    'sid': 'SM0000000000000000000000000000000a',
                    'direction': 'outbound-api',
                    'status': 'delivered',
                    'from': Sender,
                    'to': To,
                    'body': Body,
                    'date_sent': 'Tue, 07 Jul 2026 10:00:00 +0000',
                    'error_code': None,
                },
                {
                    'sid': 'SM0000000000000000000000000000000b',
                    'direction': 'inbound',
                    'status': 'received',
                    'from': To,
                    'to': Sender,
                    'body': 'Thanks',
                    'date_sent': 'Tue, 07 Jul 2026 10:05:00 +0000',
                    'error_code': None,
                },
            ],
            'next_page_uri': f'/2010-04-01/Accounts/{Username}/Messages.json?PageSize=1000&Page=1&PageToken=PA1',
        }

        events, state = self.provider.read_poll_response(request, Response(200, page_one), {})

        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].kind, Kind_Status)
        self.assertEqual(events[0].status, Status_Delivered)
        self.assertEqual(events[0].received_at, '2026-07-07T10:00:00+00:00')
        self.assertEqual(events[1].kind, Kind_Message)
        self.assertEqual(events[1].body, 'Thanks')

        self.assertEqual(state['date_sent'], '2026-07-07')
        self.assertTrue(self.provider.has_more_pages(state))

        # .. so the next poll reads that page ..
        requests = self.provider.build_poll_requests(state)
        self.assertEqual(requests[0].url, Host + page_one['next_page_uri'])
        self.assertEqual(requests[0].params, {})

        # .. and a last page without a next link records the date reached.
        page_two = {'messages': [], 'next_page_uri': None}
        events, state = self.provider.read_poll_response(requests[0], Response(200, page_two), state)

        self.assertEqual(events, [])
        self.assertFalse(self.provider.has_more_pages(state))

        requests = self.provider.build_poll_requests(state)
        self.assertEqual(requests[0].params['DateSent>'], '2026-07-07')

# ################################################################################################################################

    def test_poll_error(self) -> 'None':

        request = self.provider.build_poll_requests({})[0]

        with self.assertRaises(ProviderError):
            self.provider.read_poll_response(request, Response(401, '{"code": 20003}'), {})

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
