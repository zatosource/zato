# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.audit_log.common import AuditEvent, AuditSource

# ################################################################################################################################
# ################################################################################################################################

# What the all-events page - the one no source narrows down - calls itself and its section.
_all_sources_title = 'Audit log'
_all_sources_section_title = 'All sources'

# What each source is called in the filter selects of the all-events page.
# Every member of AuditSource is here, in the order the selects offer them.
_source_label = {
    AuditSource.AS2: 'AS2',
    AuditSource.AS4: 'AS4',
    AuditSource.Certificate: 'Certificate checks',
    AuditSource.Email_IMAP: 'IMAP',
    AuditSource.Email_SMTP: 'SMTP',
    AuditSource.FHIR: 'FHIR outgoing',
    AuditSource.File_Outgoing: 'File transfer',
    AuditSource.LLM: 'LLM',
    AuditSource.Config: 'Log access',
    AuditSource.MCP: 'MCP',
    AuditSource.Microsoft_Cloud: 'Microsoft cloud',
    AuditSource.Microsoft_Health: 'Microsoft health',
    AuditSource.MLLP_Channel: 'MLLP channels',
    AuditSource.MLLP_Outgoing: 'MLLP outgoing',
    AuditSource.Odoo: 'Odoo',
    AuditSource.PubSub: 'Pub/sub',
    AuditSource.REST_Channel: 'REST channels',
    AuditSource.REST_Outgoing: 'REST outgoing',
    AuditSource.REST_Outgoing_Health: 'REST checks',
    AuditSource.Scheduler: 'Scheduler',
    AuditSource.SOAP_Channel: 'SOAP channels',
    AuditSource.SOAP_Outgoing: 'SOAP outgoing',
    AuditSource.SOAP_Outgoing_Health: 'SOAP checks',
    AuditSource.SQL_Outgoing: 'SQL',
    AuditSource.Test_Transfer: 'Test transfers',
    AuditSource.X12: 'X12',
}

# How each source's name reads in the middle of a sentence - the "All except .." badge
# of the source filter. Only the sources whose label changes its casing there are here.
_source_except_label = {
    AuditSource.Certificate: 'certificate checks',
    AuditSource.Config: 'log access',
    AuditSource.File_Outgoing: 'file transfer',
    AuditSource.PubSub: 'pub/sub',
    AuditSource.Scheduler: 'scheduler',
    AuditSource.Test_Transfer: 'test transfers',
}

# What one event's source is called on a row and in the detail pane.
_source_event_label = {
    AuditSource.Config: 'Log access',
    AuditSource.AS2: 'AS2',
    AuditSource.AS4: 'AS4',
    AuditSource.Certificate: 'Certificate check',
    AuditSource.Email_IMAP: 'IMAP',
    AuditSource.Email_SMTP: 'SMTP',
    AuditSource.FHIR: 'FHIR outgoing',
    AuditSource.File_Outgoing: 'File transfer',
    AuditSource.LLM: 'LLM',
    AuditSource.MCP: 'MCP',
    AuditSource.Microsoft_Cloud: 'Microsoft cloud',
    AuditSource.Microsoft_Health: 'Microsoft health',
    AuditSource.MLLP_Channel: 'MLLP channel',
    AuditSource.MLLP_Outgoing: 'MLLP outgoing',
    AuditSource.Odoo: 'Odoo',
    AuditSource.PubSub: 'Pub/sub',
    AuditSource.REST_Channel: 'REST channel',
    AuditSource.REST_Outgoing: 'REST outgoing',
    AuditSource.REST_Outgoing_Health: 'REST check',
    AuditSource.Scheduler: 'Scheduler',
    AuditSource.SOAP_Channel: 'SOAP channel',
    AuditSource.SOAP_Outgoing: 'SOAP outgoing',
    AuditSource.SOAP_Outgoing_Health: 'SOAP check',
    AuditSource.SQL_Outgoing: 'SQL',
    AuditSource.Test_Transfer: 'Test transfer',
    AuditSource.X12: 'X12',
}

