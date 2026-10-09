# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_REQUEST, OK, UNAUTHORIZED
from json import dumps
from uuid import uuid4

# Zato
from live_sms.base import Content_Type_JSON, json_response, Kind_Message, Kind_Status, not_found, SimulatorEvent, SimulatorRequest, \
    SimulatorResponse, SMSSimulator
from zato.common.api import SMS

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strdict

# ################################################################################################################################
# ################################################################################################################################

_send_path = '/sms/3/messages'
_inbox_path = '/sms/1/inbox/reports'
_reports_path = '/sms/3/reports'
_balance_path = '/account/1/balance'

_auth_prefix = 'App '
_group_pending = 'PENDING'

# Infobip's status groups, by the group name the simulator is told to deliver with
_status_groups = {
    'PENDING': (1, 'PENDING', 7, 'PENDING_ENROUTE', 'Message sent to next instance'),
    'DELIVERED': (3, 'DELIVERED', 5, 'DELIVERED_TO_HANDSET', 'Message delivered to handset'),
    'UNDELIVERABLE': (2, 'UNDELIVERABLE', 4, 'UNDELIVERABLE_REJECTED_OPERATOR', 'Message rejected by operator'),
    'EXPIRED': (4, 'EXPIRED', 16, 'EXPIRED_UNKNOWN', 'Message validity expired'),
    'REJECTED': (5, 'REJECTED', 6, 'REJECTED_NETWORK', 'Message rejected by network'),
}

# The error body of a wrong credential
_error_auth = {
    'requestError': {
        'serviceException': {
            'messageId': 'UNAUTHORIZED',
            'text': 'Invalid login details',
        }
    }
}

_timestamp_format = '%Y-%m-%dT%H:%M:%S.000+0000'

# ################################################################################################################################
# ################################################################################################################################

class InfobipSimulator(SMSSimulator):
    """ Infobip's SMS API - sends, the balance read of a ping, the inbox and delivery report pulls that return
    each item once, and unsigned callbacks to a delivery URL or an inbound URL.
    """
    provider = SMS.Provider.Infobip
    initial_status = _group_pending

    def __init__(self, username:'str', password:'str') -> 'None':
        super().__init__(username, password)

        # The sequence numbers of the events each pull endpoint has returned
        self.pulled_inbox:'set[int]' = set()
        self.pulled_reports:'set[int]' = set()

# ################################################################################################################################

    def reset(self) -> 'None':
        super().reset()
        self.pulled_inbox.clear()
        self.pulled_reports.clear()

# ################################################################################################################################

    def check_auth(self, request:'SimulatorRequest') -> 'bool':
        given = request.headers.get('authorization', '')
        out = given == _auth_prefix + self.password
        return out

    def auth_failure(self) -> 'SimulatorResponse':
        out = json_response(UNAUTHORIZED, _error_auth)
        return out

# ################################################################################################################################

    def route(self, request:'SimulatorRequest') -> 'SimulatorResponse':

        if request.path == _send_path and request.method == 'POST':
            out = self._send(request)

        elif request.path == _inbox_path and request.method == 'GET':
            out = self._inbox(request)

        elif request.path == _reports_path and request.method == 'GET':
            out = self._reports(request)

        elif request.path == _balance_path and request.method == 'GET':
            out = json_response(OK, {'balance': 10.0, 'currency': 'EUR'})

        else:
            out = not_found(request.path)

        return out

# ################################################################################################################################

    def _error(self, status:'int', message_id:'str', text:'str') -> 'SimulatorResponse':
        out = json_response(status, {'requestError': {'serviceException': {'messageId': message_id, 'text': text}}})
        return out

# ################################################################################################################################

    def _status(self, group_name:'str') -> 'anydict':
        group_id, group, status_id, name, description = _status_groups[group_name]
        out = {
            'groupId': group_id,
            'groupName': group,
            'id': status_id,
            'name': name,
            'description': description,
        }
        return out

