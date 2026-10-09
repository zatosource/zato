# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Vonage provider class against Vonage's documented requests, responses and callbacks, with the signed webhook
# verification checked against a fixed token over a fixed body.

# stdlib
from hashlib import sha256
from json import dumps, loads
from unittest import main, TestCase

# Zato
from zato.common.api import SMS
from zato.common.sms.model import Kind_Message, Kind_Status, Status_Delivered, Status_Failed, Status_Sent
from zato.server.connection.sms.base import CallbackRejected, Method_GET, Method_POST, ProviderError
from zato.server.connection.sms.vonage import compute_payload_hash, VonageProvider

# Test support
from test.zato.connection.sms.common import basic_auth, Body, Callback_URL, ctx, Host, new_provider, Password, Response, \
    Sender, Signature_Secret, To, Username, Webhook_URL

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

class VonageTestCase(TestCase):

    # A fixed callback body, its SHA-256 and the HS256 token of a signed webhook over it, signed with the connection's
    # signature secret
    Vector_Body = (
        b'{"message_uuid":"aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee","to":"447700900000","from":"Vonage",'
        b'"timestamp":"2020-01-01T14:00:00.000Z","status":"delivered","channel":"sms"}'
    )
    Vector_Payload_Hash = '66eed89496133d93b022a08c939aca782c5eea9de60fba4e891997da8089ce13'
    Vector_Token = (
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
        'eyJpYXQiOjE1Nzc4ODcyMDAsImp0aSI6ImM1YmE4ZjI0LTFhMTQtNGMxZS05M2U2LWE5OGYxYjBhMGExYiIsImlzcyI6IlZvbmFnZSIsImFwcGxpY2F0aW9uX2lkIjoi'
        'MTExMTExMTEtMjIyMi0zMzMzLTQ0NDQtNTU1NTU1NTU1NTU1IiwiYXBpX2tleSI6ImExYjJjM2Q0IiwicGF5bG9hZF9oYXNoIjoiNjZlZWQ4OTQ5NjEzM2Q5M2IwMjJh'
        'MDhjOTM5YWNhNzgyYzVlZWE5ZGU2MGZiYTRlODkxOTk3ZGE4MDg5Y2UxMyJ9.'
        'ROdC9Mgabo1EWFSJ3ohit5yj1YV6EpZa7awRCFaRn1Y'
    )

    def setUp(self) -> 'None':
        self.provider = new_provider(VonageProvider, **{SMS.Field_Signature_Secret: Signature_Secret})

# ################################################################################################################################

    def test_send_request(self) -> 'None':

        method, url, headers, data = self.provider.build_send_request(To, Body, Sender, Callback_URL)

        self.assertEqual(method, Method_POST)
        self.assertEqual(url, Host + '/v1/messages')
        self.assertEqual(headers['Authorization'], basic_auth(Username, Password))
        self.assertEqual(headers['Content-Type'], 'application/json')

        self.assertEqual(loads(data), {
            'message_type': 'text',
            'channel': 'sms',
            'to': To,
            'from': Sender,
            'text': Body,
        })

# ################################################################################################################################

    def test_send_response(self) -> 'None':

        payload = {'message_uuid': 'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee'}

        result = self.provider.read_send_response(Response(202, payload))

        self.assertEqual(result.id, 'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee')
        self.assertEqual(result.status, Status_Sent)
        self.assertEqual(result.raw, payload)

# ################################################################################################################################

    def test_send_error(self) -> 'None':

        payload = {
            'type': 'https://developer.vonage.com/api-errors/messages#1020',
            'title': 'Invalid params',
            'detail': "The value of one or more parameters is invalid",
            'instance': 'bf0ca0bf927b3b52e3cb03217e1a1ddf',
        }

        with self.assertRaises(ProviderError) as ctx:
            self.provider.read_send_response(Response(422, payload))

        self.assertIn('Invalid params', str(ctx.exception))

# ################################################################################################################################

    def test_ping_request(self) -> 'None':

        method, url, headers, params = self.provider.build_ping_request()

        self.assertEqual(method, Method_GET)
        self.assertEqual(url, Host + '/v2/reports/records')
        self.assertEqual(headers['Authorization'], basic_auth(Username, Password))
        self.assertEqual(params['account_id'], Username)
        self.assertEqual(params['product'], 'SMS')
        self.assertEqual(params['date_start'], params['date_end'])

# ################################################################################################################################

    def test_payload_hash_vector(self) -> 'None':

        self.assertEqual(compute_payload_hash(self.Vector_Body), self.Vector_Payload_Hash)
        self.assertEqual(sha256(self.Vector_Body).hexdigest(), self.Vector_Payload_Hash)

# ################################################################################################################################

    def test_callback_verification(self) -> 'None':

        headers = {'Authorization': 'Bearer ' + self.Vector_Token}

        # The token verifies over the body it was signed for ..
        self.provider.verify_callback(ctx(headers), self.Vector_Body, Webhook_URL)

        # .. not over another body ..
        with self.assertRaises(CallbackRejected):
            self.provider.verify_callback(ctx(headers), self.Vector_Body + b' ', Webhook_URL)

        # .. not with another secret ..
        other = new_provider(VonageProvider, **{SMS.Field_Signature_Secret: 'AnotherSignatureSecretOfFullLength0123456789'})

        with self.assertRaises(CallbackRejected):
            other.verify_callback(ctx(headers), self.Vector_Body, Webhook_URL)

        # .. not as anything but a bearer token ..
        with self.assertRaises(CallbackRejected):
            self.provider.verify_callback(ctx({'Authorization': 'Basic abc'}), self.Vector_Body, Webhook_URL)

        # .. and not without the header.
        with self.assertRaises(CallbackRejected):
            self.provider.verify_callback(ctx({}), self.Vector_Body, Webhook_URL)

