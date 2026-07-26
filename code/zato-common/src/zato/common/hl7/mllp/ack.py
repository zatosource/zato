# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import NamedTuple

# Zato
from zato.common.crypto.api import CryptoManager

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

# What an MSH segment carries when it does not say otherwise. A segment that named no encoding
# characters would leave the acknowledgment unreadable, so the standard ones stand in for them.
Default_Encoding_Characters = '^~\\&'

# How many hex characters the acknowledgment's own control id is made of. MSH-10 holds twenty
# characters in the oldest version still in the field, and sixteen sits inside that.
_Control_Id_Bits = 64

# How MSH-7 is written - the standard's own format, with the offset that says which clock it is on.
_Timestamp_Format = '%Y%m%d%H%M%S%z'

# ################################################################################################################################
# ################################################################################################################################

class ErrorCondition(NamedTuple):
    """ One entry of the message error condition table, which is where ERR-3 comes from.
    """
    code: 'str'
    text: 'str'

# The conditions this server reports. The table they come from is HL7 0357 and the text is the
# table's own, so a receiving system reads back exactly what the standard says it means.
Condition_Segment_Sequence_Error = ErrorCondition('100', 'Segment sequence error')
Condition_Data_Type_Error        = ErrorCondition('102', 'Data type error')
Condition_Unsupported_Message    = ErrorCondition('200', 'Unsupported message type')
Condition_Application_Error      = ErrorCondition('207', 'Application internal error')

# The name of that table, as ERR-3 has to say where its code was looked up.
_Condition_Table = 'HL70357'

# Where a caller names no condition, what the acknowledgment code itself already says. An
# application error is what AE reports, while a reject is the interface turning the message
# away rather than the application having failed on it.
_Default_Conditions = {
    'AE': Condition_Application_Error,
    'CE': Condition_Application_Error,
    'AR': Condition_Unsupported_Message,
    'CR': Condition_Unsupported_Message,
}

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

    # The acknowledgment exactly as it arrived - what the audit trail stores
    # and what a resubmit records alongside the new attempt.
    ack_text:    'str'  = ''

# ################################################################################################################################
# ################################################################################################################################

def build_ack(
    original_msh_line:'str',
    ack_code:'str',
    error_text:'str' = '',
    error_condition:'ErrorCondition | None' = None,
    ) -> 'str':
    """ Builds an HL7 ACK message (ER7 string) from the MSH line of the original message.
    Swaps sender/receiver, sets a fresh timestamp and control ID, and populates MSA.
    Appends an ERR segment when error_text is provided, reporting the condition given or,
    where none is, the one the acknowledgment code itself implies.
    """

    # Parse the original MSH fields by splitting on the field separator ..
    fields = original_msh_line.split('|')

    # .. MSH has field separator at position 1 and encoding chars at position 2,
    # so fields[0]='MSH', fields[1]=encoding_chars (e.g. '^~\\&'),
    # fields[2]=sending_application (MSH-3), fields[3]=sending_facility (MSH-4),
    # fields[4]=receiving_application (MSH-5), fields[5]=receiving_facility (MSH-6),
    # fields[9]=message_control_id (MSH-10).

    # .. a line with no field separator at all is read like any other short one, because a
    # .. malformed message still has a sender waiting to be told so ..
    encoding_characters = _get_field(fields, 1)

    if not encoding_characters:
        encoding_characters = Default_Encoding_Characters

    # .. extract the sender and receiver fields to swap them ..
    original_sending_application = _get_field(fields, 2)
    original_sending_facility    = _get_field(fields, 3)
    original_receiving_application = _get_field(fields, 4)
    original_receiving_facility    = _get_field(fields, 5)
    original_control_id            = _get_field(fields, 9)

    # .. generate a fresh timestamp for MSH-7, on a clock the receiver can place ..
    now = datetime.now(timezone.utc)
    timestamp = now.strftime(_Timestamp_Format)

    # .. and a control id of our own, which is ours to be referred to by rather than
    # .. the sender's handed back to it ..
    ack_control_id = CryptoManager.generate_hex_string(_Control_Id_Bits)

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

        # A caller that knows why the message failed says so, and otherwise the acknowledgment
        # code narrows it down as far as it can be narrowed from here
        if error_condition is None:
            error_condition = _Default_Conditions[ack_code]

        condition = f'{error_condition.code}^{error_condition.text}^{_Condition_Table}'
        err_segment = f'ERR|||{condition}|E|||{error_text}'
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
    out.ack_text = ack_er7

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

    # .. an acknowledgment naming another message is not an answer to this one, and it is
    # .. reported the way every other problem here is rather than thrown at the caller. Retrying
    # .. is left unset because sending the message again would not make the reply match ..
    if control_id != sent_control_id:
        out.error_text = f'ACK MSA-2 mismatch: expected {sent_control_id!r}, got {control_id!r}'
        return out

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
