# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os

# Zato
from zato.common.crypto.api import CryptoManager

# Zato - the suite's own parts
from _clients import send_with_java
from _enmasse import Plain_Sending_Application, TLS_Sending_Application
from _services import Plain_Label, TLS_Label

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import MLLPEnvironment

    MLLPEnvironment = MLLPEnvironment

# ################################################################################################################################
# ################################################################################################################################

# What HL7 separates the segments of one message with
_Segment_Separator = '\r'

# The fields of the message the clients send. The receiving application and facility are what the
# acknowledgment reports back as its own sender, which is how a test knows the reply is this one's.
_Sending_Facility     = 'ZatoSendingFacility'
_Receiving_Application = 'ZatoReceivingApp'
_Receiving_Facility    = 'ZatoReceivingFacility'

# What every message here is, chosen because it is the one an interface engine sends most
_Message_Type    = 'ADT'
_Trigger_Event   = 'A01'
_Processing_Id   = 'P'
_Version_Id      = '2.5'

# The acknowledgment code that means the channel took the message
_Ack_Accepted = 'AA'

# The acknowledgment code the listener answers a sender the channel turned away with
_Ack_Rejected = 'AR'

# How many bits the control id of one message is made of, which is what makes each message its own
_Control_Id_Bits = 64

# ################################################################################################################################
# ################################################################################################################################

def _build_message(sending_application:'str', control_id:'str') -> 'str':
    """ Builds one admit message from the sending application that routes it and the control id
    the acknowledgment is expected to refer back to.
    """
    msh = '|'.join([
        'MSH',
        '^~\\&',
        sending_application,
        _Sending_Facility,
        _Receiving_Application,
        _Receiving_Facility,
        '20260727120000',
        '',
        f'{_Message_Type}^{_Trigger_Event}',
        control_id,
        _Processing_Id,
        _Version_Id,
    ])

    # One patient is enough for the message to be more than its own header
    pid = 'PID|1||100001^^^ZATO^MR||Doe^Jane||19800101|F'

    out = _Segment_Separator.join([msh, pid])
    return out

# ################################################################################################################################

def _get_segment(message:'str', name:'str') -> 'list':
    """ Returns the fields of the named segment of a message.
    """
    for segment in message.split(_Segment_Separator):
        if segment.startswith(name + '|'):
            out = segment.split('|')
            return out

    raise Exception(f'No {name} segment in `{message!r}`')

# ################################################################################################################################

def _read_received(messages_file:'str') -> 'list':
    """ Returns what the services have recorded so far, oldest first.
    """
    out = []

    # Nothing has reached a service yet on a run whose first message was turned away
    if not os.path.exists(messages_file):
        return out

    with open(messages_file, 'r') as file_handle:
        for line in file_handle:

            line = line.strip()

            if line:
                out.append(json.loads(line))

    return out

# ################################################################################################################################

def _assert_ack_echoes_message(ack:'bytes', control_id:'str', expected_code:'str') -> 'None':
    """ Checks that the acknowledgment is an answer to this message rather than to any other - it
    carries the code expected of it, it refers back to the control id the message was sent under,
    and its own header names as sender what the message named as receiver.
    """
    ack_text = ack.decode('utf8')

    msa_fields = _get_segment(ack_text, 'MSA')
    assert msa_fields[1] == expected_code, f'Expected {expected_code} in `{ack_text!r}`'
    assert msa_fields[2] == control_id, f'Expected the control id back in `{ack_text!r}`'

    # The header of an acknowledgment has the sender and the receiver of the message it answers
    # swapped, so what was sent as the receiving application comes back as the sending one
    msh_fields = _get_segment(ack_text, 'MSH')
    assert msh_fields[2] == _Receiving_Application, f'Unexpected sending application in `{ack_text!r}`'
    assert msh_fields[3] == _Receiving_Facility, f'Unexpected sending facility in `{ack_text!r}`'
    assert msh_fields[10] == _Processing_Id, f'Unexpected processing id in `{ack_text!r}`'
    assert msh_fields[11] == _Version_Id, f'Unexpected version in `{ack_text!r}`'

# ################################################################################################################################
# ################################################################################################################################

def test_java_client_over_a_plain_connection(mllp_environment:'MLLPEnvironment') -> 'None':
    """ A Java client sending over the plaintext bind reaches the channel that takes it and reads
    back an acknowledgment that echoes the header of what it sent.
    """
    control_id = CryptoManager.generate_hex_string(_Control_Id_Bits)
    message = _build_message(Plain_Sending_Application, control_id)

    ack = send_with_java('127.0.0.1', mllp_environment.ports.mllp_plain, message)

    _assert_ack_echoes_message(ack, control_id, _Ack_Accepted)

    # .. and the message reached the service the channel invokes, unchanged.
    received = _read_received(mllp_environment.messages_file)
    matching = []

    for entry in received:
        if control_id in entry['message']:
            matching.append(entry)

    assert len(matching) == 1, f'Expected the message once, found it {len(matching)} times'
    assert matching[0]['channel'] == Plain_Label
    assert matching[0]['message'] == message

# ################################################################################################################################

def test_java_client_over_a_verified_tls_connection(mllp_environment:'MLLPEnvironment') -> 'None':
    """ A Java client presenting the certificate the channel's security definition names reaches
    that channel over the TLS bind, the common name having travelled from HAProxy to the listener.
    """
    control_id = CryptoManager.generate_hex_string(_Control_Id_Bits)
    message = _build_message(TLS_Sending_Application, control_id)

    ack = send_with_java(
        '127.0.0.1', mllp_environment.ports.mllp_tls, message, certificates=mllp_environment.certificates)

    _assert_ack_echoes_message(ack, control_id, _Ack_Accepted)

    received = _read_received(mllp_environment.messages_file)
    matching = []

    for entry in received:
        if control_id in entry['message']:
            matching.append(entry)

    assert len(matching) == 1, f'Expected the message once, found it {len(matching)} times'
    assert matching[0]['channel'] == TLS_Label
    assert matching[0]['message'] == message

# ################################################################################################################################

def test_the_secured_channel_turns_away_an_unverified_sender(mllp_environment:'MLLPEnvironment') -> 'None':
    """ The same message sent over the plaintext bind carries no verified certificate, so the
    channel that requires one turns it away and its service never runs.
    """
    control_id = CryptoManager.generate_hex_string(_Control_Id_Bits)
    message = _build_message(TLS_Sending_Application, control_id)

    ack = send_with_java('127.0.0.1', mllp_environment.ports.mllp_plain, message)

    _assert_ack_echoes_message(ack, control_id, _Ack_Rejected)

    received = _read_received(mllp_environment.messages_file)

    for entry in received:
        assert control_id not in entry['message'], 'A message the channel turned away still reached a service'

# ################################################################################################################################
# ################################################################################################################################
