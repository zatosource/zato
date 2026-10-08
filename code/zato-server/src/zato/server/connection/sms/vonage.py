# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Vonage - the Messages API for sends and callbacks, with each callback signed as an HS256 JWT that contains
# a hash of the body, and the Reports API for polling.

# stdlib
from base64 import b64encode
from datetime import datetime, timezone
from hashlib import sha256
from hmac import compare_digest
from http.client import OK

# PyJWT
from jwt import decode as jwt_decode, PyJWTError

# Zato
from zato.common.api import SMS
from zato.common.json_internal import dumps, loads
from zato.common.sms.model import SendResult, Status_Delivered, Status_Failed, Status_Sent
from zato.server.connection.sms.base import CallbackRejected, Content_Type_Text, Ctx_Headers, Header_Authorization, \
    Method_GET, Method_POST, new_message_event, new_status_event, PollRequest, Provider, ProviderError, register_provider, \
    text_or_empty

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from requests import Response
    from zato.common.ext.bunch import Bunch
    from zato.common.sms.model import SMSEvent
    from zato.common.typing_ import anydict, stranydict, strdict, strnone
    from zato.server.connection.sms.base import CallbackResponse, PollRequestList, PollResult, SendRequest, SMSEventList

# ################################################################################################################################
# ################################################################################################################################

# The Messages API path
_messages_path = '/v1/messages'

# The Reports API path and its parameters
_reports_path = '/v2/reports/records'
_param_account_id = 'account_id'
_param_product = 'product'
_param_direction = 'direction'
_param_date_start = 'date_start'
_param_date_end = 'date_end'
_param_include_message = 'include_message'
_product_sms = 'SMS'
_direction_inbound = 'inbound'
_direction_outbound = 'outbound'
_directions = (_direction_inbound, _direction_outbound)

# Request body fields
_body_message_type = 'message_type'
_body_channel = 'channel'
_body_to = 'to'
_body_from = 'from'
_body_text = 'text'
_message_type_text = 'text'
_channel_sms = 'sms'

# Response and callback fields
_field_message_uuid = 'message_uuid'
_field_status = 'status'
_field_timestamp = 'timestamp'
_field_error = 'error'
_field_error_title = 'title'
_field_error_detail = 'detail'
_field_error_type = 'type'

# Reports API record fields
_field_records = 'records'
_field_links = '_links'
_field_next = 'next'
_field_href = 'href'
_field_message_id = 'message_id'
_field_direction = 'direction'
_field_date_received = 'date_received'
_field_error_code = 'error_code'
_field_message_body = 'message_body'

# The JWT claim with the SHA-256 hash of the callback body
_claim_payload_hash = 'payload_hash'
_jwt_algorithm = 'HS256'
_bearer_prefix = 'Bearer '

# Poll state keys - where the next window opens, where the current one ends, the next page of each direction
# and the directions already read in full over the current window
_state_date_start = 'date_start'
_state_window_end = 'window_end'
_state_next = 'next'
_state_done = 'done'

# The timestamp format the Reports API filters by
_timestamp_format = '%Y-%m-%dT%H:%M:%SZ'

# ################################################################################################################################
# ################################################################################################################################

def _now_text() -> 'str':
    out = datetime.now(timezone.utc).strftime(_timestamp_format)
    return out

# ################################################################################################################################

def compute_payload_hash(raw_body:'bytes') -> 'str':
    out = sha256(raw_body).hexdigest()
    return out

# ################################################################################################################################
# ################################################################################################################################

class VonageProvider(Provider):
    name = SMS.Provider.Vonage

    status_mapping = {
        'submitted': Status_Sent,
        'delivered': Status_Delivered,
        'read': Status_Delivered,
        'rejected': Status_Failed,
        'undeliverable': Status_Failed,
    }

    def __init__(self, config:'Bunch') -> 'None':
        super().__init__(config)
        self.signature_secret = text_or_empty(config.get(SMS.Field_Signature_Secret))

