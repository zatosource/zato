# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What one transport of channels tells the shared scenarios about itself - how its channels are called, how an
# acknowledgement reads and what the service behind them recorded.

# stdlib
from http.client import OK
from http.client import responses as http_responses

# Zato
from zato.common.typing_ import cast_

# Test support
from queue_delivery.type_under_test import TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strdict
    from queue_delivery.channel.client import ChannelResponse

# ################################################################################################################################
# ################################################################################################################################

# The channels every transport's template declares, by key - the same settings behind each key in both templates,
# which is what lets one set of scenarios run through both transports

# The switch off - the service runs as the request arrives and its own response goes back
Channel_Plain = 'plain'

# The switch on, two retries a second apart, no DLQ - the channel most scenarios call
Channel_Orders = 'orders'

# The switch on and no retries at all
Channel_No_Retries = 'no_retries'

# The switch on, one retry, the DLQ on with the rule leaving messages alone
Channel_DLQ_Keep = 'dlq_keep'

# The switch on, one retry, the DLQ off
Channel_No_DLQ = 'no_dlq'

# The DLQ rule puts a message back into the queue twice, a second apart
Channel_DLQ_Retry = 'dlq_retry'

# The DLQ rule forwards a message to Forward_Topic, with its header
Channel_DLQ_Forward = 'dlq_forward'

# The DLQ rule discards a message
Channel_DLQ_Discard = 'dlq_discard'

# A static queue response that is a JSON document
Channel_Static = 'static'

# A static queue response that is an XML document
Channel_Static_XML = 'static_xml'

# A static queue response that is plain text
Channel_Static_Text = 'static_text'

# The service overrides get_queue_response
Channel_Hooked = 'hooked'

# The service overrides get_queue_response and the channel has a static response too
Channel_Hooked_Static = 'hooked_static'

# The service's hook sleeps before it answers
Channel_Slow_Hook = 'slow_hook'

# The service counts its instantiations
Channel_Counting = 'counting'

Channel_Keys = (
    Channel_Plain,
    Channel_Orders,
    Channel_No_Retries,
    Channel_DLQ_Keep,
    Channel_No_DLQ,
    Channel_DLQ_Retry,
    Channel_DLQ_Forward,
    Channel_DLQ_Discard,
    Channel_Static,
    Channel_Static_XML,
    Channel_Static_Text,
    Channel_Hooked,
    Channel_Hooked_Static,
    Channel_Slow_Hook,
    Channel_Counting,
)

# The channel whose switch is off has no queue
Channel_Without_Queue = Channel_Plain

# The topic the forwarding channel's DLQ messages are published to
Forward_Topic = 'test.queue-delivery.forwarded'

# What every template gives its channels
Orders_Max_Retries = 2
Orders_Sleep_Time = 1

DLQ_Channel_Max_Retries = 1
DLQ_Channel_Sleep_Time = 1

DLQ_Retry_Channel_Rounds = 2
DLQ_Retry_Interval = 1

# The direct attempt and the one retry of a DLQ channel
Attempts_Per_Round = DLQ_Channel_Max_Retries + 1

# The static responses the templates give their channels, verbatim
Static_Response_JSON = '{"accepted": true, "source": "static"}'
Static_Response_XML = '<ack><accepted>true</accepted></ack>'
Static_Response_Text = 'ACCEPTED'

# How long the slow hook sleeps before it answers
Slow_Hook_Delay = 2.0

# What the hooked services put in front of the message id they answer with
Hook_Response_Prefix = 'hooked:'

# The error the target raises while it refuses, which the DLQ header and the delivery page quote
Refused_Error_Text = 'The target refuses this invocation'

# The status a channel's audit event records for an acknowledgement
Ack_Status = f'{OK} {http_responses[OK]}'

# How long a run of fifty requests may take to arrive once the target accepts them
Intake_Timeout = 90.0

# ################################################################################################################################
# ################################################################################################################################

