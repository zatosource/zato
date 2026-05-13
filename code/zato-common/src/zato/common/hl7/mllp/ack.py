# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import datetime

# Zato
from zato.common.hl7.exception import HL7Exception

# ################################################################################################################################
# ################################################################################################################################

# ACK codes that mean "accepted" (no further action needed)
_accepted_codes = frozenset({'AA', 'CA'})

# ACK codes that mean "rejected, do not retry"
_rejected_no_retry_codes = frozenset({'AE', 'CE'})

# ACK codes that mean "rejected, should retry"
_rejected_retry_codes = frozenset({'AR', 'CR'})

# All valid ACK codes
_all_ack_codes = _accepted_codes | _rejected_no_retry_codes | _rejected_retry_codes

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class AckResult:
    """ Outcome of validating an ACK message received from a remote system.
    """
    ack_code:    'str'  = ''
    is_accepted: 'bool' = False
    should_retry:'bool' = False
    error_text:  'str'  = ''

# ################################################################################################################################
# ################################################################################################################################

def build_ack(
    original_msh_line:'str',
    ack_code:'str',
    error_text:'str' = '',
    ) -> 'str':
    """ Builds an HL7 ACK message (ER7 string) from the MSH line of the original message.
    Swaps sender/receiver, sets a fresh timestamp and control ID, and populates MSA.
    Optionally appends an ERR segment when error_text is provided.
    """

    # Parse the original MSH fields by splitting on the field separator ..
    fields = original_msh_line.split('|')

    # .. MSH has field separator at position 1 and encoding chars at position 2,
    # so fields[0]='MSH', fields[1]=encoding_chars (e.g. '^~\\&'),
    # fields[2]=sending_application (MSH-3), fields[3]=sending_facility (MSH-4),
    # fields[4]=receiving_application (MSH-5), fields[5]=receiving_facility (MSH-6),
    # fields[9]=message_control_id (MSH-10).

    encoding_characters = fields[1]

    # .. extract the sender and receiver fields to swap them ..
    original_sending_application = _get_field(fields, 2)
    original_sending_facility    = _get_field(fields, 3)
    original_receiving_application = _get_field(fields, 4)
    original_receiving_facility    = _get_field(fields, 5)
    original_control_id            = _get_field(fields, 9)

    # .. generate a fresh timestamp for MSH-7 ..
    now = datetime.now()
    timestamp = now.strftime('%Y%m%d%H%M%S')

    # .. generate a fresh control ID for the ACK's own MSH-10 ..
    ack_control_id = f'ACK-{original_control_id}-{timestamp}'

    # .. extract the original processing ID (MSH-11) and version (MSH-12) ..
    processing_id = _get_field(fields, 10)
    version_id    = _get_field(fields, 11)

    # .. build the ACK MSH segment with sender/receiver swapped ..
    ack_msh = (
        f'MSH|{encoding_characters}'
        f'|{original_receiving_application}'
        f'|{original_receiving_facility}'
        f'|{original_sending_application}'
        f'|{original_sending_facility}'
        f'|{timestamp}'
        f'||ACK'
        f'|{ack_control_id}'
        f'|{processing_id}'
        f'|{version_id}'
    )

    # .. build the MSA segment ..
    ack_msa = f'MSA|{ack_code}|{original_control_id}'

    # .. start assembling the full ACK message ..
    segments = [ack_msh, ack_msa]

    # .. add an ERR segment when there is error text to report ..
    if error_text:
        err_segment = f'ERR|||207^Application internal error^HL70357|E|||{error_text}'
        segments.append(err_segment)

    out = '\r'.join(segments)
    return out

# ################################################################################################################################
# ################################################################################################################################

def validate_ack(ack_er7:'str', sent_control_id:'str') -> 'AckResult':
    """ Validates an ACK message (ER7 string) and returns an AckResult.
    Checks that MSA-2 matches the original MSH-10 we sent,
    and maps the ACK code to accepted/rejected/retry.
    """

    # Our response to produce
    out = AckResult()

    # Split the ACK into segments ..
    segments = ack_er7.split('\r')

    # .. find the MSA segment ..
    msa_line = ''

    for segment in segments:
        if segment.startswith('MSA|'):
            msa_line = segment
            break

    if not msa_line:
        out.error_text = 'ACK message has no MSA segment'
        return out

    # .. parse MSA fields ..
    msa_fields = msa_line.split('|')
    ack_code   = _get_field(msa_fields, 1)
    control_id = _get_field(msa_fields, 2)

    out.ack_code = ack_code

    # .. verify MSA-2 matches the control ID we sent ..
    if control_id != sent_control_id:
        raise HL7Exception(
            f'ACK MSA-2 mismatch: expected {sent_control_id!r}, got {control_id!r}'
        )

    # .. map the ACK code to the result fields ..
    if ack_code in _accepted_codes:
        out.is_accepted = True

    elif ack_code in _rejected_no_retry_codes:
        out.error_text = f'Application error ({ack_code})'

    elif ack_code in _rejected_retry_codes:
        out.should_retry = True
        out.error_text = f'Application reject ({ack_code})'

    # .. anything else we do not recognize.
    else:
        out.error_text = f'Unknown ACK code: {ack_code!r}'

    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_field(fields:'list[str]', index:'int') -> 'str':
    """ Safely retrieves a field from a split segment line.
    Returns empty string if the field index is beyond the available fields,
    which happens with truncated messages.
    """

    if index < len(fields):
        out = fields[index]
    else:
        out = ''

    return out

# ################################################################################################################################
# ################################################################################################################################
