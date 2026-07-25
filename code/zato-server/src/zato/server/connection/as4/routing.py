# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import AS4
from zato.common.as4.sbdh import parse_sbdh

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as4.ebms import SignalDetails, UserMessageDetails
    from zato.common.typing_ import any_, stranydict
    any_ = any_
    stranydict = stranydict
    SignalDetails = SignalDetails
    UserMessageDetails = UserMessageDetails

# ################################################################################################################################
# ################################################################################################################################

def build_routed_message(
    profile:'str',
    user_message:'UserMessageDetails',
    payload:'any_',
    sbdh_details:'any_'=None,
    ) -> 'stranydict':
    """ Builds the dictionary that one accepted payload is routed with - the ebMS metadata
    plus, for Peppol, the SBDH metadata, so subscribers route without re-parsing anything.

    A caller that has already read the SBDH passes it in, otherwise it is read here.
    """

    data = payload.data.decode('utf8', 'replace')

    # All the keys are always present, no matter the profile.
    out = {
        'message_id': user_message.message_id,
        'conversation_id': user_message.conversation_id,
        'from_party': user_message.from_party,
        'to_party': user_message.to_party,
        'service': user_message.service,
        'action': user_message.action,
        'mime_type': payload.mime_type,
        'data': data,
        'sbdh_sender': '',
        'sbdh_receiver': '',
        'sbdh_document_type': '',
        'sbdh_process_id': '',
        'sbdh_instance_identifier': '',
    }

    # Peppol payloads carry an SBDH whose identifiers subscribers route by.
    if profile == AS4.Profile.Peppol:

        if sbdh_details is None:
            sbdh_details, _ = parse_sbdh(payload.data)

        out['sbdh_sender'] = sbdh_details.sender_id
        out['sbdh_receiver'] = sbdh_details.receiver_id
        out['sbdh_document_type'] = sbdh_details.document_type
        out['sbdh_process_id'] = sbdh_details.process_id
        out['sbdh_instance_identifier'] = sbdh_details.instance_identifier

    return out

# ################################################################################################################################

def build_routed_signal(signal:'SignalDetails') -> 'stranydict':
    """ Builds the dictionary that one delivered signal is routed with - what it says about the
    earlier message it refers to, without the XML it was parsed from.
    """
    errors = []

    for error in signal.errors:
        errors.append({
            'error_code': error.error_code,
            'severity': error.severity,
            'short_description': error.short_description,
            'detail': error.detail,
        })

    # A signal that refers to no message genuinely carries no reference.
    ref_to_message_id = signal.ref_to_message_id
    if ref_to_message_id is None:
        ref_to_message_id = ''

    out = {
        'message_id': signal.message_id,
        'ref_to_message_id': ref_to_message_id,
        'timestamp': signal.timestamp,
        'is_receipt': signal.is_receipt,
        'errors': errors,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
