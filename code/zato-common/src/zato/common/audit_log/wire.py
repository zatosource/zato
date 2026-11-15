# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The form in which a worker sends its audit events to the SQLite writer process, which commits the events of every worker
# in shared transactions of the audit database. The stream to the writer carries JSON, so the times of an event travel
# as ISO 8601 text, the bytes of its attachments as Base64 and each attribute value that is not a number as the text
# that the attribute rows store.

# stdlib
from base64 import b64decode, b64encode
from datetime import datetime

# Zato
from zato.common.audit_log.buffer import PendingEvent

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, list_, stranydict

    any_ = any_
    anydict = anydict
    anylist = anylist
    stranydict = stranydict

    pending_event_list = list_[PendingEvent]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The columns of the event row that hold times
    Time_Columns = ('pub_time', 'event_time')

# ################################################################################################################################
# ################################################################################################################################

def _attr_to_wire(value:'any_') -> 'any_':
    """ Returns an attribute value as the writer receives it, which yields the same attribute rows.
    """
    if isinstance(value, (bool, int, float)):
        out = value
    else:
        out = str(value)

    return out

# ################################################################################################################################

def event_to_wire(pending:'PendingEvent') -> 'anydict':
    """ Returns one audit event in the form that the stream to the writer process carries.
    """
    values = dict(pending.values)

    for column in ModuleCtx.Time_Columns:
        if values[column] is not None:
            values[column] = values[column].isoformat()

    attrs:'stranydict' = {}

    for name, value in pending.attrs.items():
        attrs[name] = _attr_to_wire(value)

    attachments:'anylist' = []

    for attachment in pending.attachments:
        attachment = dict(attachment)
        attachment['content'] = b64encode(attachment['content']).decode('ascii')
        attachments.append(attachment)

    out = {
        'values': values,
        'attrs': attrs,
        'bodies': pending.bodies,
        'attachments': attachments,
        'parents': pending.parents,
        'parent_link_type': pending.parent_link_type,
        'is_export_payload_active': pending.is_export_payload_active,
    }
    return out

# ################################################################################################################################

def event_from_wire(data:'anydict') -> 'PendingEvent':
    """ Returns one audit event that the writer process received from a worker.
    """
    values = data['values']

    for column in ModuleCtx.Time_Columns:
        if values[column] is not None:
            values[column] = datetime.fromisoformat(values[column])

    for attachment in data['attachments']:
        attachment['content'] = b64decode(attachment['content'])

    out = PendingEvent()
    out.values = values
    out.attrs = data['attrs']
    out.bodies = data['bodies']
    out.attachments = data['attachments']
    out.parents = data['parents']
    out.parent_link_type = data['parent_link_type']
    out.is_export_payload_active = data['is_export_payload_active']

    return out

# ################################################################################################################################

def batch_to_wire(batch:'pending_event_list') -> 'anylist':
    out:'anylist' = []

    for pending in batch:
        out.append(event_to_wire(pending))

    return out

# ################################################################################################################################

def batch_from_wire(data:'anylist') -> 'pending_event_list':
    out:'pending_event_list' = []

    for item in data:
        out.append(event_from_wire(item))

    return out

# ################################################################################################################################
# ################################################################################################################################