# ################################################################################################################################

    def test_status_callback(self) -> 'None':

        events = self.provider.read_callback(ctx({}), self.Vector_Body)
        self.assertEqual(len(events), 1)

        event = events[0]
        self.assertEqual(event.kind, Kind_Status)
        self.assertEqual(event.id, 'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee')
        self.assertEqual(event.status, Status_Delivered)
        self.assertEqual(event.error_code, '')
        self.assertEqual(event.from_, 'Vonage')
        self.assertEqual(event.to, '447700900000')
        self.assertEqual(event.received_at, '2020-01-01T14:00:00.000Z')

# ################################################################################################################################

    def test_failed_status_callback(self) -> 'None':

        payload = {
            'message_uuid': 'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee',
            'to': '447700900000',
            'from': 'Vonage',
            'timestamp': '2020-01-01T14:00:00.000Z',
            'status': 'rejected',
            'error': {
                'type': 'https://developer.vonage.com/api-errors/messages#1330',
                'title': 'Rejected',
                'detail': 'The number is blacklisted',
            },
        }

        event = self.provider.read_callback(ctx({}), dumps(payload).encode('utf8'))[0]

        self.assertEqual(event.status, Status_Failed)
        self.assertEqual(event.error_code, 'https://developer.vonage.com/api-errors/messages#1330')

# ################################################################################################################################

    def test_incoming_text_callback(self) -> 'None':

        payload = {
            'message_uuid': 'ffffffff-bbbb-4ccc-8ddd-eeeeeeeeeeee',
            'to': Sender,
            'from': To,
            'timestamp': '2020-01-01T14:00:00.000Z',
            'channel': 'sms',
            'message_type': 'text',
            'text': 'Thanks',
        }

        event = self.provider.read_callback(ctx({}), dumps(payload).encode('utf8'))[0]

        self.assertEqual(event.kind, Kind_Message)
        self.assertEqual(event.id, 'ffffffff-bbbb-4ccc-8ddd-eeeeeeeeeeee')
        self.assertEqual(event.from_, To)
        self.assertEqual(event.to, Sender)
        self.assertEqual(event.body, 'Thanks')

# ################################################################################################################################

    def test_callback_response(self) -> 'None':

        status, content_type, body = self.provider.callback_response()

        self.assertEqual(status, 200)
        self.assertEqual(content_type, 'text/plain')
        self.assertEqual(body, '')

# ################################################################################################################################

    def test_poll(self) -> 'None':

        # The first poll lists both directions over a window ending now ..
        requests = self.provider.build_poll_requests({})
        self.assertEqual(len(requests), 2)

        by_direction = {}
        for request in requests:
            by_direction[request.tag] = request

        self.assertEqual(sorted(by_direction), ['inbound', 'outbound'])

        inbound = by_direction['inbound']
        self.assertEqual(inbound.url, Host + '/v2/reports/records')
        self.assertEqual(inbound.params['account_id'], Username)
        self.assertEqual(inbound.params['direction'], 'inbound')
        self.assertEqual(inbound.params['include_message'], 'true')

        window_end = inbound.params['date_end']

        # .. the inbound listing has one text and a next page ..
        inbound_page:'anydict' = {
            'records': [
                {
                    'message_id': '0A0000000123ABCD1',
                    'direction': 'inbound',
                    'from': To,
                    'to': Sender,
                    'date_received': '2026-07-07T10:05:00+0000',
                    'message_body': 'Thanks',
                },
            ],
            '_links': {'next': {'href': Host + '/v2/reports/records?direction=inbound&cursor=abc'}},
        }

        events, state = self.provider.read_poll_response(inbound, Response(200, inbound_page), {})

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].kind, Kind_Message)
        self.assertEqual(events[0].body, 'Thanks')
        self.assertEqual(state['window_end'], window_end)
        self.assertTrue(self.provider.has_more_pages(state))

        # .. the outbound listing has one report and no next page ..
        outbound_page = {
            'records': [
                {
                    'message_id': '0A0000000123ABCD2',
                    'direction': 'outbound',
                    'from': Sender,
                    'to': To,
                    'date_received': '2026-07-07T10:00:00+0000',
                    'status': 'delivered',
                    'error_code': '0',
                },
            ],
            '_links': {},
        }

        events, state = self.provider.read_poll_response(by_direction['outbound'], Response(200, outbound_page), state)

        self.assertEqual(events[0].kind, Kind_Status)
        self.assertEqual(events[0].status, Status_Delivered)
        self.assertEqual(state['done'], {'outbound': True})

        # .. so the next round reads the inbound page alone ..
        requests = self.provider.build_poll_requests(state)
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].tag, 'inbound')
        self.assertEqual(requests[0].url, inbound_page['_links']['next']['href'])

        # .. and after the last page the window's end is recorded.
        events, state = self.provider.read_poll_response(requests[0], Response(200, {'records': [], '_links': {}}), state)

        self.assertEqual(events, [])
        self.assertFalse(self.provider.has_more_pages(state))
        self.assertEqual(state['date_start'], window_end)
        self.assertNotIn('window_end', state)
        self.assertEqual(state['done'], {})

        requests = self.provider.build_poll_requests(state)
        self.assertEqual(len(requests), 2)
        self.assertEqual(requests[0].params['date_start'], window_end)

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
