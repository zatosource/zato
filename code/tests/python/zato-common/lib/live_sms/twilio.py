# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64encode
from email.utils import format_datetime
from hashlib import sha1
from hmac import new as hmac_new
from http.client import BAD_REQUEST, CREATED, OK, UNAUTHORIZED
from uuid import uuid4

# Zato
from live_sms.base import basic_auth_matches, Content_Type_Form, form_encode, json_response, Kind_Message, not_found, \
    paginate, SimulatorEvent, SimulatorRequest, SimulatorResponse, SMSSimulator
from zato.common.api import SMS

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strdict

# ################################################################################################################################
# ################################################################################################################################

# The test numbers documented for Twilio's test credentials
Test_Number_From_Valid = '+15005550006'
Test_Number_To_Not_Mobile = '+15005550009'
Test_Number_To_Invalid = '+15005550001'
Test_Number_From_Invalid = '+15005550007'

# The error of each test number
Error_To_Not_Mobile = 21614
Error_To_Invalid = 21211
Error_From_Invalid = 21606

_test_number_errors = {
    Test_Number_To_Not_Mobile: (Error_To_Not_Mobile, 'To number: {to}, is not a mobile number'),
    Test_Number_To_Invalid: (Error_To_Invalid, "The 'To' number {to} is not a valid phone number."),
}

_error_from_invalid_text = "The From phone number {from_} is not a valid, SMS-capable inbound phone number or short code for your account."

# The authentication error Twilio answers a wrong credential with
_error_auth = {
    'code': 20003,
    'message': 'Authenticate',
    'more_info': 'https://www.twilio.com/docs/errors/20003',
    'status': UNAUTHORIZED,
}

_api_version = '2010-04-01'
_messaging_service_prefix = 'MG'
_status_queued = 'queued'
_direction_inbound = 'inbound'
_direction_outbound = 'outbound-api'
_header_signature = 'X-Twilio-Signature'

# ################################################################################################################################
# ################################################################################################################################

def compute_signature(auth_token:'str', url:'str', params:'strdict') -> 'str':
    """ Base64 of HMAC-SHA1 over the URL followed by every parameter name and value in name order.
    """
    data = url

    for name in sorted(params):
        data += name + params[name]

    digest = hmac_new(auth_token.encode('utf8'), data.encode('utf8'), sha1).digest()
    out = b64encode(digest).decode('ascii')

    return out

# ################################################################################################################################

def new_message_sid() -> 'str':
    out = 'SM' + uuid4().hex
    return out

# ################################################################################################################################
# ################################################################################################################################

class TwilioSimulator(SMSSimulator):
    """ Twilio's Messages resource - sends, the account read of a ping, the message listing of a poll
    and status and incoming-text callbacks signed with the auth token.
    """
    provider = SMS.Provider.Twilio
    initial_status = _status_queued

    def _account_path(self, suffix:'str') -> 'str':
        out = f'/{_api_version}/Accounts/{self.username}{suffix}'
        return out

# ################################################################################################################################

    def check_auth(self, request:'SimulatorRequest') -> 'bool':
        out = basic_auth_matches(request, self.username, self.password)
        return out

    def auth_failure(self) -> 'SimulatorResponse':
        out = json_response(UNAUTHORIZED, _error_auth)
        return out

# ################################################################################################################################

    def route(self, request:'SimulatorRequest') -> 'SimulatorResponse':

        if request.path == self._account_path('/Messages.json'):
            if request.method == 'POST':
                out = self._send(request)
            else:
                out = self._list(request)

        elif request.path == self._account_path('.json') and request.method == 'GET':
            out = json_response(OK, {'sid': self.username, 'status': 'active', 'friendly_name': 'Simulator'})

        else:
            out = not_found(request.path)

        return out

# ################################################################################################################################

    def _error(self, status:'int', code:'int', message:'str') -> 'SimulatorResponse':
        out = json_response(status, {'code': code, 'message': message, 'more_info': f'https://www.twilio.com/docs/errors/{code}',
            'status': status})
        return out

