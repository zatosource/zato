# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# python-hl7
import hl7
from hl7.client import MLLPClient

# ################################################################################################################################
# ################################################################################################################################

# The bytes MLLP wraps each message in - one to open a frame and two to close it
_Start_Block = b'\x0b'
_End_Block   = b'\x1c\x0d'

# What every message built here says about its receiver
_Receiving_App      = 'ZATO'
_Receiving_Facility = 'ZATO'

# MSH-7 of every message built here - the tests care about routing fields, not the clock
_Timestamp = '20260731120000'

# MSH-11 and MSH-12 of every message built here
_Processing_Id = 'P'
_Version_Id    = '2.5'

# The extra segments each message type carries below its MSH line
_ADT_Body = (
    'EVN|A01|20260731120000\r'
    'PID|||12345^^^MRN||Doe^John||19800101|M\r'
    'PV1||I|ICU^Room1'
)

_ORU_Body = (
    'PID|||67890^^^MRN||Smith^Jane||19900515|F\r'
    'OBR|1||LAB001|CBC^Complete Blood Count\r'
    'OBX|1|NM|WBC^White Blood Count||7.5|10*3/uL|4.5-11.0|N|||F'
)

_message_bodies = {
    'ADT': _ADT_Body,
    'ORU': _ORU_Body,
}

# ################################################################################################################################
# ################################################################################################################################

class SendResult(NamedTuple):
    """ What one send brought back, read off the acknowledgment's MSA segment.
    """
    msa_1: 'str'
    msa_2: 'str'
    msa_3: 'str'

# ################################################################################################################################
# ################################################################################################################################

def build_message(
    control_id:'str',
    sending_app:'str',
    sending_facility:'str',
    message_type:'str' = 'ADT',
    trigger_event:'str' = 'A01',
    ) -> 'str':
    """ Builds an HL7 v2 message whose routing fields are exactly what the caller says,
    so one builder covers every combination the routing tests send.
    """

    # The MSH line carries every field the router matches on ..
    msh_line = (
        f'MSH|^~\\&|{sending_app}|{sending_facility}|{_Receiving_App}|{_Receiving_Facility}'
        f'|{_Timestamp}||{message_type}^{trigger_event}|{control_id}|{_Processing_Id}|{_Version_Id}'
    )

    # .. and the body below it is what a real sender of that message type would append.
    body = _message_bodies[message_type]

    out = msh_line + '\r' + body
    return out

# ################################################################################################################################

def parse_ack(ack_text:'str') -> 'SendResult':
    """ Reads the MSA fields out of an acknowledgment with python-hl7's own parser.
    """
    ack = hl7.parse(ack_text)
    msa = ack.segment('MSA')

    msa_1 = str(msa[1])
    msa_2 = str(msa[2])

    # MSA-3 is present only when the answering side put something there
    msa_field_count = len(msa)

    if msa_field_count > 3:
        msa_3 = str(msa[3])
    else:
        msa_3 = ''

    out = SendResult(msa_1, msa_2, msa_3)
    return out

# ################################################################################################################################

def send_message(host:'str', port:'int', message:'str') -> 'SendResult':
    """ Sends one HL7 message with python-hl7's MLLP client and returns what its
    acknowledgment's MSA segment said.
    """

    # The client frames the message, sends it and reads the reply back ..
    with MLLPClient(host, port) as client:
        reply = client.send_message(message)

    # .. the reply arrives with its MLLP framing still on ..
    reply = reply.removeprefix(_Start_Block)
    reply = reply.removesuffix(_End_Block)
    ack_text = reply.decode('utf-8')

    # .. and its MSA segment is the answer.
    out = parse_ack(ack_text)
    return out

# ################################################################################################################################
# ################################################################################################################################
