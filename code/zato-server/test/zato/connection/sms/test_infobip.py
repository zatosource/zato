# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Infobip provider class against the requests, responses and callbacks Infobip documents.

# stdlib
from json import dumps, loads
from unittest import main, TestCase

# Zato
from zato.common.sms.model import Kind_Message, Kind_Status, Status_Delivered, Status_Failed, Status_Sent
from zato.server.connection.sms.base import Method_GET, Method_POST, ProviderError
from zato.server.connection.sms.infobip import InfobipProvider

# Test support
from test.zato.connection.sms.common import Body, Callback_URL, ctx, Host, new_provider, Password, Response, To, Webhook_URL

# ################################################################################################################################
# ################################################################################################################################

class InfobipTestCase(TestCase):

    def setUp(self) -> 'None':
        self.provider = new_provider(InfobipProvider)

# ################################################################################################################################

    def test_send_request(self) -> 'None':

        method, url, headers, data = self.provider.build_send_request(To, Body, 'ZatoSMS', Callback_URL)

        self.assertEqual(method, Method_POST)
        self.assertEqual(url, Host + '/sms/3/messages')
        self.assertEqual(headers['Authorization'], 'App ' + Password)
        self.assertEqual(headers['Content-Type'], 'application/json')

        self.assertEqual(loads(data), {
            'messages': [{
                'sender': 'ZatoSMS',
                'destinations': [{'to': To}],
                'content': {'text': Body},
                'webhooks': {'delivery': {'url': Callback_URL}},
            }],
        })

# ################################################################################################################################

    def test_send_request_without_a_callback(self) -> 'None':

        _, _, _, data = self.provider.build_send_request(To, Body, 'ZatoSMS', None)
        self.assertNotIn('webhooks', loads(data)['messages'][0])

# ################################################################################################################################

    def test_send_response(self) -> 'None':

        payload = {
            'bulkId': '2034072219640523072',
            'messages': [{
                'messageId': '2250be2d4219-3af1-78856-aabe-1362af1edfd2',
                'status': {
                    'groupId': 1,
                    'groupName': 'PENDING',
                    'id': 26,
                    'name': 'PENDING_ACCEPTED',
                    'description': 'Message sent to next instance',
                },
                'destination': To,
            }],
        }

        result = self.provider.read_send_response(Response(200, payload))

        self.assertEqual(result.id, '2250be2d4219-3af1-78856-aabe-1362af1edfd2')
        self.assertEqual(result.status, Status_Sent)
        self.assertEqual(result.raw, payload)

# ################################################################################################################################

    def test_send_error(self) -> 'None':

        payload = {
            'requestError': {
                'serviceException': {
                    'messageId': 'UNAUTHORIZED',
                    'text': 'Invalid login details',
                },
            },
        }

        with self.assertRaises(ProviderError) as ctx:
            self.provider.read_send_response(Response(401, payload))

        self.assertIn('Invalid login details', str(ctx.exception))

# ################################################################################################################################

    def test_ping_request(self) -> 'None':

        method, url, headers, data = self.provider.build_ping_request()

        self.assertEqual(method, Method_GET)
        self.assertEqual(url, Host + '/account/1/balance')
        self.assertEqual(headers['Authorization'], 'App ' + Password)
        self.assertIsNone(data)

# ################################################################################################################################

    def test_callbacks_are_not_signed(self) -> 'None':

        # A provider that signs nothing accepts every callback
        self.provider.verify_callback(ctx({}), b'{"results": []}', Webhook_URL)

# ################################################################################################################################

    def test_delivery_report_callback(self) -> 'None':

        payload = {
            'results': [
                {
                    'bulkId': '2034072219640523072',
                    'messageId': '2250be2d4219-3af1-78856-aabe-1362af1edfd2',
                    'to': To,
                    'from': 'ZatoSMS',
                    'sentAt': '2026-07-07T10:00:00.000+0000',
                    'doneAt': '2026-07-07T10:00:05.000+0000',
                    'status': {'groupId': 3, 'groupName': 'DELIVERED', 'id': 5, 'name': 'DELIVERED_TO_HANDSET'},
                    'error': {'groupId': 0, 'groupName': 'OK', 'id': 0, 'name': 'NO_ERROR', 'permanent': False},
                },
                {
                    'messageId': '3350be2d4219-3af1-78856-aabe-1362af1edfd3',
                    'to': To,
                    'from': 'ZatoSMS',
                    'sentAt': '2026-07-07T10:00:00.000+0000',
                    'doneAt': '2026-07-07T10:00:09.000+0000',
                    'status': {'groupId': 5, 'groupName': 'REJECTED', 'id': 8, 'name': 'REJECTED_PREFIX_MISSING'},
                    'error': {'groupId': 2, 'groupName': 'USER_ERRORS', 'id': 51, 'name': 'EC_INVALID_DESTINATION_ADDRESS'},
                },
            ],
        }

        events = self.provider.read_callback(ctx({}), dumps(payload).encode('utf8'))
        self.assertEqual(len(events), 2)

        delivered, rejected = events

        self.assertEqual(delivered.kind, Kind_Status)
        self.assertEqual(delivered.id, '2250be2d4219-3af1-78856-aabe-1362af1edfd2')
        self.assertEqual(delivered.status, Status_Delivered)
        self.assertEqual(delivered.error_code, '')
        self.assertEqual(delivered.received_at, '2026-07-07T10:00:05.000+0000')
        self.assertEqual(delivered.from_, 'ZatoSMS')
        self.assertEqual(delivered.to, To)

        self.assertEqual(rejected.status, Status_Failed)
        self.assertEqual(rejected.error_code, 'EC_INVALID_DESTINATION_ADDRESS')

