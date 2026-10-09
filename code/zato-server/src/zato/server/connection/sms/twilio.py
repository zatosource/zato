# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Twilio - the Programmable Messaging REST API, form-encoded requests under Basic Auth, callbacks signed
# with HMAC-SHA1 in X-Twilio-Signature and answered with an empty TwiML document.

# stdlib
from base64 import b64encode
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from hashlib import sha1
from hmac import compare_digest, new as hmac_new
from http.client import OK
from urllib.parse import parse_qsl

# Zato
from zato.common.api import SMS
from zato.common.json_internal import loads
from zato.common.sms.model import SendResult, Status_Delivered, Status_Failed, Status_Sent
from zato.server.connection.sms.base import CallbackRejected, Content_Type_XML, Ctx_Headers, Method_GET, Method_POST, \
    new_message_event, new_status_event, PollRequest, Provider, ProviderError, register_provider, text_or_empty

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from requests import Response
    from zato.common.sms.model import SMSEvent
    from zato.common.typing_ import anydict, stranydict, strdict, strnone
    from zato.server.connection.sms.base import CallbackResponse, PollRequestList, PollResult, SendRequest, SMSEventList

# ################################################################################################################################
# ################################################################################################################################

# The API version every path opens with
_api_version = '2010-04-01'

# The prefix of a Messaging Service SID, sent as MessagingServiceSid instead of From
_messaging_service_prefix = 'MG'

# Request parameters
_param_to = 'To'
_param_from = 'From'
_param_body = 'Body'
_param_messaging_service_sid = 'MessagingServiceSid'
_param_status_callback = 'StatusCallback'
_param_date_sent_after = 'DateSent>'
_param_page_size = 'PageSize'

# The page size of a poll's message listing
_page_size = 1000

# Callback parameters
_callback_message_sid = 'MessageSid'
_callback_message_status = 'MessageStatus'
_callback_error_code = 'ErrorCode'
_callback_from = 'From'
_callback_to = 'To'
_callback_body = 'Body'

# Response fields
_field_sid = 'sid'
_field_status = 'status'
_field_direction = 'direction'
_field_from = 'from'
_field_to = 'to'
_field_body = 'body'
_field_date_sent = 'date_sent'
_field_date_created = 'date_created'
_field_error_code = 'error_code'
_field_messages = 'messages'
_field_next_page_uri = 'next_page_uri'
_field_message = 'message'
_field_code = 'code'

# The direction of an incoming text in a message listing
_direction_inbound = 'inbound'

# The signature header
_header_signature = 'x-twilio-signature'

# Poll state keys
_state_date_sent = 'date_sent'
_state_next_page_uri = 'next_page_uri'

# The response to an accepted callback
_callback_body_xml = '<?xml version="1.0" encoding="UTF-8"?><Response/>'

# The date format of the DateSent filter and the length of a date in that format
_date_filter_format = '%Y-%m-%d'
_date_length = 10

# ################################################################################################################################
# ################################################################################################################################

def _to_iso_8601(value:'str') -> 'str':
    """ Converts an RFC 2822 timestamp to ISO-8601. An empty value is returned unchanged.
    """
    if not value:
        return ''

    out = parsedate_to_datetime(value).isoformat()
    return out

# ################################################################################################################################

def _parse_form(raw_body:'bytes') -> 'strdict':
    out = dict(parse_qsl(raw_body.decode('utf8'), keep_blank_values=True))
    return out

# ################################################################################################################################

def compute_signature(auth_token:'str', url:'str', params:'strdict') -> 'str':
    """ The X-Twilio-Signature value of one callback - Base64 of HMAC-SHA1 over the URL followed by every
    parameter name and value in name order.
    """
    data = url

    for name in sorted(params):
        data += name + params[name]

    digest = hmac_new(auth_token.encode('utf8'), data.encode('utf8'), sha1).digest()
    out = b64encode(digest).decode('ascii')

    return out

# ################################################################################################################################
# ################################################################################################################################

class TwilioProvider(Provider):
    name = SMS.Provider.Twilio

    status_mapping = {
        'accepted': Status_Sent,
        'scheduled': Status_Sent,
        'queued': Status_Sent,
        'sending': Status_Sent,
        'sent': Status_Sent,
        'delivered': Status_Delivered,
        'read': Status_Delivered,
        'undelivered': Status_Failed,
        'failed': Status_Failed,
        'canceled': Status_Failed,
    }

# ################################################################################################################################

    def _account_url(self, suffix:'str') -> 'str':
        out = f'{self.host}/{_api_version}/Accounts/{self.username}{suffix}'
        return out

# ################################################################################################################################

    def _headers(self) -> 'strdict':
        credentials = f'{self.username}:{self.password}'.encode('utf8')
        out = {'Authorization': 'Basic ' + b64encode(credentials).decode('ascii')}
        return out

# ################################################################################################################################

    def build_send_request(self, to:'str', body:'str', sender:'str', callback_url:'strnone') -> 'SendRequest':

        data = {
            _param_to: to,
            _param_body: body,
        }

        if sender.startswith(_messaging_service_prefix):
            data[_param_messaging_service_sid] = sender
        else:
            data[_param_from] = sender

        if callback_url:
            data[_param_status_callback] = callback_url

        url = self._account_url('/Messages.json')
        out = (Method_POST, url, self._headers(), data)

        return out

