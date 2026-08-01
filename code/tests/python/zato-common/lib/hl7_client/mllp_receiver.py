# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ssl
import threading
import time
from typing import NamedTuple

# hl7apy
from hl7apy.mllp import AbstractErrorHandler, AbstractHandler, MLLPServer

# Zato
from hl7_client.ports import find_free_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The message types this receiver answers, in both the two-component form python senders write
# MSH-9 in and the three-component form HAPI writes it in
_Handled_Message_Types = (
    'ADT^A01',
    'ADT^A01^ADT_A01',
    'ORU^R01',
    'ORU^R01^ORU_R01',
    'ORM^O01',
    'ORM^O01^ORM_O01',
)

# What every listener here binds to
_Host = '127.0.0.1'

# What the receiver keeps its deliveries in
delivery_list = list['ReceivedDelivery']

# ################################################################################################################################
# ################################################################################################################################

class ReceivedDelivery(NamedTuple):
    """ One message as this receiver saw it - the text itself, when it arrived and when the
    receiver finished with it, which for a slow receiver is later than the arrival.
    """
    text: 'str'
    arrived_at: 'float'
    completed_at: 'float'

# ################################################################################################################################
# ################################################################################################################################

def _get_msh_field(message:'str', field_index:'int') -> 'str':
    """ Returns one field of the first MSH line of an HL7 message.
    """
    lines = message.split('\r')
    msh_line = lines[0]
    fields = msh_line.split('|')

    out = fields[field_index]
    return out

# ################################################################################################################################

def _build_ack(message:'str', ack_note:'str', ack_code:'str'='AA') -> 'str':
    """ Builds the acknowledgment this receiver answers one message with - the code it was started
    with, echoing the message's own control id, with the receiver's note in MSA-3 where it has one.
    The reply goes onto the wire exactly as a handler returns it, so it carries its own MLLP frame.
    """
    control_id = _get_msh_field(message, 9)

    ack_msh = 'MSH|^~\\&|MLLP_RECEIVER|RECEIVER_FACILITY|ZATO|ZATO|20260731120000||ACK|' + control_id + '|P|2.5'
    ack_msa = f'MSA|{ack_code}|{control_id}'

    if ack_note:
        ack_msa = ack_msa + '|' + ack_note

    ack = ack_msh + '\r' + ack_msa

    out = '\x0b' + ack + '\x1c\x0d'
    return out

# ################################################################################################################################
# ################################################################################################################################

class _RecordingHandler(AbstractHandler):
    """ Records one message and answers it, sleeping first for as long as the receiver
    is configured to take.
    """

    def __init__(self, message:'str', receiver:'MLLPReceiver') -> 'None':
        super().__init__(message)
        self.receiver = receiver

    def reply(self) -> 'str':

        arrived_at = time.monotonic()

        # A slow receiver takes its time before answering
        if self.receiver.delay:
            time.sleep(self.receiver.delay)

        completed_at = time.monotonic()

        delivery = ReceivedDelivery(self.incoming_message, arrived_at, completed_at)
        self.receiver.deliveries.append(delivery)

        out = _build_ack(self.incoming_message, self.receiver.ack_note, self.receiver.ack_code)
        return out

# ################################################################################################################################
# ################################################################################################################################

class _UnexpectedMessageHandler(AbstractErrorHandler):
    """ Records a message of a type this receiver does not answer, so a test reads what
    arrived rather than only seeing a closed connection.
    """

    def __init__(self, exc:'Exception', message:'str', receiver:'MLLPReceiver') -> 'None':
        super().__init__(exc, message)
        self.receiver = receiver

    def reply(self) -> 'str':

        now = time.monotonic()

        delivery = ReceivedDelivery(self.incoming_message, now, now)
        self.receiver.unexpected.append(delivery)

        out = _build_ack(self.incoming_message, f'Unexpected message: {self.exc}')
        return out

# ################################################################################################################################
# ################################################################################################################################

