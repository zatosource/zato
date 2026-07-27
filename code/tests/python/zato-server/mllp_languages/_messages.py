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

# ################################################################################################################################
# ################################################################################################################################

# What HL7 separates the segments of one message with
Segment_Separator = '\r'

# The fields of the message the clients send. The receiving application and facility are what the
# acknowledgment reports back as its own sender, which is how a test knows the reply is this one's.
_Sending_Facility      = 'ZatoSendingFacility'
_Receiving_Application = 'ZatoReceivingApp'
_Receiving_Facility    = 'ZatoReceivingFacility'

# What every message here is, chosen because it is the one an interface engine sends most
_Message_Type    = 'ADT'
_Trigger_Event   = 'A01'
_Processing_Id   = 'P'
_Version_Id      = '2.5'

# The acknowledgment code that means the channel took the message
Ack_Accepted = 'AA'

# The acknowledgment code the listener answers a sender the channel turned away with
Ack_Rejected = 'AR'

# How many bits the control id of one message is made of, which is what makes each message its own
_Control_Id_Bits = 64

# ################################################################################################################################
# ################################################################################################################################

def new_control_id() -> 'str':
    """ Returns a control id no other message of this run carries, which is how a test tells the
    message it sent from every other one that reached the same service.
    """
    out = CryptoManager.generate_hex_string(_Control_Id_Bits)
    return out

# ################################################################################################################################

def build_message(sending_application:'str', control_id:'str') -> 'str':
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

    out = Segment_Separator.join([msh, pid])
    return out

# ################################################################################################################################

def get_segment(message:'str', name:'str') -> 'list':
    """ Returns the fields of the named segment of a message.
    """
    for segment in message.split(Segment_Separator):
        if segment.startswith(name + '|'):
            out = segment.split('|')
            return out

    raise Exception(f'No {name} segment in `{message!r}`')

# ################################################################################################################################

def get_acknowledged_control_id(ack:'bytes') -> 'str':
    """ Returns the control id of the message the acknowledgment answers, which is what says
    which of the messages sent it belongs to.
    """
    msa_fields = get_segment(ack.decode('utf8'), 'MSA')

    out = msa_fields[2]
    return out

# ################################################################################################################################

def read_received(messages_file:'str') -> 'list':
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

def find_recorded(messages_file:'str', control_id:'str') -> 'list':
    """ Returns every entry a service recorded for the message sent under this control id, which
    is one for a message that was taken and none for one that was turned away.
    """
    out = []

    for entry in read_received(messages_file):
        if control_id in entry['message']:
            out.append(entry)

    return out

# ################################################################################################################################

def assert_ack_echoes_message(ack:'bytes', control_id:'str', expected_code:'str') -> 'None':
    """ Checks that the acknowledgment is an answer to this message rather than to any other - it
    carries the code expected of it, it refers back to the control id the message was sent under,
    and its own header names as sender what the message named as receiver.
    """
    ack_text = ack.decode('utf8')

    msa_fields = get_segment(ack_text, 'MSA')
    assert msa_fields[1] == expected_code, f'Expected {expected_code} in `{ack_text!r}`'
    assert msa_fields[2] == control_id, f'Expected the control id back in `{ack_text!r}`'

    # The header of an acknowledgment has the sender and the receiver of the message it answers
    # swapped, so what was sent as the receiving application comes back as the sending one
    msh_fields = get_segment(ack_text, 'MSH')
    assert msh_fields[2] == _Receiving_Application, f'Unexpected sending application in `{ack_text!r}`'
    assert msh_fields[3] == _Receiving_Facility, f'Unexpected sending facility in `{ack_text!r}`'
    assert msh_fields[10] == _Processing_Id, f'Unexpected processing id in `{ack_text!r}`'
    assert msh_fields[11] == _Version_Id, f'Unexpected version in `{ack_text!r}`'

# ################################################################################################################################
# ################################################################################################################################
