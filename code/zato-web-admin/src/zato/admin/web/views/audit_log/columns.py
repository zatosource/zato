# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

What each source's audit log page looks like - its title, the columns of its table, the attrs that
render as columns of their own, the outcomes its events report, and the ceilings the page itself
is bounded by.
"""

# Zato
from zato.common.audit_log.common import AuditOutcome

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strtuple
    strtuple = strtuple

# ################################################################################################################################
# ################################################################################################################################

_poll_url = '/zato/audit-log/poll/'
_flow_url = '/zato/audit-log/flow/'

_default_page = 1
_default_page_size = 25

# How many characters of the payload are shown in the table
_data_preview_len = 200

# How many characters of a message a caller that only shows the top of one is given - enough
# for the head of any message and short of what a browser would have to be handed a whole
# multi-megabyte body for
_preview_len = 4000

# The columns returned to the frontend, in the order they appear in the select below
_row_columns = ('id', 'cid', 'source', 'event_type', 'object_name', 'event_time_iso', 'msg_id', 'correl_id',
    'endpoint', 'ext_client_id', 'outcome', 'status', 'classification', 'size', 'duration_ms', 'data')

# A line of one event's flow reads one thing a row of a list has no place for - where the event
# stands among the others of its own cid, which is what orders two events of the same moment.
_flow_columns = _row_columns + ('cid_sequence',)

# The row columns holding numbers - every other one is text, and a database NULL in a text column
# reaches the frontend as an empty string so no cell renderer needs to know about NULLs at all.
_row_numeric_columns = ('id', 'size', 'duration_ms', 'cid_sequence')

# The free-text search covers these columns
_search_columns = ('data', 'msg_id', 'correl_id', 'endpoint', 'ext_client_id')

# The status query parameter value narrowing the page down to open exchanges
_status_outstanding = 'outstanding'

# ################################################################################################################################
# ################################################################################################################################

# Per-source page titles - more sources will follow, e.g. REST outgoing connections
_source_title = {
    'pubsub': 'Pub/sub audit log',
    'rest-channel': 'REST channel audit log',
    'soap-channel': 'SOAP channel audit log',
    'rest-outgoing': 'Outgoing REST audit log',
    'soap-outgoing': 'Outgoing SOAP audit log',
    'email-imap': 'IMAP audit log',
    'as2': 'AS2 audit log',
    'as4': 'AS4 audit log',
    'x12': 'X12 audit log',
    'mcp': 'MCP audit log',
    'hl7': 'HL7 audit log',
    'fhir': 'FHIR audit log',
}

# Each column tells the frontend which row key to read, what header label to show
# and how to render the cell - the types are implemented in audit_log.js
_pubsub_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'msg_id', 'label': 'Message id', 'type': 'text'},
    {'key': 'endpoint', 'label': 'Endpoint', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

_rest_channel_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'endpoint', 'label': 'Endpoint', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

_soap_channel_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'endpoint', 'label': 'Endpoint', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

_rest_outgoing_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'endpoint', 'label': 'Endpoint', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

_soap_outgoing_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'endpoint', 'label': 'Endpoint', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

_email_imap_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'endpoint', 'label': 'Folder', 'type': 'text'},
    {'key': 'msg_id', 'label': 'Message id', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

_as2_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'object_name', 'label': 'Partner', 'type': 'text'},
    {'key': 'msg_id', 'label': 'Message id', 'type': 'text'},
    {'key': 'disposition', 'label': 'Disposition', 'type': 'text'},
    {'key': 'mic', 'label': 'MIC', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
    {'key': 'action', 'label': 'Actions', 'type': 'action'},
]

_as4_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'object_name', 'label': 'Partner', 'type': 'text'},
    {'key': 'msg_id', 'label': 'Message id', 'type': 'text'},
    {'key': 'conversation_id', 'label': 'Conversation id', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
    {'key': 'action', 'label': 'Actions', 'type': 'action'},
]

_x12_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'object_name', 'label': 'Partner', 'type': 'text'},
    {'key': 'msg_id', 'label': 'Control number', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

_mcp_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'endpoint', 'label': 'Tool', 'type': 'text'},
    {'key': 'ext_client_id', 'label': 'Caller', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

_hl7_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'msg_id', 'label': 'Control id', 'type': 'text'},
    {'key': 'msg_type', 'label': 'Type', 'type': 'text'},
    {'key': 'mrn', 'label': 'MRN', 'type': 'text'},
    {'key': 'facility', 'label': 'Facility', 'type': 'text'},
    {'key': 'ack_status', 'label': 'ACK', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
    {'key': 'action', 'label': 'Actions', 'type': 'action'},
]

_fhir_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'endpoint', 'label': 'Request', 'type': 'text'},
    {'key': 'resource_type', 'label': 'Resource', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
    {'key': 'action', 'label': 'Actions', 'type': 'action'},
]

# Per-source table columns
_source_columns = {
    'pubsub': _pubsub_columns,
    'rest-channel': _rest_channel_columns,
    'soap-channel': _soap_channel_columns,
    'rest-outgoing': _rest_outgoing_columns,
    'soap-outgoing': _soap_outgoing_columns,
    'email-imap': _email_imap_columns,
    'as2': _as2_columns,
    'as4': _as4_columns,
    'x12': _x12_columns,
    'mcp': _mcp_columns,
    'hl7': _hl7_columns,
    'fhir': _fhir_columns,
}

# ################################################################################################################################
# ################################################################################################################################

# Per-source attr columns - these render as columns of their own, read out of the event_attr
# table in one query per page, and the free-text search covers them through the attr-to-cid shape.
_source_attr_columns = {
    'hl7': ('msg_type', 'mrn', 'facility', 'ack_status'),
    'fhir': ('resource_type', 'method'),
}

# The sources whose payloads live in the event_body table rather than the data column
_source_body_preview = {'hl7'}

# ################################################################################################################################
# ################################################################################################################################

# What outcomes a source's events report, which is what the listing offers as filters. Everything
# that carries a message reports whether it went through or failed ..
_default_outcomes = (AuditOutcome.OK, AuditOutcome.Error)

# .. and a pushed pub/sub message may also run out of time before it can be delivered, which is
# an outcome of its own and one no other source can report.
_source_outcomes = {
    'pubsub': (AuditOutcome.OK, AuditOutcome.Error, AuditOutcome.Expired),
}

# ################################################################################################################################

def _get_outcomes(source:'str') -> 'strtuple':
    """ Returns the outcomes this source's events report, so that a page offers filters for
    the outcomes it can actually show and for no others.
    """
    if source in _source_outcomes:
        out = _source_outcomes[source]
        return out

    return _default_outcomes

# ################################################################################################################################
# ################################################################################################################################
