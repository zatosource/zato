# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Infobip - the SMS API v3 for sends under an App authorization header, JSON callbacks without a signature,
# and pull endpoints for incoming messages and delivery reports that return every item once only.

# stdlib
from http.client import OK

# Zato
from zato.common.api import SMS
from zato.common.json_internal import dumps, loads
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
_send_path = '/sms/3/messages'
_inbox_path = '/sms/1/inbox/reports'
_reports_path = '/sms/3/reports'
_balance_path = '/account/1/balance'

# The authorization scheme of an API key
_auth_prefix = 'App '

# Request body fields
_body_messages = 'messages'
_body_sender = 'sender'
_body_destinations = 'destinations'
_body_to = 'to'
_body_content = 'content'
_body_text = 'text'
_body_webhooks = 'webhooks'
_body_delivery = 'delivery'
_body_url = 'url'

# Response and callback fields
_field_messages = 'messages'
_field_results = 'results'
_field_message_id = 'messageId'
_field_status = 'status'
_field_group_name = 'groupName'
_field_error = 'error'
_field_error_name = 'name'
_field_error_group = 'groupName'
_field_from = 'from'
_field_to = 'to'
_field_text = 'text'
_field_received_at = 'receivedAt'
_field_done_at = 'doneAt'
_field_sent_at = 'sentAt'
_field_pending_count = 'pendingMessageCount'
_field_request_error = 'requestError'
_field_service_exception = 'serviceException'
_field_exception_text = 'text'

# The error group of a message without an error
_error_group_ok = 'OK'

# The pull endpoints' page size
_param_limit = 'limit'
_limit = '1000'

# The poll request tags
_tag_inbox = 'inbox'
_tag_reports = 'reports'

# Poll state keys
_state_pending_inbox = 'pending_inbox'

# ################################################################################################################################
# ################################################################################################################################

class InfobipProvider(Provider):
    name = SMS.Provider.Infobip

    # Infobip reports a status group, whose name is mapped
    status_mapping = {
        'pending': Status_Sent,
        'delivered': Status_Delivered,
        'undeliverable': Status_Failed,
        'expired': Status_Failed,
        'rejected': Status_Failed,
    }

# ################################################################################################################################

    def _headers(self) -> 'strdict':
        out = {
            'Authorization': _auth_prefix + self.password,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        return out

# ################################################################################################################################

    def build_send_request(self, to:'str', body:'str', sender:'str', callback_url:'strnone') -> 'SendRequest':

        message:'anydict' = {
            _body_sender: sender,
            _body_destinations: [{_body_to: to}],
            _body_content: {_body_text: body},
        }

        if callback_url:
            message[_body_webhooks] = {_body_delivery: {_body_url: callback_url}}

        data = {_body_messages: [message]}

        url = self.host + _send_path
        out = (Method_POST, url, self._headers(), dumps(data))

        return out

# ################################################################################################################################

    def read_send_response(self, response:'Response') -> 'SendResult':
        payload = loads(response.text)

        if not response.ok:
            text = payload.get(_field_request_error, {}).get(_field_service_exception, {}).get(_field_exception_text)
            raise ProviderError(f'Infobip error {response.status_code}: {text}')

        message = payload[_field_messages][0]

        out = SendResult()
        out.id = message[_field_message_id]
        out.status = self.map_status(message[_field_status][_field_group_name])
        out.raw = payload

        return out

# ################################################################################################################################

    def build_ping_request(self) -> 'SendRequest':
        url = self.host + _balance_path
        out = (Method_GET, url, self._headers(), None)
        return out

# ################################################################################################################################

    def read_callback(self, request_ctx:'stranydict', raw_body:'bytes') -> 'SMSEventList':
        payload = loads(raw_body.decode('utf8'))
        out = []

        for result in payload[_field_results]:
            out.append(self._event_from_result(result))

        return out

# ################################################################################################################################

    def _event_from_result(self, result:'anydict') -> 'SMSEvent':
        message_id = text_or_empty(result.get(_field_message_id))
        from_ = text_or_empty(result.get(_field_from))
        to = text_or_empty(result.get(_field_to))

        # A delivery report has a status group, an incoming message has its text
        if _field_status in result:
            status = self.map_status(result[_field_status][_field_group_name])

            error_code = ''
            if _field_error in result:
                error = result[_field_error]
                if error.get(_field_error_group) != _error_group_ok:
                    error_code = text_or_empty(error.get(_field_error_name))

            received_at = text_or_empty(result.get(_field_done_at))
            if not received_at:
                received_at = text_or_empty(result.get(_field_sent_at))

            out = new_status_event(message_id, from_, to, status, error_code, received_at, result)

        else:
            body = text_or_empty(result.get(_field_text))
            received_at = text_or_empty(result.get(_field_received_at))
            out = new_message_event(message_id, from_, to, body, received_at, result)

        return out

# ################################################################################################################################

    def callback_response(self) -> 'CallbackResponse':
        out = (OK, Content_Type_Text, '')
        return out

# ################################################################################################################################

    def build_poll_requests(self, state:'stranydict') -> 'PollRequestList':
        headers = self._headers()
        params = {_param_limit: _limit}

        inbox = PollRequest(Method_GET, self.host + _inbox_path, headers, params, _tag_inbox)

        # Messages remain in the inbox, which is read again alone ..
        if state.get(_state_pending_inbox):
            out = [inbox]
            return out

        # .. otherwise both pull endpoints are read.
        reports = PollRequest(Method_GET, self.host + _reports_path, headers, params, _tag_reports)
        out = [inbox, reports]

        return out

# ################################################################################################################################

    def read_poll_response(self, request:'PollRequest', response:'Response', state:'stranydict') -> 'PollResult':

        if not response.ok:
            raise ProviderError(f'Infobip pull failed with {response.status_code}: {response.text}')

        payload = loads(response.text)
        events = []

        for result in payload.get(_field_results, []):
            events.append(self._event_from_result(result))

        new_state = dict(state)

        if request.tag == _tag_inbox:
            pending = payload.get(_field_pending_count, 0)
            new_state[_state_pending_inbox] = pending > 0

        out = (events, new_state)
        return out

# ################################################################################################################################

    def has_more_pages(self, state:'stranydict') -> 'bool':
        out = bool(state.get(_state_pending_inbox))
        return out

# ################################################################################################################################
# ################################################################################################################################

register_provider(InfobipProvider)

# ################################################################################################################################
# ################################################################################################################################