class ChannelTypeUnderTest:
    """ One transport of channels as the shared scenarios see it. The shared client helpers read it through TestConfig
    the same as they read a type of outgoing connection, which is why the channels are its connections.
    """

    # The InboundType the transport's channels queue under
    conn_type = ''

    # The short name of the suite - in logger names, container names, temporary directories and log files
    suite_name = ''

    # The channel names of the transport's template, by the keys of Channel_Keys
    connections:'strdict' = {}

    # The URL path of each channel, by the same keys
    url_paths:'strdict' = {}

    # The keys of the channels that have no queue, so no topic in a broker either
    keys_without_queue = (Channel_Without_Queue,)

    # The server needs nothing in its environment beyond what every server gets
    server_environment:'strdict' = {}

    # The transport's enmasse template
    template_path = ''

    # The transport's own services, copied to the server's pickup directory along with the shared ones
    services_source = ''

    # The audit source the transport's channels write under
    audit_source = ''

    # The Content-Type each static response leaves with, by the channel's key
    static_content_types:'strdict' = {}

    # The Content-Type the default acknowledgement leaves with
    ack_content_type = ''

    # The HTTP method every call uses
    request_method = 'POST'

    # The status the channel's audit event records for an acknowledgement
    ack_status = Ack_Status

    # How long the intake scenario waits for its run of requests to arrive once the target accepts
    intake_timeout = Intake_Timeout

    # The service each channel's queued requests go to, by the channel's key
    services:'strdict' = {}

    # The section of an enmasse file the transport's channels are under
    enmasse_section = ''

# ################################################################################################################################

    def service_of(self, key:'str') -> 'str':
        """ The name of the service behind a channel.
        """
        out = self.services[key]
        return out

# ################################################################################################################################

    def path_params_of(self, order_id:'str') -> 'anydict':
        """ The path parameters a call with that order id gives the service - a transport whose paths carry none gives none.
        """
        raise NotImplementedError()

# ################################################################################################################################

    def call(self, key:'str', document:'anydict', headers:'strdict | None'=None, params:'strdict | None'=None) -> 'ChannelResponse':
        """ Calls a channel with a document, the way a client of the transport does.
        """
        raise NotImplementedError()

# ################################################################################################################################

    def read_ack(self, response:'ChannelResponse') -> 'anydict':
        """ The acknowledgement a response carries, as a dict with is_ok and cid.
        """
        raise NotImplementedError()

# ################################################################################################################################

    def read_hook_response(self, response:'ChannelResponse') -> 'str':
        """ The text a hooked service answered with.
        """
        raise NotImplementedError()

# ################################################################################################################################

    def is_hook_response(self, response:'ChannelResponse') -> 'bool':
        """ Whether a response is the one a hooked service builds rather than the default acknowledgement - a hook's
        response names the message id behind the prefix whatever its shape, an acknowledgement never does.
        """
        out = Hook_Response_Prefix in response.text
        return out

# ################################################################################################################################

    def read_plain_response(self, response:'ChannelResponse') -> 'anydict':
        """ The document the target answers with when its channel's switch is off.
        """
        raise NotImplementedError()

# ################################################################################################################################

    def body_of_envelope_data(self, data:'any_') -> 'anydict':
        """ The document the data part of a queued envelope holds, comparable to what a scenario sent.
        """
        raise NotImplementedError()

# ################################################################################################################################

    def check_received_request(self, received:'anydict', key:'str', document:'anydict') -> 'None':
        """ Checks what the target recorded of a request in the transport's own terms - the body and the headers.
        """
        raise NotImplementedError()

# ################################################################################################################################

    def check_destination(self, key:'str', destination:'str') -> 'None':
        """ Checks the destination the delivery page shows for a message of a channel.
        """
        raise NotImplementedError()

# ################################################################################################################################
# ################################################################################################################################

def get_type_under_test() -> 'ChannelTypeUnderTest':
    """ The transport under test, as the session fixture pointed TestConfig at it.
    """
    out = cast_('ChannelTypeUnderTest', TestConfig.type_under_test)
    return out

# ################################################################################################################################
# ################################################################################################################################
