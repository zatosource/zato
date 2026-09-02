# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import SCHEDULER
from zato.common.audit_log.common import source_attr_names, AuditOutcome, Status_Outstanding
from zato.common.audit_log.search import search_columns

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strtuple

    # Add dummy assignments to satisfy type checkers
    strtuple = strtuple

# ################################################################################################################################
# ################################################################################################################################

_poll_url = '/zato/audit-log/poll/'

_default_page = 1
_default_page_size = 25

# How many characters of the payload are shown in the table.
_data_preview_length = 200

# How many characters of a message a caller that only shows the top of one is given.
_preview_length = 4000

# The columns returned to the frontend, in the order they appear in the select below.
_row_columns = ('id', 'cid', 'source', 'event_type', 'object_name', 'event_time_iso', 'msg_id', 'correl_id',
    'endpoint', 'ext_client_id', 'outcome', 'status', 'classification', 'size', 'duration_ms', 'data')

# A flow row also carries the event's position among the others of its own cid.
_flow_columns = _row_columns + ('cid_sequence',)

# The row columns holding numbers.
_row_numeric_columns = ('id', 'size', 'duration_ms', 'cid_sequence')

# The columns the free-text search covers.
_search_columns = search_columns

# The status query parameter value narrowing the page down to open exchanges.
_status_outstanding = Status_Outstanding

# ################################################################################################################################
# ################################################################################################################################

# Each column tells the frontend which row key to read, what header label to show
# and how to render the cell - the types are implemented in audit-log.js.
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
    {'key': 'endpoint', 'label': 'Service', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'status', 'label': 'Status', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

_soap_channel_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'endpoint', 'label': 'Service', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'status', 'label': 'Status', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

_rest_outgoing_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'endpoint', 'label': 'Address', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'status', 'label': 'Status', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

_soap_outgoing_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'endpoint', 'label': 'Address', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'status', 'label': 'Status', 'type': 'text'},
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

_file_outgoing_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'operation', 'label': 'Operation', 'type': 'text'},
    {'key': 'schedule', 'label': 'Schedule', 'type': 'text'},
    {'key': 'file_name', 'label': 'File', 'type': 'text'},
    {'key': 'endpoint', 'label': 'Remote path', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
    {'key': 'action', 'label': 'Actions', 'type': 'action'},
]

_sql_outgoing_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'object_name', 'label': 'Connection', 'type': 'text'},
    {'key': 'endpoint', 'label': 'Database', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'duration_ms', 'label': 'Duration', 'type': 'text'},
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

_mllp_columns = [
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

_scheduler_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'object_name', 'label': 'Job', 'type': 'text'},
    {'key': 'endpoint', 'label': 'Service', 'type': 'text'},
    {'key': 'current_run', 'label': 'Run', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'duration_ms', 'label': 'Duration', 'type': 'text'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
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

_llm_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'object_name', 'label': 'Connection', 'type': 'text'},
    {'key': 'endpoint', 'label': 'Address', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'duration_ms', 'label': 'Duration', 'type': 'text'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

_email_smtp_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'endpoint', 'label': 'Address', 'type': 'text'},
    {'key': 'msg_id', 'label': 'Message id', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

# A log access record is named by who read what rather than by a message.
_config_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'actor', 'label': 'Actor', 'type': 'text'},
    {'key': 'viewed_object_name', 'label': 'Viewed', 'type': 'text'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

_odoo_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'object_name', 'label': 'Connection', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'status', 'label': 'Status', 'type': 'text'},
    {'key': 'duration_ms', 'label': 'Duration', 'type': 'text'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

_microsoft_cloud_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'object_name', 'label': 'Connection', 'type': 'text'},
    {'key': 'endpoint', 'label': 'Request', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'duration_ms', 'label': 'Duration', 'type': 'text'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

_microsoft_health_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'object_name', 'label': 'Service', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'status', 'label': 'Status', 'type': 'text'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

_certificate_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'object_name', 'label': 'Connection', 'type': 'text'},
    {'key': 'endpoint', 'label': 'Address', 'type': 'text'},
    {'key': 'days_left', 'label': 'Days left', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'status', 'label': 'Status', 'type': 'text'},
]

_test_transfer_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'object_name', 'label': 'Connection', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'status', 'label': 'Status', 'type': 'text'},
]

# The columns of the all-events page - the ones every source shares, plus the source itself.
_all_sources_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'source', 'label': 'Source', 'type': 'text'},
    {'key': 'object_name', 'label': 'Object', 'type': 'text'},
    {'key': 'msg_id', 'label': 'Message id', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

# Per-source table columns.
_source_columns = {
    'pubsub': _pubsub_columns,
    'rest-channel': _rest_channel_columns,
    'soap-channel': _soap_channel_columns,
    'rest-outgoing': _rest_outgoing_columns,
    'soap-outgoing': _soap_outgoing_columns,

    # A check's rows have the same shape as the calls it watches.
    'rest-outgoing-health': _rest_outgoing_columns,
    'soap-outgoing-health': _soap_outgoing_columns,
    'email-imap': _email_imap_columns,
    'email-smtp': _email_smtp_columns,
    'file-outgoing': _file_outgoing_columns,
    'sql-outgoing': _sql_outgoing_columns,
    'as2': _as2_columns,
    'as4': _as4_columns,
    'x12': _x12_columns,
    'mcp': _mcp_columns,
    'mllp-channel': _mllp_columns,
    'mllp-outgoing': _mllp_columns,
    'fhir': _fhir_columns,
    'scheduler': _scheduler_columns,
    'llm': _llm_columns,
    'config': _config_columns,
    'odoo': _odoo_columns,
    'microsoft-cloud': _microsoft_cloud_columns,
    'microsoft-health': _microsoft_health_columns,
    'certificate': _certificate_columns,
    'test-transfer': _test_transfer_columns,
}

# ################################################################################################################################
# ################################################################################################################################

# Per-source attr columns - these render as columns of their own, read out of the event_attr
# table in one query per page, and the free-text search covers them through the attr-to-cid shape.
_source_attr_columns = source_attr_names

# The sources whose payloads live in the event_body table rather than the data column.
_source_body_preview = {'mllp-channel', 'mllp-outgoing'}

# ################################################################################################################################
# ################################################################################################################################

# What outcomes a source's events report, which is what the listing offers as filters. Everything
# that carries a message reports whether it went through or failed ..
_default_outcomes = (AuditOutcome.OK, AuditOutcome.Error)

# .. and a pushed pub/sub message may also run out of time before it can be delivered, which is
# an outcome of its own and one no other source can report.
_source_outcomes = {
    'pubsub': (AuditOutcome.OK, AuditOutcome.Error, AuditOutcome.Expired),

    # A scheduler run is running until it completes, and it may also overrun its execution
    # time limit, which no message-carrying source can.
    'scheduler': (SCHEDULER.OUTCOME.RUNNING, SCHEDULER.OUTCOME.OK, SCHEDULER.OUTCOME.ERROR, SCHEDULER.OUTCOME.TIMEOUT),
}

# The all-events page can show anything any source reports, so it offers every outcome there is.
_all_outcomes = (AuditOutcome.OK, AuditOutcome.Error, AuditOutcome.Expired)

# ################################################################################################################################
# ################################################################################################################################

def _get_outcomes(source:'str') -> 'strtuple':
    """ Returns the outcomes the source's events report. An empty source is the all-events page.
    """
    if source == '':
        out = _all_outcomes
    elif source_outcomes := _source_outcomes.get(source):
        out = source_outcomes
    else:
        out = _default_outcomes

    return out

# ################################################################################################################################
# ################################################################################################################################
