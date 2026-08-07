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
from zato.common.destination.constants import Default_Method, Default_Path, Default_Subject, Default_To, \
    DestinationOption, DestinationType, Hop_Destination_Name
from zato.common.destination.model import get_option, new_entry, DestinationException

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
    DestinationType.MLLP: AuditSource.MLLP_Outgoing,
    DestinationType.FHIR: AuditSource.FHIR,
    DestinationType.SMTP: AuditSource.Email_SMTP,
}

# Which destination type a recorded delivery went to, read the other way round
_type_by_source = {source: destination_type for destination_type, source in _source_by_type.items()}

# What repeating one delivery needs beyond the payload, by the type of connection it went through -
# each option stored flat alongside the payload, at the default in force when the destination
# does not carry it. This is the convention every producer of a resendable row follows.
_stored_options = {
    DestinationType.REST: {
        DestinationOption.Method: Default_Method,
    },
    DestinationType.FHIR: {
        DestinationOption.Method: Default_Method,
        DestinationOption.Path: Default_Path,
    },
    DestinationType.SMTP: {
        DestinationOption.To: Default_To,
        DestinationOption.Subject: Default_Subject,
    },

    # An MLLP delivery is the message itself and nothing else
    DestinationType.MLLP: {},
}

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
    """ Builds the document one delivery is recorded with - the payload that went out, the
    destination it went to and whatever else repeating that one delivery needs.
    """
    details:'stranydict' = {
        'payload': payload,
        Hop_Destination_Name: entry.name,
    }

    for name, default in _stored_options[entry.type].items():
        details[name] = get_option(entry, name, default)

    out = dumps(details)
    return out

# ################################################################################################################################

def get_hop_entry(source:'str', connection:'str', details:'stranydict') -> 'DestinationEntry':
    """ Returns the destination one recorded delivery went to, rebuilt out of the row that
    delivery left behind, so repeating it goes out exactly the way it did the first time.
    """
    if source not in _type_by_source:
        raise DestinationException(f'Source `{source}` records no delivery that can be repeated on its own')

    destination_type = _type_by_source[source]

    # Whatever the row carries of what its type needs - a row recorded before an option existed
    # falls back to the default in force for it, the same as a destination not carrying it.
    options = {}

    for name, default in _stored_options[destination_type].items():
        options[name] = details.get(name, default)

    # A row names the destination it went to, and one recorded by a connection on its own behalf
    # is addressed by that connection.
    name = details.get(Hop_Destination_Name, connection)

    out = new_entry(name, destination_type, connection, options=options)
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