# ################################################################################################################################

    def _send(self, request:'SimulatorRequest') -> 'SimulatorResponse':
        payload = request.json()

        if 'messages' not in payload or not payload['messages']:
            out = self._error(BAD_REQUEST, 'BAD_REQUEST', 'messages is required')
            return out

        message = payload['messages'][0]

        for name in ('sender', 'destinations', 'content'):
            if name not in message:
                out = self._error(BAD_REQUEST, 'BAD_REQUEST', f'{name} is required')
                return out

        to = message['destinations'][0]['to']
        sender = message['sender']
        text = message['content']['text']

        if to in self.rejected_numbers:
            out = self._error(BAD_REQUEST, 'BAD_REQUEST', self.rejected_numbers[to])
            return out

        callback_url = ''
        if 'webhooks' in message:
            callback_url = message['webhooks']['delivery']['url']

        message_id = uuid4().hex
        _ = self.record_send(message_id, to, sender, text, callback_url, payload)

        response = {
            'bulkId': uuid4().hex,
            'messages': [{
                'messageId': message_id,
                'status': self._status(_group_pending),
                'destination': to,
            }],
        }

        out = json_response(OK, response)
        return out

# ################################################################################################################################

    def _result(self, event:'SimulatorEvent') -> 'anydict':

        if event.kind == Kind_Message:
            out = {
                'messageId': event.message_id,
                'from': event.from_,
                'to': event.to,
                'text': event.body,
                'cleanText': event.body,
                'keyword': '',
                'receivedAt': event.at.strftime(_timestamp_format),
                'smsCount': 1,
            }
        else:
            out = {
                'bulkId': '',
                'messageId': event.message_id,
                'from': event.from_,
                'to': event.to,
                'sentAt': event.at.strftime(_timestamp_format),
                'doneAt': event.at.strftime(_timestamp_format),
                'smsCount': 1,
                'status': self._status(event.status),
                'error': self._error_of(event),
            }

        return out

# ################################################################################################################################

    def _error_of(self, event:'SimulatorEvent') -> 'anydict':

        if event.error_code:
            out = {'groupId': 2, 'groupName': 'HANDSET_ERRORS', 'id': 1, 'name': event.error_code,
                'description': 'Handset error', 'permanent': True}
        else:
            out = {'groupId': 0, 'groupName': 'OK', 'id': 0, 'name': 'NO_ERROR', 'description': 'No Error',
                'permanent': False}

        return out

# ################################################################################################################################

    def _pull(self, waiting:'list[SimulatorEvent]', pulled:'set[int]', limit:'int') -> 'tuple[list[anydict], int]':
        """ The events not yet returned, up to the limit, marked as returned, and the number remaining.
        """
        page = waiting[:limit]
        remaining = len(waiting) - len(page)

        results = []
        for event in page:
            pulled.add(event.seq)
            results.append(self._result(event))

        out = (results, remaining)
        return out

# ################################################################################################################################

    def _inbox(self, request:'SimulatorRequest') -> 'SimulatorResponse':
        limit = int(request.query.get('limit', str(self.page_size)))
        if limit > self.page_size:
            limit = self.page_size

        waiting = []
        for event in self.events:
            if event.kind == Kind_Message and event.seq not in self.pulled_inbox:
                waiting.append(event)

        results, remaining = self._pull(waiting, self.pulled_inbox, limit)

        out = json_response(OK, {
            'results': results,
            'messageCount': len(results),
            'pendingMessageCount': remaining,
        })
        return out

# ################################################################################################################################

    def _reports(self, request:'SimulatorRequest') -> 'SimulatorResponse':
        limit = int(request.query.get('limit', str(self.page_size)))
        if limit > self.page_size:
            limit = self.page_size

        # A report is final - a message still pending is not reported
        waiting = []
        for event in self.events:
            if event.kind == Kind_Status and event.status != _group_pending and event.seq not in self.pulled_reports:
                waiting.append(event)

        results, _ = self._pull(waiting, self.pulled_reports, limit)

        out = json_response(OK, {'results': results})
        return out

# ################################################################################################################################

    def new_incoming_id(self) -> 'str':
        out = uuid4().hex
        return out

# ################################################################################################################################

    def callback_body(self, event:'SimulatorEvent') -> 'tuple[str, bytes]':
        payload = {
            'results': [self._result(event)],
            'messageCount': 1,
            'pendingMessageCount': 0,
        }
        out = (Content_Type_JSON, dumps(payload).encode('utf8'))
        return out

# ################################################################################################################################

    def callback_headers(self, sign_url:'str', body:'bytes', event:'SimulatorEvent') -> 'strdict':
        out:'strdict' = {}
        return out

# ################################################################################################################################
# ################################################################################################################################