# ################################################################################################################################

    def _headers(self) -> 'strdict':
        credentials = f'{self.username}:{self.password}'.encode('utf8')
        out = {
            'Authorization': 'Basic ' + b64encode(credentials).decode('ascii'),
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        return out

# ################################################################################################################################

    def build_send_request(self, to:'str', body:'str', sender:'str', callback_url:'strnone') -> 'SendRequest':

        data = {
            _body_message_type: _message_type_text,
            _body_channel: _channel_sms,
            _body_to: to,
            _body_from: sender,
            _body_text: body,
        }

        url = self.host + _messages_path
        out = (Method_POST, url, self._headers(), dumps(data))

        return out

# ################################################################################################################################

    def read_send_response(self, response:'Response') -> 'SendResult':
        payload = loads(response.text)

        if not response.ok:
            title = payload.get(_field_error_title)
            detail = payload.get(_field_error_detail)
            raise ProviderError(f'Vonage error {response.status_code}: {title} - {detail}')

        out = SendResult()
        out.id = payload[_field_message_uuid]
        out.status = Status_Sent
        out.raw = payload

        return out

# ################################################################################################################################

    def build_ping_request(self) -> 'SendRequest':

        # An authenticated read of the Reports API over an empty window - the same host and credentials a poll uses
        now = _now_text()
        params = {
            _param_account_id: self.username,
            _param_product: _product_sms,
            _param_direction: _direction_outbound,
            _param_date_start: now,
            _param_date_end: now,
        }
        url = self.host + _reports_path
        out = (Method_GET, url, self._headers(), params)
        return out

# ################################################################################################################################

    def verify_callback(self, request_ctx:'stranydict', raw_body:'bytes', url:'str') -> 'None':
        headers = request_ctx[Ctx_Headers]

        if Header_Authorization not in headers:
            raise CallbackRejected('Vonage callback has no Authorization header')

        value = headers[Header_Authorization]

        if not value.startswith(_bearer_prefix):
            raise CallbackRejected('Vonage callback Authorization header is not a bearer token')

        token = value[len(_bearer_prefix):]

        try:
            claims = jwt_decode(token, self.signature_secret, algorithms=[_jwt_algorithm])
        except PyJWTError as e:
            raise CallbackRejected(f'Vonage callback token does not verify: {e}')

        if _claim_payload_hash not in claims:
            raise CallbackRejected('Vonage callback token has no payload hash')

        expected = compute_payload_hash(raw_body)

        if not compare_digest(claims[_claim_payload_hash], expected):
            raise CallbackRejected('Vonage callback payload hash does not match the body')

# ################################################################################################################################

    def read_callback(self, request_ctx:'stranydict', raw_body:'bytes') -> 'SMSEventList':
        payload = loads(raw_body.decode('utf8'))

        message_id = payload[_field_message_uuid]
        from_ = text_or_empty(payload.get(_body_from))
        to = text_or_empty(payload.get(_body_to))
        received_at = text_or_empty(payload.get(_field_timestamp))

        # A status callback has a status, an inbound message has its text
        if _field_status in payload:
            status = self.map_status(payload[_field_status])
            error_code = ''
            if _field_error in payload:
                error = payload[_field_error]
                error_code = text_or_empty(error.get(_field_error_type))
            event = new_status_event(message_id, from_, to, status, error_code, received_at, payload)
        else:
            body = text_or_empty(payload.get(_body_text))
            event = new_message_event(message_id, from_, to, body, received_at, payload)

        out = [event]
        return out

# ################################################################################################################################

    def callback_response(self) -> 'CallbackResponse':
        out = (OK, Content_Type_Text, '')
        return out

# ################################################################################################################################

    def build_poll_requests(self, state:'stranydict') -> 'PollRequestList':
        out = []
        headers = self._headers()

        # A listing left pages behind, so the next page of each direction is read ..
        next_links = state.get(_state_next, {})

        if next_links:
            for direction, href in next_links.items():
                out.append(PollRequest(Method_GET, href, headers, {}, direction))
            return out

        # .. otherwise each direction not yet read is listed over the current window, which is the one
        # a previous poll left unfinished, or a new one that reaches from the previous poll to now.
        date_start = state.get(_state_date_start)
        if not date_start:
            date_start = _now_text()

        date_end = state.get(_state_window_end)
        if not date_end:
            date_end = _now_text()

        done = state.get(_state_done, {})
        url = self.host + _reports_path

        for direction in _directions:

            if direction in done:
                continue

            params = {
                _param_account_id: self.username,
                _param_product: _product_sms,
                _param_direction: direction,
                _param_date_start: date_start,
                _param_date_end: date_end,
                _param_include_message: 'true',
            }
            out.append(PollRequest(Method_GET, url, headers, params, direction))

        return out

# ################################################################################################################################

    def read_poll_response(self, request:'PollRequest', response:'Response', state:'stranydict') -> 'PollResult':

        if not response.ok:
            raise ProviderError(f'Vonage report failed with {response.status_code}: {response.text}')

        payload = loads(response.text)
        events = []

        for record in payload.get(_field_records, []):
            events.append(self._event_from_record(record))

        new_state = dict(state)
        next_links = dict(new_state.get(_state_next, {}))

        links = payload.get(_field_links, {})
        if _field_next in links:
            next_links[request.tag] = links[_field_next][_field_href]
        else:
            next_links.pop(request.tag, None)

        new_state[_state_next] = next_links

        # The first page of a direction names the window it reads
        if _param_date_end in request.params:
            new_state[_state_window_end] = request.params[_param_date_end]

        # A direction without further pages is read in full over the window
        done = dict(new_state.get(_state_done, {}))
        if request.tag not in next_links:
            done[request.tag] = True
        new_state[_state_done] = done

        # Once every direction is read, the end of this window is where the next one opens
        if len(done) == len(_directions):
            new_state[_state_date_start] = new_state[_state_window_end]
            del new_state[_state_window_end]
            new_state[_state_done] = {}

        out = (events, new_state)
        return out

# ################################################################################################################################

    def _event_from_record(self, record:'anydict') -> 'SMSEvent':
        message_id = text_or_empty(record.get(_field_message_id))
        from_ = text_or_empty(record.get(_body_from))
        to = text_or_empty(record.get(_body_to))
        received_at = text_or_empty(record.get(_field_date_received))

        if record.get(_field_direction) == _direction_inbound:
            body = text_or_empty(record.get(_field_message_body))
            out = new_message_event(message_id, from_, to, body, received_at, record)
        else:
            status = self.map_status(text_or_empty(record.get(_field_status)))
            error_code = text_or_empty(record.get(_field_error_code))
            out = new_status_event(message_id, from_, to, status, error_code, received_at, record)

        return out

# ################################################################################################################################

    def has_more_pages(self, state:'stranydict') -> 'bool':
        out = bool(state.get(_state_next))
        return out

# ################################################################################################################################
# ################################################################################################################################

register_provider(VonageProvider)

# ################################################################################################################################
# ################################################################################################################################