# ################################################################################################################################

    def read_send_response(self, response:'Response') -> 'SendResult':
        payload = loads(response.text)

        if not response.ok:
            code = payload.get(_field_code)
            message = payload.get(_field_message)
            raise ProviderError(f'Twilio error {code}: {message}')

        out = SendResult()
        out.id = payload[_field_sid]
        out.status = self.map_status(payload[_field_status])
        out.raw = payload

        return out

# ################################################################################################################################

    def build_ping_request(self) -> 'SendRequest':
        url = self._account_url('.json')
        out = (Method_GET, url, self._headers(), None)
        return out

# ################################################################################################################################

    def verify_callback(self, request_ctx:'stranydict', raw_body:'bytes', url:'str') -> 'None':
        headers = request_ctx[Ctx_Headers]

        if _header_signature not in headers:
            raise CallbackRejected('Twilio callback has no signature')

        given = headers[_header_signature]
        expected = compute_signature(self.password, url, _parse_form(raw_body))

        if not compare_digest(given, expected):
            raise CallbackRejected('Twilio callback signature does not verify')

# ################################################################################################################################

    def read_callback(self, request_ctx:'stranydict', raw_body:'bytes') -> 'SMSEventList':
        params = _parse_form(raw_body)
        received_at = datetime.now(timezone.utc).isoformat()

        message_id = params[_callback_message_sid]
        from_ = text_or_empty(params.get(_callback_from))
        to = text_or_empty(params.get(_callback_to))

        # A status callback has the message's status, an incoming text has its body
        if _callback_message_status in params:
            status = self.map_status(params[_callback_message_status])
            error_code = text_or_empty(params.get(_callback_error_code))
            event = new_status_event(message_id, from_, to, status, error_code, received_at, params)
        else:
            body = text_or_empty(params.get(_callback_body))
            event = new_message_event(message_id, from_, to, body, received_at, params)

        out = [event]
        return out

# ################################################################################################################################

    def callback_response(self) -> 'CallbackResponse':
        out = (OK, Content_Type_XML, _callback_body_xml)
        return out

# ################################################################################################################################

    def build_poll_requests(self, state:'stranydict') -> 'PollRequestList':

        # The previous poll recorded a next page, which is read first ..
        if state.get(_state_next_page_uri):
            url = self.host + state[_state_next_page_uri]
            request = PollRequest(Method_GET, url, self._headers(), {})

        # .. otherwise a new listing starts at the date the previous poll recorded, or today for the first poll.
        else:
            date_sent = state.get(_state_date_sent)
            if not date_sent:
                date_sent = datetime.now(timezone.utc).strftime(_date_filter_format)

            params = {
                _param_date_sent_after: date_sent,
                _param_page_size: str(_page_size),
            }
            url = self._account_url('/Messages.json')
            request = PollRequest(Method_GET, url, self._headers(), params)

        out = [request]
        return out

# ################################################################################################################################

    def read_poll_response(self, request:'PollRequest', response:'Response', state:'stranydict') -> 'PollResult':

        if not response.ok:
            raise ProviderError(f'Twilio listing failed with {response.status_code}: {response.text}')

        payload = loads(response.text)
        events = []

        latest_date = state.get(_state_date_sent, '')

        for item in payload[_field_messages]:
            event = self._event_from_listing(item)
            events.append(event)

            # The date of the newest message is the start of the next listing
            if event.received_at:
                item_date = event.received_at[:_date_length]
                if item_date > latest_date:
                    latest_date = item_date

        new_state = dict(state)
        new_state[_state_date_sent] = latest_date
        new_state[_state_next_page_uri] = text_or_empty(payload.get(_field_next_page_uri))

        out = (events, new_state)
        return out

# ################################################################################################################################

    def _event_from_listing(self, item:'anydict') -> 'SMSEvent':
        message_id = item[_field_sid]
        from_ = text_or_empty(item.get(_field_from))
        to = text_or_empty(item.get(_field_to))

        date_sent = text_or_empty(item.get(_field_date_sent))
        if not date_sent:
            date_sent = text_or_empty(item.get(_field_date_created))
        received_at = _to_iso_8601(date_sent)

        if item.get(_field_direction) == _direction_inbound:
            body = text_or_empty(item.get(_field_body))
            out = new_message_event(message_id, from_, to, body, received_at, item)
        else:
            status = self.map_status(text_or_empty(item.get(_field_status)))
            error_code = text_or_empty(item.get(_field_error_code))
            out = new_status_event(message_id, from_, to, status, error_code, received_at, item)

        return out

# ################################################################################################################################

    def has_more_pages(self, state:'stranydict') -> 'bool':
        out = bool(state.get(_state_next_page_uri))
        return out

# ################################################################################################################################
# ################################################################################################################################

register_provider(TwilioProvider)

# ################################################################################################################################
# ################################################################################################################################
