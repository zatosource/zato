# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from hashlib import sha256
from http.client import ACCEPTED, BAD_REQUEST, OK, UNAUTHORIZED, UNPROCESSABLE_ENTITY
from json import dumps
from time import time
from urllib.parse import urlencode
from uuid import uuid4

# PyJWT
from jwt import encode as jwt_encode

# Zato
from live_sms.base import basic_auth_matches, Content_Type_JSON, json_response, Kind_Message, not_found, paginate, \
    SimEvent, SimRequest, SimResponse, SMSSimulator
from zato.common.api import SMS

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strdict

# ################################################################################################################################
# ################################################################################################################################

_messages_path = '/v1/messages'
_reports_path = '/v2/reports/records'

_status_submitted = 'submitted'
_direction_inbound = 'inbound'
_direction_outbound = 'outbound'

_jwt_algorithm = 'HS256'
_timestamp_format = '%Y-%m-%dT%H:%M:%SZ'

# The error Vonage answers a wrong credential with
_error_auth = {
    'type': 'https://developer.vonage.com/api-errors#unauthorized',
    'title': 'Unauthorized',
    'detail': 'You did not provide correct credentials.',
    'instance': 'simulator',
}

# ################################################################################################################################
# ################################################################################################################################

def sign_callback(signature_secret:'str', body:'bytes') -> 'str':
    """ The bearer token of a signed Vonage callback - HS256 with the SHA-256 hash of the body as a claim.
    """
    claims = {
        'iat': int(time()),
        'jti': uuid4().hex,
        'application_id': 'simulator',
        'payload_hash': sha256(body).hexdigest(),
    }

    out = jwt_encode(claims, signature_secret, algorithm=_jwt_algorithm)
    return out

# ################################################################################################################################
# ################################################################################################################################

class VonageSimulator(SMSSimulator):
    """ Vonage's Messages API and Reports API - sends, the reports read a ping and a poll make, and status
    and inbound-message callbacks signed with the account's signature secret.
    """
    provider = SMS.Provider.Vonage
    initial_status = _status_submitted

    def __init__(self, username:'str', password:'str', signature_secret:'str') -> 'None':
        super().__init__(username, password)
        self.signature_secret = signature_secret

        # Numbers a send to which is rejected, with the Vonage reason given
        self.rejected_numbers:'dict[str, str]' = {}

# ################################################################################################################################

    def check_auth(self, request:'SimRequest') -> 'bool':
        out = basic_auth_matches(request, self.username, self.password)
        return out

    def auth_failure(self) -> 'SimResponse':
        out = json_response(UNAUTHORIZED, _error_auth)
        return out

# ################################################################################################################################

    def route(self, request:'SimRequest') -> 'SimResponse':

        if request.path == _messages_path and request.method == 'POST':
            out = self._send(request)

        elif request.path == _reports_path and request.method == 'GET':
            out = self._reports(request)

        else:
            out = not_found(request.path)

        return out

# ################################################################################################################################

    def _error(self, status:'int', title:'str', detail:'str') -> 'SimResponse':
        out = json_response(status, {
            'type': 'https://developer.vonage.com/api-errors',
            'title': title,
            'detail': detail,
            'instance': 'simulator',
        })
        return out

# ################################################################################################################################

    def _send(self, request:'SimRequest') -> 'SimResponse':
        payload = request.json()

        for name in ('message_type', 'channel', 'to', 'from', 'text'):
            if name not in payload:
                out = self._error(UNPROCESSABLE_ENTITY, 'Missing parameter', f'The `{name}` parameter is required')
                return out

        if payload['channel'] != 'sms' or payload['message_type'] != 'text':
            out = self._error(BAD_REQUEST, 'Invalid parameter', 'Only text messages over sms are accepted')
            return out

        to = payload['to']

        if to in self.rejected_numbers:
            out = self._error(UNPROCESSABLE_ENTITY, 'Invalid params', self.rejected_numbers[to])
            return out

        message_uuid = str(uuid4())
        _ = self.add_send(message_uuid, to, payload['from'], payload['text'], '', payload)

        out = json_response(ACCEPTED, {'message_uuid': message_uuid})
        return out

# ################################################################################################################################

    def _record(self, event:'SimEvent') -> 'anydict':

        out = {
            'account_id': self.username,
            'message_id': event.message_id,
            'client_ref': '',
            'from': event.from_,
            'to': event.to,
            'date_received': event.at.strftime(_timestamp_format),
            'currency': 'EUR',
            'price': '0.0',
        }

        if event.kind == Kind_Message:
            out['direction'] = _direction_inbound
            out['status'] = 'delivered'
            out['message_body'] = event.body
        else:
            out['direction'] = _direction_outbound
            out['status'] = event.status
            out['error_code'] = event.error_code
            out['message_body'] = event.body

        return out

# ################################################################################################################################

    def _reports(self, request:'SimRequest') -> 'SimResponse':
        """ The records of one direction over a dated window, in pages linked through _links.next.
        """
        for name in ('account_id', 'product', 'direction', 'date_start', 'date_end'):
            if name not in request.query:
                out = self._error(BAD_REQUEST, 'Missing parameter', f'The `{name}` parameter is required')
                return out

        if request.query['account_id'] != self.username:
            out = self._error(UNAUTHORIZED, 'Unauthorized', 'The account_id is not the one authenticated')
            return out

        direction = request.query['direction']
        date_start = request.query['date_start']
        date_end = request.query['date_end']
        offset = int(request.query.get('offset', '0'))

        wants_inbound = direction == _direction_inbound

        items = []
        for event in self.events:
            is_inbound = event.kind == Kind_Message
            if is_inbound != wants_inbound:
                continue
            at = event.at.strftime(_timestamp_format)
            if date_start <= at <= date_end:
                items.append(self._record(event))

        page, next_offset = paginate(items, self.page_size, offset)

        payload:'anydict' = {
            'request_id': uuid4().hex,
            'request_status': 'SUCCESS',
            'records': page,
            '_links': {'self': {'href': self.url + _reports_path}},
        }

        if next_offset >= 0:
            next_query = dict(request.query)
            next_query['offset'] = str(next_offset)
            query_text = urlencode(next_query)
            payload['_links']['next'] = {'href': f'{self.url}{_reports_path}?{query_text}'}

        out = json_response(OK, payload)
        return out

# ################################################################################################################################

    def new_incoming_id(self) -> 'str':
        out = str(uuid4())
        return out

# ################################################################################################################################

    def callback_body(self, event:'SimEvent') -> 'tuple[str, bytes]':

        payload:'anydict' = {
            'message_uuid': event.message_id,
            'to': event.to,
            'from': event.from_,
            'timestamp': event.at.isoformat(),
            'channel': 'sms',
        }

        if event.kind == Kind_Message:
            payload['message_type'] = 'text'
            payload['text'] = event.body
        else:
            payload['status'] = event.status
            if event.error_code:
                payload['error'] = {
                    'type': event.error_code,
                    'title': 'Delivery failed',
                    'detail': f'The message could not be delivered, code {event.error_code}',
                }

        out = (Content_Type_JSON, dumps(payload).encode('utf8'))
        return out

# ################################################################################################################################

    def callback_headers(self, sign_url:'str', body:'bytes', event:'SimEvent') -> 'strdict':
        token = sign_callback(self.signature_secret, body)
        out = {'Authorization': 'Bearer ' + token}
        return out

# ################################################################################################################################
# ################################################################################################################################