# ################################################################################################################################

    def test_incoming_text_callback(self) -> 'None':

        payload = {
            'results': [{
                'messageId': '817790313235066447',
                'from': To,
                'to': '41793026727',
                'text': 'Thanks',
                'cleanText': 'Thanks',
                'keyword': '',
                'receivedAt': '2026-07-07T10:05:00.000+0000',
                'smsCount': 1,
            }],
            'messageCount': 1,
            'pendingMessageCount': 0,
        }

        event = self.provider.read_callback(ctx({}), dumps(payload).encode('utf8'))[0]

        self.assertEqual(event.kind, Kind_Message)
        self.assertEqual(event.id, '817790313235066447')
        self.assertEqual(event.from_, To)
        self.assertEqual(event.to, '41793026727')
        self.assertEqual(event.body, 'Thanks')
        self.assertEqual(event.received_at, '2026-07-07T10:05:00.000+0000')

# ################################################################################################################################

    def test_callback_response(self) -> 'None':

        status, content_type, body = self.provider.callback_response()

        self.assertEqual(status, 200)
        self.assertEqual(content_type, 'text/plain')
        self.assertEqual(body, '')

# ################################################################################################################################

    def test_poll(self) -> 'None':

        # A poll pulls the inbox and the reports ..
        requests = self.provider.build_poll_requests({})
        self.assertEqual(len(requests), 2)

        inbox, reports = requests
        self.assertEqual(inbox.tag, 'inbox')
        self.assertEqual(inbox.url, Host + '/sms/1/inbox/reports')
        self.assertEqual(inbox.params, {'limit': '1000'})
        self.assertEqual(reports.tag, 'reports')
        self.assertEqual(reports.url, Host + '/sms/3/reports')

        # .. the inbox has one text and more pending ..
        inbox_page = {
            'results': [{
                'messageId': '817790313235066447',
                'from': To,
                'to': '41793026727',
                'text': 'Thanks',
                'receivedAt': '2026-07-07T10:05:00.000+0000',
            }],
            'messageCount': 1,
            'pendingMessageCount': 3,
        }

        events, state = self.provider.read_poll_response(inbox, Response(200, inbox_page), {})

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].kind, Kind_Message)
        self.assertTrue(self.provider.has_more_pages(state))

        # .. the reports have one delivery ..
        reports_page = {
            'results': [{
                'messageId': '2250be2d4219-3af1-78856-aabe-1362af1edfd2',
                'to': To,
                'from': 'ZatoSMS',
                'sentAt': '2026-07-07T10:00:00.000+0000',
                'doneAt': '2026-07-07T10:00:05.000+0000',
                'status': {'groupId': 3, 'groupName': 'DELIVERED', 'id': 5, 'name': 'DELIVERED_TO_HANDSET'},
                'error': {'groupId': 0, 'groupName': 'OK', 'id': 0, 'name': 'NO_ERROR'},
            }],
        }

        events, state = self.provider.read_poll_response(reports, Response(200, reports_page), state)

        self.assertEqual(events[0].kind, Kind_Status)
        self.assertEqual(events[0].status, Status_Delivered)

        # .. so the next round pulls the inbox alone, until nothing is pending.
        requests = self.provider.build_poll_requests(state)
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].tag, 'inbox')

        empty_inbox = {'results': [], 'messageCount': 0, 'pendingMessageCount': 0}
        events, state = self.provider.read_poll_response(requests[0], Response(200, empty_inbox), state)

        self.assertEqual(events, [])
        self.assertFalse(self.provider.has_more_pages(state))
        self.assertEqual(len(self.provider.build_poll_requests(state)), 2)

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
