# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Object section of an MLLP channel's evidence - what the channel is, read off the ODB, so the model reads
# which messages the channel takes and where it hands them before it reads how it acknowledged them. An MLLP
# channel is a generic connection - its listener is the environment's, shared by every channel, so what tells
# one channel from another is the MSH fields it matches on. The alert settings lines at its end are the ones
# explain/settings_info.py builds for every object that has alert settings.

from __future__ import annotations

# Zato
from zato.common.alerting.explain.settings_info import settings_lines, Off, On
from zato.common.alerting.object_config import alert_type_mllp_channel
from zato.common.api import GENERIC
from zato.common.destination.constants import Respond_From_Service
from zato.common.destination.model import parse_entries
from zato.common.hl7.mllp.fields import get_match_label, Channel_Defaults, Matcher_Labels
from zato.common.odb.model import GenericConn
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import anylist, stranydict, strlist
    anylist = anylist
    SASession = SASession
    stranydict = stranydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# What the Type line of the channel reads as
_type_label = 'MLLP channel'

# What a channel says of a service or of destinations it has none of
_none = 'None'

# What the reply line says when the service produces the acknowledgment
_reply_from_service = 'the service'

# What a destination reads as when it receives nothing
_inactive = 'inactive'

# ################################################################################################################################
# ################################################################################################################################

def _stored_value(opaque:'stranydict', name:'str') -> 'object':
    """ One stored field of the channel, at the field's default when the channel was saved before the field existed.
    """
    if name in opaque:
        out = opaque[name]
    else:
        out = Channel_Defaults[name]

    return out

# ################################################################################################################################

def _destination_lines(opaque:'stranydict') -> 'anylist':
    """ One line per destination - what it is called, what kind of connection it delivers through and whether it
    receives anything - or one line saying the channel has none.
    """

    # Our response to produce
    out:'anylist' = []

    entries = parse_entries(_stored_value(opaque, 'destinations'))

    for entry in entries:
        description = f'{entry.name} - {entry.type} through {entry.connection}'

        if not entry.is_active:
            description += f', {_inactive}'

        out.append(('Destination', description))

    if not entries:
        out.append(('Destinations', _none))

    return out

# ################################################################################################################################

def describe_mllp_channel(session:'SASession', cluster_id:'int', name:'str') -> 'anylist | None':
    """ The label and value pairs describing one MLLP channel - which messages it takes, whether it is the default
    channel, the service that handles them, its destinations, what produces the acknowledgment and how the other
    destinations receive their copy, whether its audit log is on and the alert thresholds it sets of its own.
    None when no MLLP channel goes by the name in the cluster.
    """
    row = session.query(GenericConn).\
        filter(GenericConn.cluster_id==cluster_id).\
        filter(GenericConn.type_==GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP).\
        filter(GenericConn.name==name).\
        first()

    if row is None:
        return None

    opaque = parse_instance_opaque_attr(row)

    # Our response to produce
    out:'anylist' = []

    out.append(('Name', row.name))
    out.append(('Type', _type_label))
    out.append(('Active', 'yes' if row.is_active else 'no'))

    # Which messages reach the channel - the MSH fields it matches on, or every message
    match_values:'stranydict' = {}

    for field_name, _ in Matcher_Labels:
        match_values[field_name] = _stored_value(opaque, field_name)

    out.append(('Match', get_match_label(match_values)))
    out.append(('Default channel', 'yes' if _stored_value(opaque, 'is_default') is True else 'no'))

    service = _stored_value(opaque, 'service')

    if service:
        out.append(('Service', service))
    else:
        out.append(('Service', _none))

    out.extend(_destination_lines(opaque))

    # What produces the acknowledgment the sender receives, and how the other destinations are delivered to
    respond_from = _stored_value(opaque, 'respond_from')

    if respond_from == Respond_From_Service:
        out.append(('Reply produced by', _reply_from_service))
    else:
        out.append(('Reply produced by', f'destination {respond_from}'))

    out.append(('Delivery mode', _stored_value(opaque, 'delivery_mode')))

    # A channel created before the flag existed logs, the same as one whose flag is on - and the alerts read
    # the audit log, so a channel with it off has nothing for them to count
    is_audit_log_active = _stored_value(opaque, 'is_audit_log_active') is True

    out.append(('Audit log', On if is_audit_log_active else Off))

    out.extend(settings_lines(alert_type_mllp_channel, opaque))

    return out

# ################################################################################################################################
# ################################################################################################################################
