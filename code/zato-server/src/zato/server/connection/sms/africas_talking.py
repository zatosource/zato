# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Africa's Talking - form-encoded sends under an apiKey header, form-encoded callbacks without a signature
# answered with the text OK, and a pull endpoint for incoming texts keyed by the last message ID received.

# stdlib
from datetime import datetime, timezone
from http.client import OK
from urllib.parse import parse_qsl

# Zato
from zato.common.api import SMS
from zato.common.json_internal import loads
from zato.common.sms.model import SendResult, Status_Delivered, Status_Failed, Status_Sent
from zato.server.connection.sms.base import Content_Type_Text, Method_GET, Method_POST, new_message_event, \
    new_status_event, PollRequest, Provider, ProviderError, register_provider, text_or_empty

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from requests import Response
    from zato.common.sms.model import SMSEvent
    from zato.common.typing_ import anydict, stranydict, strdict, strnone
    from zato.server.connection.sms.base import CallbackResponse, PollRequestList, PollResult, SendRequest, SMSEventList

# ################################################################################################################################
# ################################################################################################################################

# API paths
_messaging_path = '/version1/messaging'
_user_path = '/version1/user'

# The API key header
_header_api_key = 'apiKey'

# Request parameters
_param_username = 'username'
_param_to = 'to'
_param_message = 'message'
_param_from = 'from'
_param_last_received_id = 'lastReceivedId'

# Response fields
_field_sms_message_data = 'SMSMessageData'
_field_recipients = 'Recipients'
_field_messages = 'Messages'
_field_message_id = 'messageId'
_field_status = 'status'
_field_status_code = 'statusCode'
_field_number = 'number'

# Callback and pull fields
_field_id = 'id'
_field_from = 'from'
_field_to = 'to'
_field_text = 'text'
_field_date = 'date'
_field_phone_number = 'phoneNumber'
_field_failure_reason = 'failureReason'

# The highest status code of an accepted recipient
_status_code_accepted_max = 102

# Poll state keys
_state_last_received_id = 'last_received_id'
_first_received_id = 0

# The response to an accepted callback
_callback_body_ok = 'OK'

# ################################################################################################################################
# ################################################################################################################################

def _parse_form(raw_body:'bytes') -> 'strdict':
    out = dict(parse_qsl(raw_body.decode('utf8'), keep_blank_values=True))
    return out

# ################################################################################################################################
# ################################################################################################################################

class AfricasTalkingProvider(Provider):
    name = SMS.Provider.Africas_Talking

    status_mapping = {
        'processed': Status_Sent,
        'sent': Status_Sent,
        'queued': Status_Sent,
        'submitted': Status_Sent,
        'buffered': Status_Sent,
        'success': Status_Delivered,
        'failed': Status_Failed,
        'rejected': Status_Failed,
    }

# ################################################################################################################################

    def _headers(self) -> 'strdict':
        out = {
            _header_api_key: self.password,
            'Accept': 'application/json',
        }
        return out

# ################################################################################################################################

    def build_send_request(self, to:'str', body:'str', sender:'str', callback_url:'strnone') -> 'SendRequest':

        data = {
            _param_username: self.username,
            _param_to: to,
            _param_message: body,
        }

        if sender:
            data[_param_from] = sender

        url = self.host + _messaging_path
        out = (Method_POST, url, self._headers(), data)

        return out

# ################################################################################################################################

    def read_send_response(self, response:'Response') -> 'SendResult':

        if not response.ok:
            raise ProviderError(f"Africa's Talking error {response.status_code}: {response.text}")

        payload = loads(response.text)
        recipients = payload[_field_sms_message_data][_field_recipients]

        if not recipients:
            message = payload[_field_sms_message_data].get('Message')
            raise ProviderError(f"Africa's Talking accepted no recipient: {message}")

        recipient = recipients[0]
        status_code = recipient[_field_status_code]

        if status_code > _status_code_accepted_max:
            raise ProviderError(f"Africa's Talking rejected the recipient with {status_code}: {recipient[_field_status]}")

        out = SendResult()
        out.id = recipient[_field_message_id]
        out.status = self.map_status(recipient[_field_status])
        out.raw = payload

        return out

# ################################################################################################################################

    def build_ping_request(self) -> 'SendRequest':
        params = {_param_username: self.username}
        url = self.host + _user_path
        out = (Method_GET, url, self._headers(), params)
        return out

# ################################################################################################################################

    def read_callback(self, request_ctx:'stranydict', raw_body:'bytes') -> 'SMSEventList':
        params = _parse_form(raw_body)
        message_id = text_or_empty(params.get(_field_id))

        # A delivery report has a status, an incoming text has its text
        if _field_status in params:
            status = self.map_status(params[_field_status])
            error_code = text_or_empty(params.get(_field_failure_reason))
            to = text_or_empty(params.get(_field_phone_number))
            received_at = datetime.now(timezone.utc).isoformat()
            event = new_status_event(message_id, self.sender, to, status, error_code, received_at, params)
        else:
            event = self._message_event(params)

        out = [event]
        return out

# ################################################################################################################################

    def _message_event(self, item:'anydict') -> 'SMSEvent':
        message_id = text_or_empty(item.get(_field_id))
        from_ = text_or_empty(item.get(_field_from))
        to = text_or_empty(item.get(_field_to))
        body = text_or_empty(item.get(_field_text))
        received_at = text_or_empty(item.get(_field_date))

        out = new_message_event(message_id, from_, to, body, received_at, item)
        return out

# ################################################################################################################################

    def callback_response(self) -> 'CallbackResponse':
        out = (OK, Content_Type_Text, _callback_body_ok)
        return out

# ################################################################################################################################

    def build_poll_requests(self, state:'stranydict') -> 'PollRequestList':
        last_received_id = state.get(_state_last_received_id, _first_received_id)

        params = {
            _param_username: self.username,
            _param_last_received_id: str(last_received_id),
        }

        url = self.host + _messaging_path
        out = [PollRequest(Method_GET, url, self._headers(), params)]

        return out

# ################################################################################################################################

    def read_poll_response(self, request:'PollRequest', response:'Response', state:'stranydict') -> 'PollResult':

        if not response.ok:
            raise ProviderError(f"Africa's Talking fetch failed with {response.status_code}: {response.text}")

        payload = loads(response.text)
        events = []

        last_received_id = state.get(_state_last_received_id, _first_received_id)

        for item in payload[_field_sms_message_data][_field_messages]:
            events.append(self._message_event(item))

            # The next fetch starts after the highest ID read
            item_id = int(item[_field_id])
            if item_id > last_received_id:
                last_received_id = item_id

        new_state = dict(state)
        new_state[_state_last_received_id] = last_received_id

        out = (events, new_state)
        return out

# ################################################################################################################################
# ################################################################################################################################

register_provider(AfricasTalkingProvider)

# ################################################################################################################################
# ################################################################################################################################
