# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

What each source's audit log page looks like - its title, the columns of its table, the attrs that
render as columns of their own, the outcomes its events report, and the ceilings the page itself
is bounded by.
"""

# Zato
from zato.common.api import SCHEDULER
from zato.common.audit_log.common import AuditEvent, AuditOutcome, AuditSource
from zato.common.defaults import default_cluster_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strtuple
    strtuple = strtuple

# ################################################################################################################################
# ################################################################################################################################

_poll_url = '/zato/audit-log/poll/'

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

# The free-text search covers these columns - every one the detail pane offers a Search beside,
# so no value shown as searchable comes back with nothing
_search_columns = ('data', 'event_type', 'msg_id', 'correl_id', 'endpoint', 'ext_client_id',
    'status', 'classification')

# The status query parameter value narrowing the page down to open exchanges
_status_outstanding = 'outstanding'

# ################################################################################################################################
# ################################################################################################################################

# What the all-events page - the one no source narrows down - calls itself and its section
_all_sources_title = 'Audit log'
_all_sources_section_title = 'All sources'

# What each source is called where one word has to do - the filter selects of the
# all-events page. Every member of AuditSource is here, in the order the selects
# offer them, so every source there can be is on offer whether or not it has
# written anything yet. The config source is the log access record - who read what,
# when and from which screen.
_source_label = {
    AuditSource.AS2: 'AS2',
    AuditSource.AS4: 'AS4',
    AuditSource.Email_IMAP: 'IMAP',
    AuditSource.Email_SMTP: 'SMTP',
    AuditSource.FHIR: 'FHIR outgoing',
    AuditSource.File_Outgoing: 'File transfer',
    AuditSource.LLM: 'LLM',
    AuditSource.Config: 'Log access',
    AuditSource.MCP: 'MCP',
    AuditSource.MLLP_Channel: 'MLLP channels',
    AuditSource.MLLP_Outgoing: 'MLLP outgoing',
    AuditSource.PubSub: 'Pub/sub',
    AuditSource.REST_Channel: 'REST channels',
    AuditSource.REST_Outgoing: 'REST outgoing',
    AuditSource.REST_Outgoing_Health: 'REST checks',
    AuditSource.Scheduler: 'Scheduler',
    AuditSource.SOAP_Channel: 'SOAP channels',
    AuditSource.SOAP_Outgoing: 'SOAP outgoing',
    AuditSource.SOAP_Outgoing_Health: 'SOAP checks',
    AuditSource.SQL_Outgoing: 'SQL',
    AuditSource.X12: 'X12',
}

# How each source's name reads in the middle of a sentence - the "All except .." badge
# of the source filter. Only the sources whose label changes its casing there are here -
# a label led by an acronym, AS2 or REST, reads the same wherever it stands.
_source_except_label = {
    AuditSource.Config: 'log access',
    AuditSource.File_Outgoing: 'file transfer',
    AuditSource.PubSub: 'pub/sub',
    AuditSource.Scheduler: 'scheduler',
}

# What one event's source is called on a row and in the detail pane - singular where
# the filter select's group name is plural, because a row is one event of one object
_source_event_label = {
    AuditSource.Config: 'Log access',
    AuditSource.AS2: 'AS2',
    AuditSource.AS4: 'AS4',
    AuditSource.Email_IMAP: 'IMAP',
    AuditSource.Email_SMTP: 'SMTP',
    AuditSource.FHIR: 'FHIR outgoing',
    AuditSource.File_Outgoing: 'File transfer',
    AuditSource.LLM: 'LLM',
    AuditSource.MCP: 'MCP',
    AuditSource.MLLP_Channel: 'MLLP channel',
    AuditSource.MLLP_Outgoing: 'MLLP outgoing',
    AuditSource.PubSub: 'Pub/sub',
    AuditSource.REST_Channel: 'REST channel',
    AuditSource.REST_Outgoing: 'REST outgoing',
    AuditSource.REST_Outgoing_Health: 'REST check',
    AuditSource.Scheduler: 'Scheduler',
    AuditSource.SOAP_Channel: 'SOAP channel',
    AuditSource.SOAP_Outgoing: 'SOAP outgoing',
    AuditSource.SOAP_Outgoing_Health: 'SOAP check',
    AuditSource.SQL_Outgoing: 'SQL',
    AuditSource.X12: 'X12',
}

# What the object of each source is called - the word its detail pane row is labelled
# with, so the pane says "Channel" or "Topic" rather than a word that names nothing
_source_object_label = {
    AuditSource.Config: 'Screen',
    AuditSource.AS2: 'Partner',
    AuditSource.AS4: 'Partner',
    AuditSource.Email_IMAP: 'Connection',
    AuditSource.Email_SMTP: 'Connection',
    AuditSource.FHIR: 'Connection',
    AuditSource.File_Outgoing: 'Connection',
    AuditSource.LLM: 'Connection',
    AuditSource.MCP: 'Channel',
    AuditSource.MLLP_Channel: 'Channel',
    AuditSource.MLLP_Outgoing: 'Connection',
    AuditSource.PubSub: 'Topic',
    AuditSource.REST_Channel: 'Channel',
    AuditSource.REST_Outgoing: 'Connection',
    AuditSource.REST_Outgoing_Health: 'Connection',
    AuditSource.Scheduler: 'Job',
    AuditSource.SOAP_Channel: 'Channel',
    AuditSource.SOAP_Outgoing: 'Connection',
    AuditSource.SOAP_Outgoing_Health: 'Connection',
    AuditSource.SQL_Outgoing: 'Connection',
    AuditSource.X12: 'Partner',
}

# Where each source's own main page is - what the source's name in the detail pane
# leads to. A source with no page of its own is not here and its name stays text.
_source_page_url = {
    AuditSource.Scheduler: f'/zato/scheduler/dashboard/?cluster={default_cluster_id}&range=0',
    AuditSource.REST_Channel: f'/zato/http-soap/?cluster={default_cluster_id}&connection=channel&transport=plain_http',
    AuditSource.SOAP_Channel: f'/zato/http-soap/?cluster={default_cluster_id}&connection=channel&transport=soap',
    AuditSource.REST_Outgoing: f'/zato/http-soap/?cluster={default_cluster_id}&connection=outgoing&transport=plain_http',
    AuditSource.SOAP_Outgoing: f'/zato/http-soap/?cluster={default_cluster_id}&connection=outgoing&transport=soap',

    # A check's object is the connection it watches, so both lead where the connection is
    AuditSource.REST_Outgoing_Health:
        f'/zato/http-soap/?cluster={default_cluster_id}&connection=outgoing&transport=plain_http',
    AuditSource.SOAP_Outgoing_Health: f'/zato/http-soap/?cluster={default_cluster_id}&connection=outgoing&transport=soap',

    AuditSource.MLLP_Channel: f'/zato/channel/hl7/mllp/?cluster={default_cluster_id}',
    AuditSource.MLLP_Outgoing: f'/zato/outgoing/hl7/mllp/?cluster={default_cluster_id}',
    AuditSource.FHIR: f'/zato/outgoing/hl7/fhir/?cluster={default_cluster_id}',
    AuditSource.SQL_Outgoing: f'/zato/outgoing/sql/?cluster={default_cluster_id}',
    AuditSource.Email_IMAP: f'/zato/email/imap/?cluster={default_cluster_id}',
    AuditSource.Email_SMTP: f'/zato/email/smtp/?cluster={default_cluster_id}',
    AuditSource.PubSub: f'/zato/pubsub/topic/?cluster={default_cluster_id}',
    AuditSource.File_Outgoing: f'/zato/outgoing/ftp/?cluster={default_cluster_id}',
    AuditSource.LLM: f'/zato/outgoing/llm/?cluster={default_cluster_id}&type_=outconn-llm',
}

# Where one object's own page is - the source's page opened on that object.
# `{name}` is filled in with the object's name on the frontend. Built out of the
# base map above so the two can never drift apart.
_object_page_url = {source: f'{url}&query={{name}}' for source, url in _source_page_url.items()}

# A scheduler job's own page is the classic scheduler listing filtered down to it -
# the dashboard's job detail page is keyed by a numeric id no event name carries.
_object_page_url[AuditSource.Scheduler] = f'/zato/scheduler/?cluster={default_cluster_id}&query={{name}}'

# Where what a source writes into an event's endpoint leads. REST and SOAP channels
# and the scheduler record the service the message or run was handed to, and a service
# has a page - an outgoing URL, a folder or a host address does not, so no other
# source is here.
_endpoint_page_url = {
    AuditSource.REST_Channel: f'/zato/service/?cluster={default_cluster_id}&query={{name}}',
    AuditSource.SOAP_Channel: f'/zato/service/?cluster={default_cluster_id}&query={{name}}',
    AuditSource.Scheduler: f'/zato/service/?cluster={default_cluster_id}&query={{name}}',
}

# Where one run of a scheduled job has its own page - the scheduler dashboard's run detail
# screen, keyed by the job's numeric id and the run's number. `{job_id}` and `{run}` are
# filled in on the frontend out of the event's own attrs.
_run_page_url = {
    AuditSource.Scheduler:
        f'/zato/scheduler/dashboard/job/{{job_id}}/run/{{run}}/?cluster={default_cluster_id}&range=0&outcomes=all',
}

# What each source writes into an event's endpoint, called by what it is - the service
# a channel hands its messages to, the folder a mailbox was read from, the database
# a query ran against. A source the map does not know keeps the plain Endpoint word.
_source_endpoint_label = {
    AuditSource.REST_Channel: 'Service',
    AuditSource.SOAP_Channel: 'Service',
    AuditSource.Scheduler: 'Service',
    AuditSource.REST_Outgoing: 'Address',
    AuditSource.SOAP_Outgoing: 'Address',
    AuditSource.REST_Outgoing_Health: 'Address',
    AuditSource.SOAP_Outgoing_Health: 'Address',
    AuditSource.Email_IMAP: 'Folder',
    AuditSource.Email_SMTP: 'Address',
    AuditSource.SQL_Outgoing: 'Database',
    AuditSource.File_Outgoing: 'Remote path',
    AuditSource.MCP: 'Tool',
    AuditSource.MLLP_Channel: 'Address',
    AuditSource.MLLP_Outgoing: 'Address',
    AuditSource.FHIR: 'Request',
    AuditSource.LLM: 'Address',
}

# How one event type reads on the screen - every member of AuditEvent is here,
# and an event type the map does not know is shown by its own raw name
_event_type_label = {
    AuditEvent.Published: 'Published',
    AuditEvent.Delivered: 'Delivered',
    AuditEvent.Delivery_Failed: 'Delivery failed',
    AuditEvent.Expired: 'Expired',
    AuditEvent.Received: 'Received',
    AuditEvent.Request_Received: 'Request received',
    AuditEvent.Response_Sent: 'Response sent',
    AuditEvent.Request_Sent: 'Request sent',
    AuditEvent.Response_Received: 'Response received',
    AuditEvent.Message_Received: 'Message received',
    AuditEvent.Message_Marked_Seen: 'Message marked seen',
    AuditEvent.Message_Deleted: 'Message deleted',
    AuditEvent.Interchange_Sent: 'Interchange sent',
    AuditEvent.Interchange_Received: 'Interchange received',
    AuditEvent.Ack_Sent: 'ACK sent',
    AuditEvent.Ack_Received: 'ACK received',
    AuditEvent.Message_Sent: 'Message sent',
    AuditEvent.MDN_Sent: 'MDN sent',
    AuditEvent.MDN_Received: 'MDN received',
    AuditEvent.Receipt_Sent: 'Receipt sent',
    AuditEvent.Receipt_Received: 'Receipt received',
    AuditEvent.Alert_Raised: 'Alert raised',
    AuditEvent.Alert_Diagnosed: 'Alert diagnosed',
    AuditEvent.MCP_Initialize: 'MCP initialize',
    AuditEvent.MCP_Tools_List: 'MCP tools list',
    AuditEvent.MCP_Tools_Call: 'MCP tools call',
    AuditEvent.MCP_Session_Delete: 'MCP session delete',
    AuditEvent.MCP_Discover: 'MCP discover',
    AuditEvent.Bulk_Resubmit: 'Bulk resubmit',
    AuditEvent.Config_Created: 'Config created',
    AuditEvent.Config_Edited: 'Config edited',
    AuditEvent.Config_Deleted: 'Config deleted',
    AuditEvent.Content_Viewed: 'Content viewed',
    AuditEvent.Job_Executed: 'Job executed',
    AuditEvent.Auth_Failed: 'Auth failed',
}

# Per-source page titles - more sources will follow, e.g. REST outgoing connections
_source_title = {
    'pubsub': 'Pub/sub audit log',
    'rest-channel': 'REST channel audit log',
    'soap-channel': 'SOAP channel audit log',
    'rest-outgoing': 'Outgoing REST audit log',
    'soap-outgoing': 'Outgoing SOAP audit log',
    'rest-outgoing-health': 'REST check audit log',
    'soap-outgoing-health': 'SOAP check audit log',
    'email-imap': 'IMAP audit log',
    'file-outgoing': 'File transfer audit log',
    'sql-outgoing': 'SQL audit log',
    'as2': 'AS2 audit log',
    'as4': 'AS4 audit log',
    'x12': 'X12 audit log',
    'mcp': 'MCP audit log',
    'mllp-channel': 'MLLP channel audit log',
    'mllp-outgoing': 'Outgoing MLLP audit log',
    'fhir': 'FHIR audit log',
    'scheduler': 'Scheduler audit log',
    'llm': 'LLM audit log',
}

# Each column tells the frontend which row key to read, what header label to show
# and how to render the cell - the types are implemented in audit-log.js
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
    {'key': 'endpoint', 'label': 'Remote path', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
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

# The all-events page - every source in one listing - reads each row by the columns
# every source shares, plus the source itself, which a single-source page never says
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

# Per-source table columns
_source_columns = {
    'pubsub': _pubsub_columns,
    'rest-channel': _rest_channel_columns,
    'soap-channel': _soap_channel_columns,
    'rest-outgoing': _rest_outgoing_columns,
    'soap-outgoing': _soap_outgoing_columns,

    # A check writes what a call writes, through the same writer, so its rows have the same shape
    'rest-outgoing-health': _rest_outgoing_columns,
    'soap-outgoing-health': _soap_outgoing_columns,
    'email-imap': _email_imap_columns,
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
}

# ################################################################################################################################
# ################################################################################################################################

# Per-source attr columns - these render as columns of their own, read out of the event_attr
# table in one query per page, and the free-text search covers them through the attr-to-cid shape.
_source_attr_columns = {
    'mllp-channel': ('msg_type', 'mrn', 'facility', 'ack_status'),
    'mllp-outgoing': ('msg_type', 'mrn', 'facility', 'ack_status'),
    'fhir': ('resource_type', 'method'),
    'scheduler': ('current_run', 'delay_ms', 'job_id'),

    # Who viewed what - a view record is named by these two rather than by an event id
    'config': ('actor', 'viewed_object_name'),
}

# The sources whose payloads live in the event_body table rather than the data column
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

# The all-events page can show anything any source reports, so it offers every outcome there is
_all_outcomes = (AuditOutcome.OK, AuditOutcome.Error, AuditOutcome.Expired)

# ################################################################################################################################

def _get_outcomes(source:'str') -> 'strtuple':
    """ Returns the outcomes this source's events report, so that a page offers filters for
    the outcomes it can actually show and for no others. An empty source is the all-events
    page, whose rows may report anything any source can.
    """
    if source == '':
        return _all_outcomes

    if source in _source_outcomes:
        out = _source_outcomes[source]
        return out

    return _default_outcomes

# ################################################################################################################################
# ################################################################################################################################
