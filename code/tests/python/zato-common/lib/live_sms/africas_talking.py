# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_REQUEST, CREATED, OK, UNAUTHORIZED
from uuid import uuid4

# Zato
from live_sms.base import Content_Type_Form, Content_Type_Text, form_encode, json_response, Kind_Message, not_found, \
    SimulatorEvent, SimulatorRequest, SimulatorResponse, SMSSimulator
from zato.common.api import SMS

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strdict

# ################################################################################################################################
# ################################################################################################################################

_messaging_path = '/version1/messaging'
_user_path = '/version1/user'
_header_api_key = 'apikey'

_status_sent = 'Sent'
_status_code_sent = 101

# The rejection statuses, each with the code Africa's Talking gives it
Rejection_Statuses = {
    'InvalidPhoneNumber': 403,
    'UnsupportedNumberType': 405,
    'InsufficientBalance': 406,
    'UserInBlacklist': 407,
}

_timestamp_format = '%Y-%m-%d %H:%M:%S'

# ################################################################################################################################
# ################################################################################################################################

class AfricasTalkingSimulator(SMSSimulator):
    """ Africa's Talking's messaging API - sends, the user read of a ping, the lastReceivedId fetch of a poll
    and form-encoded callbacks for delivery reports and incoming texts.
    """
    provider = SMS.Provider.Africas_Talking
    initial_status = _status_sent

    def __init__(self, username:'str', password:'str') -> 'None':
        super().__init__(username, password)

        # Incoming texts have integer IDs, the paging key of the fetch endpoint
        self._next_incoming_id = 1000

# ################################################################################################################################

    def check_auth(self, request:'SimulatorRequest') -> 'bool':
        given = request.headers.get(_header_api_key, '')
        out = given == self.password
        return out

    def auth_failure(self) -> 'SimulatorResponse':
        out = SimulatorResponse(UNAUTHORIZED, Content_Type_Text, 'The supplied authentication is invalid')
        return out

# ################################################################################################################################

    def route(self, request:'SimulatorRequest') -> 'SimulatorResponse':

        if request.path == _messaging_path:
            if request.method == 'POST':
                out = self._send(request)
            else:
                out = self._fetch(request)

        elif request.path == _user_path and request.method == 'GET':
            out = self._user(request)

        else:
            out = not_found(request.path)

        return out

# ################################################################################################################################

    def _user(self, request:'SimulatorRequest') -> 'SimulatorResponse':

        if request.query.get('username') != self.username:
            out = SimulatorResponse(UNAUTHORIZED, Content_Type_Text, 'The supplied authentication is invalid')
        else:
            out = json_response(OK, {'UserData': {'balance': 'KES 1000.0000'}})

        return out

# ################################################################################################################################

    def _send(self, request:'SimulatorRequest') -> 'SimulatorResponse':
        form = request.form()

        for name in ('username', 'to', 'message'):
            if name not in form:
                out = SimulatorResponse(BAD_REQUEST, Content_Type_Text, f'Missing parameter: {name}')
                return out

        if form['username'] != self.username:
            out = SimulatorResponse(UNAUTHORIZED, Content_Type_Text, 'The supplied authentication is invalid')
            return out

        to = form['to']
        message = form['message']
        from_ = form.get('from', '')

        if to in self.rejected_numbers:
            status = self.rejected_numbers[to]
            recipient = {
                'statusCode': Rejection_Statuses[status],
                'number': to,
                'status': status,
                'cost': 'KES 0.0000',
                'messageId': 'None',
            }
            payload = {'SMSMessageData': {'Message': 'Sent to 0/1 Total Cost: KES 0.0000', 'Recipients': [recipient]}}
            out = json_response(CREATED, payload)
            return out

        message_id = 'ATXid_' + uuid4().hex
        _ = self.record_send(message_id, to, from_, message, '', form)

        recipient = {
            'statusCode': _status_code_sent,
            'number': to,
            'status': _status_sent,
            'cost': 'KES 0.8000',
            'messageId': message_id,
        }
        payload = {'SMSMessageData': {'Message': 'Sent to 1/1 Total Cost: KES 0.8000', 'Recipients': [recipient]}}

        out = json_response(CREATED, payload)
        return out

# ################################################################################################################################

    def _message(self, event:'SimulatorEvent') -> 'anydict':
        out = {
            'linkId': uuid4().hex,
            'text': event.body,
            'to': event.to,
            'id': int(event.message_id),
            'date': event.at.strftime(_timestamp_format),
            'from': event.from_,
        }
        return out

# ################################################################################################################################

    def _fetch(self, request:'SimulatorRequest') -> 'SimulatorResponse':
        """ Every incoming text with an ID above lastReceivedId, oldest first.
        """
        if request.query.get('username') != self.username:
            out = SimulatorResponse(UNAUTHORIZED, Content_Type_Text, 'The supplied authentication is invalid')
            return out

        last_received_id = int(request.query.get('lastReceivedId', '0'))

        messages = []
        for event in self.events:
            if event.kind == Kind_Message and int(event.message_id) > last_received_id:
                messages.append(self._message(event))

        messages = messages[:self.page_size]

        out = json_response(OK, {'SMSMessageData': {'Messages': messages}})
        return out

# ################################################################################################################################

    def new_incoming_id(self) -> 'str':
        self._next_incoming_id += 1
        out = str(self._next_incoming_id)
        return out

# ################################################################################################################################

    def callback_params(self, event:'SimulatorEvent') -> 'strdict':

        if event.kind == Kind_Message:
            out = {
                'id': event.message_id,
                'from': event.from_,
                'to': event.to,
                'text': event.body,
                'date': event.at.strftime(_timestamp_format),
                'linkId': uuid4().hex,
                'networkCode': '63902',
            }
        else:
            out = {
                'id': event.message_id,
                'status': event.status,
                'phoneNumber': event.to,
                'networkCode': '63902',
                'retryCount': '0',
            }
            if event.error_code:
                out['failureReason'] = event.error_code

        return out

# ################################################################################################################################

    def callback_body(self, event:'SimulatorEvent') -> 'tuple[str, bytes]':
        out = (Content_Type_Form, form_encode(self.callback_params(event)))
        return out

# ################################################################################################################################

    def callback_headers(self, sign_url:'str', body:'bytes', event:'SimulatorEvent') -> 'strdict':
        out:'strdict' = {}
        return out

# ################################################################################################################################
# ################################################################################################################################