# What the object of each source is called in the detail pane.
_source_object_label = {
    AuditSource.Config: 'Screen',
    AuditSource.AS2: 'Partner',
    AuditSource.AS4: 'Partner',
    AuditSource.Certificate: 'Connection',
    AuditSource.Email_IMAP: 'Connection',
    AuditSource.Email_SMTP: 'Connection',
    AuditSource.FHIR: 'Connection',
    AuditSource.File_Outgoing: 'Connection',
    AuditSource.LLM: 'Connection',
    AuditSource.MCP: 'Channel',
    AuditSource.Microsoft_Cloud: 'Connection',
    AuditSource.Microsoft_Health: 'Service',
    AuditSource.MLLP_Channel: 'Channel',
    AuditSource.MLLP_Outgoing: 'Connection',
    AuditSource.Odoo: 'Connection',
    AuditSource.PubSub: 'Topic',
    AuditSource.REST_Channel: 'Channel',
    AuditSource.REST_Outgoing: 'Connection',
    AuditSource.REST_Outgoing_Health: 'Connection',
    AuditSource.Scheduler: 'Job',
    AuditSource.SOAP_Channel: 'Channel',
    AuditSource.SOAP_Outgoing: 'Connection',
    AuditSource.SOAP_Outgoing_Health: 'Connection',
    AuditSource.SQL_Outgoing: 'Connection',
    AuditSource.Test_Transfer: 'Connection',
    AuditSource.X12: 'Partner',
}

# What each source writes into an event's endpoint, called by what it is.
# A source the map does not know keeps the plain Endpoint word.
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
    AuditSource.Microsoft_Cloud: 'Request',
    AuditSource.Certificate: 'Address',
}

# How one event type reads on the screen - every member of AuditEvent is here,
# and an event type the map does not know is shown by its own raw name.
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
    AuditEvent.MCP_Prompts_List: 'MCP prompts list',
    AuditEvent.MCP_Prompts_Get: 'MCP prompts get',
    AuditEvent.MCP_Session_Delete: 'MCP session delete',
    AuditEvent.MCP_Discover: 'MCP discover',
    AuditEvent.Bulk_Resubmit: 'Bulk resubmit',
    AuditEvent.Config_Created: 'Config created',
    AuditEvent.Config_Edited: 'Config edited',
    AuditEvent.Config_Deleted: 'Config deleted',
    AuditEvent.Content_Viewed: 'Content viewed',
    AuditEvent.Job_Executed: 'Job executed',
    AuditEvent.Auth_Failed: 'Auth failed',
    AuditEvent.File_Claimed: 'File claimed',
    AuditEvent.File_Acked: 'File acked',
    AuditEvent.Run_Completed: 'Run completed',
    AuditEvent.Cert_Checked: 'Certificate checked',
    AuditEvent.Health_Checked: 'Health checked',
    AuditEvent.Test_Transfer_Executed: 'Test transfer executed',
}

# Per-source page titles - every member of AuditSource has one.
_source_title = {
    'pubsub': 'Pub/sub audit log',
    'rest-channel': 'REST channel audit log',
    'soap-channel': 'SOAP channel audit log',
    'rest-outgoing': 'Outgoing REST audit log',
    'soap-outgoing': 'Outgoing SOAP audit log',
    'rest-outgoing-health': 'REST check audit log',
    'soap-outgoing-health': 'SOAP check audit log',
    'email-imap': 'IMAP audit log',
    'email-smtp': 'SMTP audit log',
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
    'config': 'Log access audit log',
    'odoo': 'Odoo audit log',
    'microsoft-cloud': 'Microsoft cloud audit log',
    'microsoft-health': 'Microsoft health audit log',
    'certificate': 'Certificate check audit log',
    'test-transfer': 'Test transfer audit log',
}

# ################################################################################################################################
# ################################################################################################################################
