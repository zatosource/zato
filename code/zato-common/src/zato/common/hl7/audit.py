# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# HL7 audit semantics - what a parsed HL7 v2 message contributes to the shared audit log:
# the searchable attributes each message row carries and what an MSA acknowledgment
# means for the outcome of the exchange it acknowledges.

from __future__ import annotations

# stdlib
from dataclasses import dataclass
from typing import NamedTuple

# Zato
from zato.common.audit_log.api import AuditClassification, AuditOutcome

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict
    from zato.hl7v2.base import HL7Message
    HL7Message = HL7Message
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

class ACKStatus:
    """ The acknowledgment-status axis of an HL7 exchange - the MSA-1 codes from table 0008
    plus the timeout marker for a message no acknowledgment ever arrived for.
    """
    Application_Accept = 'AA'
    Application_Error  = 'AE'
    Application_Reject = 'AR'
    Commit_Accept      = 'CA'
    Commit_Error       = 'CE'
    Commit_Reject      = 'CR'
    Timeout            = 'timeout'

# ################################################################################################################################
# ################################################################################################################################

def get_message_type(msg:'HL7Message') -> 'str':
    """ Returns the message type of a parsed message, e.g. ADT^A01 - the message code
    from MSH-9.1 joined with the trigger event from MSH-9.2 when there is one.
    """
    message_code = msg.get('msh.message_type.message_code')
    if message_code is None:
        message_code = ''

    trigger_event = msg.get('msh.message_type.trigger_event')

    # A trigger event completes the type, and a bare code stands on its own.
    if trigger_event:
        out = f'{message_code}^{trigger_event}'
    else:
        out = message_code

    return out

# ################################################################################################################################

def get_mrn(msg:'HL7Message') -> 'str':
    """ Returns the patient's medical record number - the PID-3 identifier explicitly typed MR,
    or the first identifier at all when none carries that type. An empty string means
    the message has no PID segment or no patient identifiers.
    """

    # Our response to produce
    out = ''

    # The first identifier is remembered in case none is typed MR
    first_identifier = ''

    index = 0

    # Walk all the identifier repetitions ..
    while True:

        identifier = msg.get(f'pid.patient_identifier_list[{index}]')

        # .. there are no more repetitions to look at ..
        if identifier is None:
            break

        # .. remember the first one we saw ..
        if not first_identifier:
            first_identifier = identifier

        # .. and an identifier explicitly typed as a medical record number wins immediately.
        type_code = msg.get(f'pid.patient_identifier_list[{index}].identifier_type_code')
        if type_code == 'MR':
            out = identifier
            break

        index += 1

    # Default to the first identifier when none was typed MR
    if not out:
        out = first_identifier

    return out

# ################################################################################################################################

def get_sending_facility(msg:'HL7Message') -> 'str':
    """ Returns the sending facility from MSH-4 - its namespace id, which is the human-readable part.
    """
    out = msg.get('msh.sending_facility')
    if out is None:
        out = ''

    return out

# ################################################################################################################################

def get_control_id(msg:'HL7Message') -> 'str':
    """ Returns the message control id from MSH-10 - what the audit log stores as the event's msg_id
    and what the acknowledgment quotes back in MSA-2.
    """
    out = msg.get('msh.message_control_id')
    if out is None:
        out = ''

    return out

# ################################################################################################################################

def get_audit_attrs(msg:'HL7Message') -> 'stranydict':
    """ Returns the searchable attributes an HL7 message contributes to its audit events -
    what the message browser lets an operator find messages by.
    """
    out = {
        'msg_type': get_message_type(msg),
        'mrn': get_mrn(msg),
        'facility': get_sending_facility(msg),
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ACKResult:
    """ What one MSA acknowledgment means for the audit trail of the message it acknowledges.
    """

    # The MSA-1 code as received, or the timeout marker when no acknowledgment arrived
    ack_status: 'str' = ''

    # The platform outcome the acknowledgment maps to
    outcome: 'str' = ''

    # The application outcome - the negative acknowledgment code when there is one
    application_outcome: 'str' = ''

    # Whether a failed exchange could work when resubmitted as-is
    classification: 'str' = ''

    # MSA-2 - the control id of the message being acknowledged
    control_id: 'str' = ''

# ################################################################################################################################

class _ACKCodeDetails(NamedTuple):
    outcome: str
    classification: str

# What each acknowledgment code from table 0008 means - a reject can never succeed as-is,
# so it is classified permanent, while an error stays unclassified because either
# a resend or a repair may apply and a person needs to decide which.
_ack_code_details = {
    ACKStatus.Application_Accept: _ACKCodeDetails(AuditOutcome.OK, ''),
    ACKStatus.Commit_Accept:      _ACKCodeDetails(AuditOutcome.OK, ''),
    ACKStatus.Application_Error:  _ACKCodeDetails(AuditOutcome.Error, ''),
    ACKStatus.Commit_Error:       _ACKCodeDetails(AuditOutcome.Error, ''),
    ACKStatus.Application_Reject: _ACKCodeDetails(AuditOutcome.Error, AuditClassification.Permanent),
    ACKStatus.Commit_Reject:      _ACKCodeDetails(AuditOutcome.Error, AuditClassification.Permanent),
}

# ################################################################################################################################

def interpret_ack_code(code:'str', control_id:'str'='') -> 'ACKResult':
    """ Maps one MSA-1 acknowledgment code to what it means for the audit trail.
    """

    # Our response to produce
    out = ACKResult()

    out.ack_status = code
    out.control_id = control_id

    # A code from the acknowledgment table maps directly ..
    if details := _ack_code_details.get(code):
        out.outcome = details.outcome
        out.classification = details.classification

        # .. a negative acknowledgment carries its code as the application outcome ..
        if details.outcome == AuditOutcome.Error:
            out.application_outcome = code

    # .. and anything else means the acknowledgment itself was not understood,
    # which is an error of its own kind, left unclassified.
    else:
        out.outcome = AuditOutcome.Error

    return out

# ################################################################################################################################

def interpret_ack(msg:'HL7Message') -> 'ACKResult':
    """ Interprets the MSA segment of a parsed acknowledgment message. A message with no MSA
    at all is interpreted as an error because the sender expected an acknowledgment
    and received something else.
    """
    code = msg.get('msa.acknowledgment_code')
    if code is None:
        code = ''

    control_id = msg.get('msa.message_control_id')
    if control_id is None:
        control_id = ''

    out = interpret_ack_code(code, control_id)
    return out

# ################################################################################################################################

def interpret_ack_timeout() -> 'ACKResult':
    """ Returns what it means when no acknowledgment arrived in time - a transient failure,
    because resending the same message once the receiver is back can work.
    """

    # Our response to produce
    out = ACKResult()

    out.ack_status = ACKStatus.Timeout
    out.outcome = AuditOutcome.Error
    out.classification = AuditClassification.Transient

    return out

# ################################################################################################################################
# ################################################################################################################################