class _ReusableMLLPServer(MLLPServer):
    """ The same server, except it can rebind to its port right after a stop - which is what
    a receiver that goes down and comes back on the address its senders know has to do.
    """
    allow_reuse_address = True

# ################################################################################################################################
# ################################################################################################################################

class _TLSMLLPServer(_ReusableMLLPServer):
    """ The same server again, except every connection it accepts is wrapped in TLS before a byte
    of it is read. hl7apy has nothing to say about transport security, so the wrapping happens where
    the connection is accepted, which leaves the whole of the HL7 side of it untouched.
    """

    # Set by the receiver before the server is started, because what a connection is wrapped in has
    # to exist by the time the first one is accepted
    ssl_context:'any_' = None

    def get_request(self) -> 'any_':

        connection, address = super().get_request()

        # A handshake that fails leaves nothing to serve, and the exception it raises is handled
        # by the server's own error handling rather than by taking the listener down
        wrapped = self.ssl_context.wrap_socket(connection, server_side=True)

        return wrapped, address

# ################################################################################################################################
# ################################################################################################################################

class MLLPReceiver:
    """ A standard-library-of-the-trade MLLP receiving side, built on hl7apy's own MLLP server -
    the same class other Python systems receive HL7 with. It records every delivery it is sent
    and acknowledges each one, taking a configurable amount of time over each when a test needs
    a slow receiver.
    """

    def __init__(
        self,
        delay:'float'=0.0,
        ack_note:'str'='',
        ack_code:'str'='AA',
        cert_path:'str'='',
        key_path:'str'='',
        ca_path:'str'='',
    ) -> 'None':

        self.delay = delay
        self.ack_note = ack_note

        # What every acknowledgment this receiver sends carries in MSA-1. It is AA for a receiver
        # that takes what it is sent, and a rejection code for one a test points a sender at to see
        # how the sender handles being turned away.
        self.ack_code = ack_code

        # What this receiver presents to a sender that connects to it. A certificate turns TLS on,
        # and naming an authority on top of it turns the verification of the sender on too, which
        # is the mutual case an outgoing connection with a certificate of its own is pointed at.
        self.cert_path = cert_path
        self.key_path = key_path
        self.ca_path = ca_path

        self.port = find_free_port()

        self.deliveries:'delivery_list' = []
        self.unexpected:'delivery_list' = []

        self._server:'any_' = None
        self._thread:'threading.Thread | None' = None

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the receiver on its port, which stays the same across a stop and a start,
        the way a real system comes back on the address its senders know.
        """
        handlers:'stranydict' = {}

        for message_type in _Handled_Message_Types:
            handlers[message_type] = (_RecordingHandler, self)

        handlers['ERR'] = (_UnexpectedMessageHandler, self)

        # A receiver with a certificate terminates TLS, and one without takes plain connections
        if self.cert_path:
            self._server = _TLSMLLPServer(_Host, self.port, handlers)
            self._server.ssl_context = self._build_ssl_context()
        else:
            self._server = _ReusableMLLPServer(_Host, self.port, handlers)

        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

# ################################################################################################################################

    def _build_ssl_context(self) -> 'any_':
        """ Builds what this receiver terminates TLS with - what it presents, and where an
        authority is named, what it verifies a sender against.
        """
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(self.cert_path, self.key_path)

        # An authority is only named by a test of the mutual case, and naming one is what makes a
        # sender without a certificate of its own be turned away at the handshake
        if self.ca_path:
            context.verify_mode = ssl.CERT_REQUIRED
            context.load_verify_locations(self.ca_path)

        return context

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the receiver, leaving its port free for a later start.
        """
        self._server.shutdown()
        self._server.server_close()
        self._server = None

# ################################################################################################################################

    @property
    def address(self) -> 'str':
        """ Where an outgoing connection is pointed to reach this receiver.
        """
        out = f'{_Host}:{self.port}'
        return out

# ################################################################################################################################
# ################################################################################################################################