# ################################################################################################################################

    def _send(self, request:'SimulatorRequest') -> 'SimulatorResponse':
        form = request.form()

        if 'To' not in form:
            out = self._error(BAD_REQUEST, 21604, "A 'To' phone number is required.")
            return out

        if 'Body' not in form:
            out = self._error(BAD_REQUEST, 21602, 'Message body is required.')
            return out

        to = form['To']
        body = form['Body']

        if 'MessagingServiceSid' in form:
            from_ = form['MessagingServiceSid']
        elif 'From' in form:
            from_ = form['From']
        else:
            out = self._error(BAD_REQUEST, 21603, "A 'From' phone number is required.")
            return out

        if from_ == Test_Number_From_Invalid:
            out = self._error(BAD_REQUEST, Error_From_Invalid, _error_from_invalid_text.format(from_=from_))
            return out

        if to in _test_number_errors:
            code, text = _test_number_errors[to]
            out = self._error(BAD_REQUEST, code, text.format(to=to))
            return out

        callback_url = form.get('StatusCallback', '')
        message_sid = new_message_sid()

        _ = self.record_send(message_sid, to, from_, body, callback_url, form)

        payload = self._message_payload(message_sid, to, from_, body, _status_queued, '', _direction_outbound)
        out = json_response(CREATED, payload)

        return out

# ################################################################################################################################

    def _message_payload(self, sid:'str', to:'str', from_:'str', body:'str', status:'str', error_code:'str',
        direction:'str') -> 'anydict':

        # Twilio lists a message without an error as error_code null
        error_value = None
        if error_code:
            error_value = int(error_code)

        out = {
            'sid': sid,
            'account_sid': self.username,
            'to': to,
            'from': from_,
            'body': body,
            'status': status,
            'direction': direction,
            'error_code': error_value,
            'num_segments': '1',
            'api_version': _api_version,
        }
        return out

# ################################################################################################################################

    def _listing_item(self, event:'SimulatorEvent') -> 'anydict':

        if event.kind == Kind_Message:
            direction = _direction_inbound
            status = 'received'
        else:
            direction = _direction_outbound
            status = event.status

        out = self._message_payload(event.message_id, event.to, event.from_, event.body, status, event.error_code,
            direction)
        out['date_sent'] = format_datetime(event.at)
        out['date_created'] = format_datetime(event.at)

        return out

# ################################################################################################################################

    def _list(self, request:'SimulatorRequest') -> 'SimulatorResponse':
        """ The message listing - every message dated on or after the DateSent> filter, newest first,
        in pages of PageSize with a next_page_uri while pages remain.
        """
        date_after = request.query.get('DateSent>', '')
        offset = int(request.query.get('Page', '0'))

        page_size = int(request.query.get('PageSize', str(self.page_size)))
        if page_size > self.page_size:
            page_size = self.page_size

        # The listing shows the latest status of each message
        latest:'dict[str, SimulatorEvent]' = {}
        for event in self.events:
            latest[event.message_id] = event

        items = []
        for event in latest.values():
            if event.at.strftime('%Y-%m-%d') >= date_after:
                items.append(self._listing_item(event))

        items.reverse()

        page, next_offset = paginate(items, page_size, offset * page_size)

        payload:'anydict' = {
            'messages': page,
            'page': offset,
            'page_size': page_size,
            'next_page_uri': None,
        }

        if next_offset >= 0:
            next_page = offset + 1
            payload['next_page_uri'] = self._account_path(f'/Messages.json?DateSent%3E={date_after}&PageSize={page_size}&Page={next_page}')

        out = json_response(OK, payload)
        return out

# ################################################################################################################################

    def new_incoming_id(self) -> 'str':
        out = new_message_sid()
        return out

# ################################################################################################################################

    def callback_params(self, event:'SimulatorEvent') -> 'strdict':
        """ The form fields of a status callback or an incoming text.
        """
        out = {
            'MessageSid': event.message_id,
            'SmsSid': event.message_id,
            'AccountSid': self.username,
            'From': event.from_,
            'To': event.to,
            'ApiVersion': _api_version,
        }

        if event.kind == Kind_Message:
            out['Body'] = event.body
            out['NumMedia'] = '0'
        else:
            out['MessageStatus'] = event.status
            out['SmsStatus'] = event.status
            if event.error_code:
                out['ErrorCode'] = event.error_code

        return out

# ################################################################################################################################

    def callback_body(self, event:'SimulatorEvent') -> 'tuple[str, bytes]':
        out = (Content_Type_Form, form_encode(self.callback_params(event)))
        return out

# ################################################################################################################################

    def callback_headers(self, sign_url:'str', body:'bytes', event:'SimulatorEvent') -> 'strdict':
        signature = compute_signature(self.password, sign_url, self.callback_params(event))
        out = {_header_signature: signature}
        return out

# ################################################################################################################################
# ################################################################################################################################
