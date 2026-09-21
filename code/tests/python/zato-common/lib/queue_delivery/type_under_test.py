# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What one type of outgoing connection tells the shared harness about itself, and what the harness knows about the
# environment it built for the type's suite.

# stdlib
from json import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strdict
    from queue_delivery.backends import Backend
    from queue_delivery.receiver import RecordedRequest, RecordingReceiver

# ################################################################################################################################
# ################################################################################################################################

# The connections every type's template declares, by key - the same settings behind each key in every template,
# which is what lets one set of scenarios run through every type

# The switch off - a send goes to the wire the way it always did
Conn_Plain = 'plain'

# The switch on, two retries a second apart, no DLQ - the connection most scenarios send through
Conn_Orders = 'orders'

# The switch on and no retries at all
Conn_No_Retries = 'no_retries'

# The switch on, one retry, the DLQ on with the rule leaving messages alone
Conn_DLQ_Keep = 'dlq_keep'

# The switch on, one retry, the DLQ off
Conn_No_DLQ = 'no_dlq'

# The DLQ rule puts a message back into the queue twice, a second apart
Conn_DLQ_Retry = 'dlq_retry'

# The DLQ rule forwards a message to Forward_Topic, with its header
Conn_DLQ_Forward = 'dlq_forward'

# The DLQ rule discards a message
Conn_DLQ_Discard = 'dlq_discard'

Connection_Keys = (
    Conn_Plain,
    Conn_Orders,
    Conn_No_Retries,
    Conn_DLQ_Keep,
    Conn_No_DLQ,
    Conn_DLQ_Retry,
    Conn_DLQ_Forward,
    Conn_DLQ_Discard,
)

# The connection whose switch is off has no queue and no topic in a broker
Conn_Without_Queue = Conn_Plain

# The topic the forwarding connection's DLQ messages are published to
Forward_Topic = 'test.queue-delivery.forwarded'

# What every template gives its connections
Orders_Max_Retries = 2
Orders_Sleep_Time = 1
Orders_Backoff_Threshold = 10
Orders_Backoff_Multiplier = 1

DLQ_Conn_Max_Retries = 1
DLQ_Conn_Sleep_Time = 1

DLQ_Retry_Conn_Rounds = 2
DLQ_Retry_Interval = 1

# The direct attempt and the one retry of a DLQ connection
Attempts_Per_Round = DLQ_Conn_Max_Retries + 1

# ################################################################################################################################
# ################################################################################################################################

class TypeUnderTest:
    """ One type of outgoing connection as the shared harness and scenarios see it.
    """

    # The OutgoingType the type registers under
    conn_type = ''

    # The short name of the suite - in logger names, container names, temporary directories and log files
    suite_name = ''

    # The connection names of the type's template, by the keys of Connection_Keys
    connections:'strdict' = {}

    # The type's enmasse template with the port placeholders of its receivers
    template_path = ''

    # The type's own services, copied to the server's pickup directory along with the shared ones
    services_source = ''

    # The receiver class of the type, constructed with a port
    receiver_class:'type[RecordingReceiver]' = None # type: ignore[assignment]

    # What a send's error starts with when the endpoint refuses the message
    refused_error_prefix = ''

    # What a send's error carries when nothing listens on the endpoint's port
    down_error_text = ''

# ################################################################################################################################

    def body_of(self, request:'RecordedRequest') -> 'any_':
        """ The document a recorded request carried, comparable to what a scenario sent.
        """
        out = loads(request.body)
        return out

# ################################################################################################################################

    def body_of_envelope_data(self, data:'any_') -> 'any_':
        """ The document the data part of a queued envelope holds, comparable to what a scenario sent.
        """
        out = loads(data)
        return out

# ################################################################################################################################

    def envelope_data_of(self, document:'any_') -> 'str':
        """ A document as the data part of a queued envelope carries it - what an edit of a message writes.
        """
        out = dumps(document)
        return out

# ################################################################################################################################

    def check_envelope_request(self, request_part:'anydict', data:'any_') -> 'None':
        """ Checks the request part of a queued envelope holds what was sent, in the type's own terms.
        """
        raise NotImplementedError()

# ################################################################################################################################

    def check_destination(self, conn_key:'str', destination:'str') -> 'None':
        """ Checks the destination the delivery page shows for a message of a connection.
        """
        raise NotImplementedError()

# ################################################################################################################################
# ################################################################################################################################

class TestConfig:
    """ What the tests need to know about the environment the session fixture built for them.
    """

    type_under_test:'TypeUnderTest' = None # type: ignore[assignment]

    base_url = ''
    password = ''

    server_directory = ''
    server_port = 0
    zato_bin = ''

    backend:'Backend' = None # type: ignore[assignment]

    # The endpoints, by the keys of Connection_Keys
    receivers:'dict[str, RecordingReceiver]' = {}

    state:'any_' = None

# ################################################################################################################################
# ################################################################################################################################
