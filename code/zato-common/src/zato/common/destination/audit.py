# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# One row per delivery attempt to one destination. Every row shares the correlation id of the
# message that came in, so the trail of one inbound message already shows everything it fanned
# out to, and every row carries the payload it went out with, which is what makes a single
# failed delivery repeatable on its own later.

from __future__ import annotations

# stdlib
from json import dumps

# Zato
from zato.common.audit_log.common import AuditEvent, AuditOutcome, AuditSource
from zato.common.destination.constants import Default_Method, Default_Path, DestinationOption, DestinationType
from zato.common.destination.model import get_option

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.api import AuditLog
    from zato.common.destination.model import DestinationEntry
    from zato.common.typing_ import any_, intnone, stranydict
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# Which audit source a delivery belongs to, by the type of connection it goes through
_source_by_type = {
    DestinationType.REST: AuditSource.REST_Outgoing,
    DestinationType.MLLP: AuditSource.HL7,
    DestinationType.FHIR: AuditSource.FHIR,
    DestinationType.SMTP: AuditSource.Email_SMTP,
}

# The types whose delivery is one HTTP call, so repeating it needs the method and the path as well
_types_with_method = (DestinationType.REST, DestinationType.FHIR)

# ################################################################################################################################
# ################################################################################################################################

def get_payload_text(payload:'any_') -> 'str':
    """ Returns one payload the way it is stored - what goes out on the wire when the
    payload is already text or bytes, and its JSON form when it is a document.
    """

    # Bytes went out as they are and are recorded decoded ..
    if isinstance(payload, bytes):
        out = payload.decode('utf-8', errors='replace')

    # .. text is recorded as it stands ..
    elif isinstance(payload, str):
        out = payload

    # .. a document is recorded the way it goes out ..
    elif isinstance(payload, (dict, list)):
        out = dumps(payload)

    # .. and anything else is recorded as it describes itself.
    else:
        out = str(payload)

    return out

# ################################################################################################################################

def build_stored_data(entry:'DestinationEntry', payload:'str') -> 'str':
    """ Builds the document one delivery is recorded with - the payload that went out, plus
    what an HTTP delivery needs to be repeated exactly as it was made.
    """
    details:'stranydict' = {'payload': payload}

    if entry.type in _types_with_method:
        details[DestinationOption.Method] = get_option(entry, DestinationOption.Method, Default_Method)
        details[DestinationOption.Path] = get_option(entry, DestinationOption.Path, Default_Path)

    out = dumps(details)
    return out

# ################################################################################################################################

def record_hop(
    audit_log:'AuditLog',
    channel_name:'str',
    entry:'DestinationEntry',
    payload:'any_',
    *,
    cid:'str',
    sequence:'int',
    attempt:'int',
    duration_ms:'int',
    error:'str' = '',
    ) -> 'intnone':
    """ Records one delivery attempt to one destination, whether it succeeded or not, so the
    delivery history of every destination of a channel has no holes in it.
    """
    source = _source_by_type[entry.type]

    payload_text = get_payload_text(payload)
    stored_data = build_stored_data(entry, payload_text)

    attrs = {
        'channel_name': channel_name,
        'destination_name': entry.name,
        'destination_type': entry.type,
        'delivery_sequence': sequence,
        'attempt': attempt,
    }

    # A delivery that raised is recorded with what it raised, which is also what
    # decides whether another attempt with the same message can work ..
    if error:
        outcome = AuditOutcome.Error

    # .. and one that went through is recorded as it is.
    else:
        outcome = AuditOutcome.OK

    out = audit_log.insert(
        source,
        AuditEvent.Request_Sent,
        entry.connection,
        cid=cid,
        size=len(payload_text),
        outcome=outcome,
        status=error,
        duration_ms=duration_ms,
        data=stored_data,
        attrs=attrs,
    )

    return out

# ################################################################################################################################
# ################################################################################################################################
