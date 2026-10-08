# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What SMS channels tell the shared scenarios about themselves - each call is a simulated Twilio callback
# of an incoming text whose body is the document the scenario sends.

# stdlib
import os
from json import dumps, loads

# Zato
from zato.common.api import SMS
from zato.common.audit_log.api import AuditSource
from zato.common.pubsub.outgoing import InboundType
from zato.common.util.mcp_oauth import Server_Address_Env_Key

# Test support
from live_sms.base import form_encode
from live_sms.suite import SimulatorSuite
from live_sms.twilio import compute_signature, Magic_From_Valid, new_message_sid
from queue_delivery.channel.client import channel_url, post
from queue_delivery.channel.type_under_test import ChannelTypeUnderTest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strdict
    from queue_delivery.channel.client import ChannelResponse

# ################################################################################################################################
# ################################################################################################################################

_directory = os.path.dirname(__file__)

# The channels of the enmasse template, by key
Channels = {
    'plain':         'test.queue-delivery.sms.plain',
    'orders':        'test.queue-delivery.sms.orders',
    'no_retries':    'test.queue-delivery.sms.no-retries',
    'dlq_keep':      'test.queue-delivery.sms.dlq-keep',
    'no_dlq':        'test.queue-delivery.sms.no-dlq',
    'dlq_retry':     'test.queue-delivery.sms.dlq-retry',
    'dlq_forward':   'test.queue-delivery.sms.dlq-forward',
    'dlq_discard':   'test.queue-delivery.sms.dlq-discard',
    'static':        'test.queue-delivery.sms.static',
    'static_xml':    'test.queue-delivery.sms.static-xml',
    'static_text':   'test.queue-delivery.sms.static-text',
    'hooked':        'test.queue-delivery.sms.hooked',
    'hooked_static': 'test.queue-delivery.sms.hooked-static',
    'slow_hook':     'test.queue-delivery.sms.slow-hook',
    'counting':      'test.queue-delivery.sms.counting',
}

# The webhook path of each channel - the one path the internal REST channel serves, with the channel's name after it
URL_Paths = {}
for _key, _name in Channels.items():
    URL_Paths[_key] = SMS.Webhook_Path_Prefix + _name

# The service each channel's queued requests go to, as the delivery page shows it
_target_service = 'test.queue-delivery.channel.target'
_hooked_service = 'test.queue-delivery.channel.hooked'

Services = {
    'plain':         _target_service,
    'orders':        _target_service,
    'no_retries':    _target_service,
    'dlq_keep':      _target_service,
    'no_dlq':        _target_service,
    'dlq_retry':     _target_service,
    'dlq_forward':   _target_service,
    'dlq_discard':   _target_service,
    'static':        _target_service,
    'static_xml':    _target_service,
    'static_text':   _target_service,
    'hooked':        _hooked_service,
    'hooked_static': _hooked_service,
    'slow_hook':     'test.queue-delivery.channel.slow-hook',
    'counting':      'test.queue-delivery.channel.counting',
}

Request_Method = 'POST'

# The server builds each channel's webhook URL from this address and Twilio signs its callbacks over that URL -
# the server's port is settled only once it starts, so the address is a fixed one and the simulator signs over it
# while posting to the port the server listens on
Signing_Address = 'http://sms-channel-suite.zato.test'

# The numbers of a simulated incoming text
From_Number = '+12025550102'
To_Number = Magic_From_Valid

# What Twilio answers an accepted callback with
_content_type_xml = 'text/xml'

# ################################################################################################################################
# ################################################################################################################################

class SMSChannelType(ChannelTypeUnderTest):
    """ SMS channels under test.
    """

    conn_type = InboundType.SMS
    audit_source = AuditSource.SMS_Channel
    suite_name = 'channel_sms'

    connections = Channels
    url_paths = URL_Paths

    template_path = os.path.join(_directory, '_enmasse_template.yaml')
    services_source = os.path.join(_directory, '_services.py')

    static_content_types:'strdict' = {}

    ack_content_type = _content_type_xml
    request_method = Request_Method
    services = Services
    enmasse_section = 'channel_sms'

    server_environment = {
        Server_Address_Env_Key: Signing_Address,
    }

    def __init__(self) -> 'None':

        # The Twilio simulator every channel's connection points to - the session fixture starts it before the server
        self.simulators = SimulatorSuite()
        self.twilio = self.simulators.twilio

# ################################################################################################################################

    def path_params_of(self, order_id:'str') -> 'anydict':
        out:'anydict' = {}
        return out

# ################################################################################################################################

    def signing_url(self, key:'str') -> 'str':
        """ The URL the server believes a channel's webhook has, which is what a callback's signature is computed over.
        """
        out = Signing_Address + self.url_paths[key]
        return out

# ################################################################################################################################

    def call(self, key:'str', document:'anydict', headers:'strdict | None'=None, params:'strdict | None'=None) -> 'ChannelResponse':
        """ Posts one simulated Twilio callback of an incoming text whose body is the document, signed the way Twilio signs.
        """
        callback = {
            'MessageSid': new_message_sid(),
            'AccountSid': self.twilio.username,
            'From': From_Number,
            'To': To_Number,
            'Body': dumps(document),
            'NumMedia': '0',
        }

        signature = compute_signature(self.twilio.password, self.signing_url(key), callback)

        request_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Twilio-Signature': signature,
        }

        if headers:
            request_headers.update(headers)

        out = post(channel_url(key, params), form_encode(callback), request_headers)
        return out

# ################################################################################################################################

    def read_ack(self, response:'ChannelResponse') -> 'anydict':
        """ The acknowledgement of a callback is Twilio's empty TwiML, the correlation ID is in a response header.
        """
        cid = ''
        wanted = SMS.Header_Callback_CID.lower()

        for name, value in response.headers.items():
            if name.lower() == wanted:
                cid = value
                break

        out = {
            'is_ok': bool(cid),
            'cid': cid,
        }

        return out

# ################################################################################################################################

    def read_hook_response(self, response:'ChannelResponse') -> 'str':
        out = response.text
        return out

# ################################################################################################################################

    def read_plain_response(self, response:'ChannelResponse') -> 'anydict':
        out = {'text': response.text}
        return out

# ################################################################################################################################

    def body_of_envelope_data(self, data:'any_') -> 'anydict':
        """ The envelope holds the event as JSON, the event's body is the document a call sent.
        """
        event = loads(data)
        out = loads(event['body'])
        return out

# ################################################################################################################################

    def check_received_request(self, received:'anydict', key:'str', document:'anydict') -> 'None':
        assert received['payload'] == document, received
        assert received['channel_name'] == Channels[key], received

# ################################################################################################################################

    def check_destination(self, key:'str', destination:'str') -> 'None':
        assert destination == Services[key], destination

# ################################################################################################################################
# ################################################################################################################################

sms_channel_type = SMSChannelType()

# ################################################################################################################################
# ################################################################################################################################
