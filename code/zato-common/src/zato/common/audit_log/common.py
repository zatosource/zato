# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from http.client import BAD_GATEWAY, BAD_REQUEST, FORBIDDEN, GATEWAY_TIMEOUT, NOT_FOUND, REQUEST_TIMEOUT, \
    SERVICE_UNAVAILABLE, TOO_MANY_REQUESTS, UNAUTHORIZED, UNPROCESSABLE_ENTITY

# SQLAlchemy
from sqlalchemy import BigInteger, Column, Index, Integer, MetaData, Numeric, String, Table, Text

# ################################################################################################################################
# ################################################################################################################################

# The name of the SQLite file holding all audit events, shared by all sources
Audit_DB_File_Name = 'audit.db'

# The environment variable overriding how many days of events are kept
Env_Retention_Days = 'Zato_Audit_Log_Retention_Days'

# What one source's own retention variable is prefixed with - the source name in upper case
# with dashes turned into underscores completes it, e.g. Zato_Audit_Log_Retention_Days_AS2.
Env_Retention_Days_Prefix = 'Zato_Audit_Log_Retention_Days_'

# How many days of events are kept when the environment does not say otherwise
_default_retention_days = 30

# How many days the B2B sources are kept for. What a partner sent and what it signed for is the
# evidence a trade dispute is settled with, and disputes surface years after the exchange,
# so the sources that carry non-repudiation evidence outlive the debug events by default.
_default_evidence_retention_days = 7 * 365

# How many days a health check's own events are kept for. A check running every ten seconds writes
# more rows in a day than most connections carry in a month, and a ping that answered a week ago
# tells nobody anything, so these age out well before the traffic events do.
_default_health_check_retention_days = 7

# Maximum length of short string columns
_short_column_len = 255

# Maximum length of the endpoint column - it may hold full addresses
_endpoint_column_len = 500

# Attribute values are capped so they always fit an indexable column
Attr_Value_Max_Len = _short_column_len

# ################################################################################################################################

class AuditSource:
    PubSub        = 'pubsub'
    REST_Channel  = 'rest-channel'
    SOAP_Channel  = 'soap-channel'
    REST_Outgoing = 'rest-outgoing'
    SOAP_Outgoing = 'soap-outgoing'
    Email_IMAP    = 'email-imap'
    Email_SMTP    = 'email-smtp'
    File_Outgoing = 'file-outgoing'
    SQL_Outgoing  = 'sql-outgoing'
    AS2           = 'as2'
    AS4           = 'as4'
    X12           = 'x12'
    MCP           = 'mcp'
    MLLP_Channel  = 'mllp-channel'
    MLLP_Outgoing = 'mllp-outgoing'
    FHIR          = 'fhir'
    Config        = 'config'
    Scheduler     = 'scheduler'
    LLM           = 'llm'
    Odoo          = 'odoo'

    # One source for all the Microsoft cloud services - 365, Teams, OneDrive,
    # SharePoint, Power Automate and Fabric - the object name says which connection spoke.
    Microsoft_Cloud = 'microsoft-cloud'

    # An outgoing connection's own health check writes here rather than to the connection's
    # traffic source, under the same object name, so what a check measures is counted apart
    # from what the connection's real calls measure.
    REST_Outgoing_Health = 'rest-outgoing-health'
    SOAP_Outgoing_Health = 'soap-outgoing-health'

    # The probe sources - the default scheduler jobs that measure what no
    # per-call event can, writing ordinary audit events the collectors read.
    Certificate      = 'certificate'
    Microsoft_Health = 'microsoft-health'
    Test_Transfer    = 'test-transfer'

# ################################################################################################################################

# What tells a check's event or measure from the connection's own.
health_sources = {AuditSource.REST_Outgoing_Health, AuditSource.SOAP_Outgoing_Health}

# ################################################################################################################################

# What each source is called in a sentence a person reads, an alert message above all. The code
# an event carries is what the tables are keyed by, not a name anyone should have to read.
_source_label = {
    AuditSource.PubSub: 'Pub/sub',
    AuditSource.REST_Channel: 'REST channel',
    AuditSource.SOAP_Channel: 'SOAP channel',
    AuditSource.REST_Outgoing: 'REST outgoing',
    AuditSource.SOAP_Outgoing: 'SOAP outgoing',
    AuditSource.REST_Outgoing_Health: 'REST check',
    AuditSource.SOAP_Outgoing_Health: 'SOAP check',
    AuditSource.Email_IMAP: 'IMAP',
    AuditSource.Email_SMTP: 'SMTP',
    AuditSource.File_Outgoing: 'File transfer',
    AuditSource.SQL_Outgoing: 'SQL',
    AuditSource.AS2: 'AS2',
    AuditSource.AS4: 'AS4',
    AuditSource.X12: 'X12',
    AuditSource.MCP: 'MCP',
    AuditSource.MLLP_Channel: 'MLLP channel',
    AuditSource.MLLP_Outgoing: 'MLLP outgoing',
    AuditSource.FHIR: 'FHIR outgoing',
    AuditSource.Config: 'Log access',
    AuditSource.Scheduler: 'Scheduler',
    AuditSource.LLM: 'LLM',
    AuditSource.Odoo: 'Odoo',
    AuditSource.Microsoft_Cloud: 'Microsoft cloud',
    AuditSource.Certificate: 'Certificate',
    AuditSource.Microsoft_Health: 'Microsoft health',
    AuditSource.Test_Transfer: 'Test transfer',
}

# ################################################################################################################################

def get_source_label(source:'str') -> 'str':
    """ What one source is called in a sentence.
    """
    out = _source_label[source]
    return out

# ################################################################################################################################

# The sources kept for something other than the usual span, with how long each is kept for.
_source_retention_days = {
    AuditSource.AS2: _default_evidence_retention_days,
    AuditSource.AS4: _default_evidence_retention_days,
    AuditSource.X12: _default_evidence_retention_days,
    AuditSource.REST_Outgoing_Health: _default_health_check_retention_days,
    AuditSource.SOAP_Outgoing_Health: _default_health_check_retention_days,
}

# ################################################################################################################################

def get_source_env_suffix(source:'str') -> 'str':
    """ Turns one source name into the tail of its own environment variable - the name in upper case
    with the dashes that read well in a source name turned into the underscores a variable needs.
    """
    out = source.replace('-', '_').upper()
    return out

# ################################################################################################################################

def get_retention_days(source:'str' = '') -> 'int':
    """ Returns how many days of audit events are kept, for one source or, with no source named,
    process-wide - the latter is also the widest window the reports run over.

    A source's own environment variable comes first, then the source's own default, and only then
    the process-wide setting. The order is deliberate: an operator shortening retention across the
    board is asking for less diagnostic history, not for the evidence of what a partner signed for
    to be deleted, and that decision has to be made for the source it concerns by name.
    """
    if source:

        suffix = get_source_env_suffix(source)
        env_name = f'{Env_Retention_Days_Prefix}{suffix}'

        if value := os.environ.get(env_name, ''):
            out = int(value)
            return out

        if source in _source_retention_days:
            out = _source_retention_days[source]
            return out

    if value := os.environ.get(Env_Retention_Days, ''):
        out = int(value)
        return out

    out = _default_retention_days
    return out

# ################################################################################################################################

class AuditEvent:
    Published            = 'published'
    Delivered            = 'delivered'
    Delivery_Failed      = 'delivery-failed'
    Expired              = 'expired'
    Received             = 'received'
    Request_Received     = 'request-received'
    Response_Sent        = 'response-sent'
    Request_Sent         = 'request-sent'
    Response_Received    = 'response-received'
    Message_Received     = 'message-received'
    Message_Marked_Seen  = 'message-marked-seen'
    Message_Deleted      = 'message-deleted'
    Interchange_Sent     = 'interchange-sent'
    Interchange_Received = 'interchange-received'
    Ack_Sent             = 'ack-sent'
    Ack_Received         = 'ack-received'
    Message_Sent         = 'message-sent'
    MDN_Sent             = 'mdn-sent'
    MDN_Received         = 'mdn-received'
    Receipt_Sent         = 'receipt-sent'
    Receipt_Received     = 'receipt-received'
    Alert_Raised         = 'alert-raised'
    Alert_Diagnosed      = 'alert-diagnosed'
    MCP_Initialize       = 'mcp-initialize'
    MCP_Tools_List       = 'mcp-tools-list'
    MCP_Tools_Call       = 'mcp-tools-call'
    MCP_Prompts_List     = 'mcp-prompts-list'
    MCP_Prompts_Get      = 'mcp-prompts-get'
    MCP_Session_Delete   = 'mcp-session-delete'
    MCP_Discover         = 'mcp-discover'
    Bulk_Resubmit        = 'bulk-resubmit'
    Config_Created       = 'config-created'
    Config_Edited        = 'config-edited'
    Config_Deleted       = 'config-deleted'
    Content_Viewed       = 'content-viewed'
    Job_Executed         = 'job-executed'

    # What a file transfer schedule writes about each file it takes and about
    # each of its runs - the claim rename, the move or delete after success
    # and the per-run summary with its counts.
    File_Claimed         = 'file-claimed'
    File_Acked           = 'file-acked'
    Run_Completed        = 'run-completed'

    # A call that failed on credentials rather than networking - its own type
    # because its remedy is different, so alerting counts it separately.
    Auth_Failed          = 'auth-failed'

    # What the probe jobs write - a certificate's days left, a remote service's
    # own health state and a test transfer's outcome.
    Cert_Checked           = 'cert-checked'
    Health_Checked         = 'health-checked'
    Test_Transfer_Executed = 'test-transfer-executed'

# ################################################################################################################################

class AuditOutcome:
    OK      = 'ok'
    Error   = 'error'
    Expired = 'expired'

# ################################################################################################################################

class AuditBody:
    """ The kinds of message bodies an event may carry - what was sent, what came back,
    what the other side said when it failed, and the files that travelled with the message.
    """
    Request    = 'request'
    Response   = 'response'
    Error      = 'error'
    Attachment = 'attachment'
    SQL_Rows   = 'sql-rows'

# ################################################################################################################################

class AuditClassification:
    """ Whether a failure can be resubmitted as-is (transient), needs its message changed first (permanent),
    or needs a human decision (operator-fixable).
    """
    Transient        = 'transient'
    Permanent        = 'permanent'
    Operator_Fixable = 'operator-fixable'

# ################################################################################################################################

class AuditLink:
    """ How one event relates to its parent events - lineage allows multiple parents
    because aggregation produces one message out of many.
    """
    Resubmit_Of     = 'resubmit-of'
    Batch_Item_Of   = 'batch-item-of'
    Aggregated_From = 'aggregated-from'

# ################################################################################################################################
# ################################################################################################################################

# The one table holding all audit events, portable across SQLite, MySQL, PostgreSQL and Oracle DB.
# Short columns are VARCHAR because MySQL cannot index TEXT columns without a prefix length.
metadata = MetaData()

# Event identifiers are 64-bit, except under SQLite where the autoincrement
# primary key must be a plain INTEGER to become an alias of the built-in rowid.
_big_id_column = BigInteger()
_sqlite_id_column = Integer()
_id_column_type = _big_id_column.with_variant(_sqlite_id_column, 'sqlite')

# The column types the tables below are built out of, named once so no table definition
# needs an inner call of its own.
_short_column = String(_short_column_len)
_endpoint_column = String(_endpoint_column_len)
_attr_number_column = Numeric(20, 6, asdecimal=False)

# How much of a short column an index spans when a whole one would not fit. MySQL caps a key
# at 3072 bytes, which four full-width utf8mb4 columns overrun, and rule, source, object
# and kind names all tell themselves apart well inside this many characters.
_index_prefix_len = 64

# ################################################################################################################################

_event_columns = [
    Column('id', _id_column_type, primary_key=True, autoincrement=True),
    Column('cid', _short_column),
    Column('cid_sequence', Integer),
    Column('source', _short_column),
    Column('event_type', _short_column),
    Column('object_name', _short_column),
    Column('msg_id', _short_column),
    Column('correl_id', _short_column),
    Column('ext_client_id', _short_column),
    Column('pub_time_iso', _short_column),
    Column('event_time_iso', _short_column),
    Column('server_name', _short_column),
    Column('endpoint', _endpoint_column),
    Column('sub_key', _short_column),
    Column('size', Integer),
    Column('priority', Integer),
    Column('outcome', _short_column),
    Column('application_outcome', _short_column),
    Column('classification', _short_column),
    Column('status', _short_column),
    Column('duration_ms', Integer),
    Column('data', Text),
    Index('idx_event_source_object', 'source', 'object_name', 'id'),

    # One object's events are read newest first by the time they happened rather than by the
    # order they were written in, and a page of them is one window of that order - without
    # this the whole of an object's history would be sorted to answer for a single page.
    Index('idx_event_source_object_time', 'source', 'object_name', 'event_time_iso'),

    Index('idx_event_cid', 'cid', 'id'),
    Index('idx_event_msg_id', 'msg_id', 'id'),

    # A resubmission names the event it was born from by that event's cid, so reading a message's
    # flow asks which events point back at the cids it already holds - the only correlation
    # question of the four with no index of its own behind it.
    Index('idx_event_correl_id', 'correl_id', 'id'),

    # The reconciliation queries ask for the open events of one source before a moment in time -
    # every message whose receipt has not arrived - and the msg_id index above covers only the
    # lookup of the closing event, leaving the outer half of that question a full scan.
    Index('idx_event_source_type_time', 'source', 'event_type', 'event_time_iso'),
]

event_table = Table('event', metadata, *_event_columns)

# ################################################################################################################################

# Searchable attributes - any source declares indexed search fields with no schema changes.
# Values are stored as capped text, and numbers additionally go to a numeric column
# so aggregation queries can sum and group without casting.
_event_attr_columns = [
    Column('id', _id_column_type, primary_key=True, autoincrement=True),
    Column('event_id', BigInteger),
    Column('name', _short_column),
    Column('value', _short_column),
    Column('value_number', _attr_number_column),
    Index('idx_event_attr_event', 'event_id'),
    Index('idx_event_attr_name_value', 'name', 'value'),
    Index('idx_event_attr_name_number', 'name', 'value_number'),
]

event_attr_table = Table('event_attr', metadata, *_event_attr_columns)

# ################################################################################################################################

# Message bodies live in their own table referenced from event rows - metadata inserts stay small
# and pruning content is a bulk delete here rather than column surgery on the event table.
# The event time is denormalized so pruning never needs a join.
_event_body_columns = [
    Column('id', _id_column_type, primary_key=True, autoincrement=True),
    Column('event_id', BigInteger),
    Column('kind', _short_column),
    Column('event_time_iso', _short_column),
    Column('data', Text),
    Index('idx_event_body_event', 'event_id'),
    Index('idx_event_body_time', 'event_time_iso'),
]

event_body_table = Table('event_body', metadata, *_event_body_columns)

# ################################################################################################################################

# Lineage between events - resubmissions, batch membership and aggregation.
# A link table because one event may have many parents.
_event_link_columns = [
    Column('id', _id_column_type, primary_key=True, autoincrement=True),
    Column('child_event_id', BigInteger),
    Column('parent_event_id', BigInteger),
    Column('link_type', _short_column),
    Index('idx_event_link_child', 'child_event_id'),
    Index('idx_event_link_parent', 'parent_event_id'),
]

event_link_table = Table('event_link', metadata, *_event_link_columns)

# ################################################################################################################################

# The resubmit dedup ledger - every resubmit acquires its key here before dispatch,
# so a double-click or two overlapping bulk operations cannot double-apply one message.
# A row acquired but never completed marks an interrupted resubmit, detectable as in-doubt.
_event_dedup_columns = [
    Column('id', _id_column_type, primary_key=True, autoincrement=True),
    Column('dedup_key', _short_column),
    Column('cid', _short_column),
    Column('action', _short_column),
    Column('actor', _short_column),
    Column('created_iso', _short_column),
    Column('outcome', _short_column),
    Column('completed_iso', _short_column),
    Index('idx_event_dedup_key', 'dedup_key', unique=True),
    Index('idx_event_dedup_outcome', 'outcome'),
]

event_dedup_table = Table('event_dedup', metadata, *_event_dedup_columns)

# ################################################################################################################################

# Alerts with their dedup count - one row per (rule, source, object, kind) within the dedup
# window, repeated findings increment the count instead of adding rows. There is
# no lifecycle here - what happens to an alert after it goes out lives in Jira,
# ServiceNow or whatever else receives it.
_alert_columns = [
    Column('id', _id_column_type, primary_key=True, autoincrement=True),
    Column('rule_name', _short_column),
    Column('source', _short_column),
    Column('object_name', _short_column),
    Column('kind', _short_column),
    Column('severity', _short_column),
    Column('message', Text),
    Column('link', _endpoint_column),
    Column('count', Integer),
    Column('first_raised_iso', _short_column),
    Column('last_raised_iso', _short_column),
    Index('idx_alert_rule_object', 'rule_name', 'source', 'object_name', 'kind', mysql_length={
        'rule_name': _index_prefix_len,
        'source': _index_prefix_len,
        'object_name': _index_prefix_len,
        'kind': _index_prefix_len,
    }),
]

alert_table = Table('alert', metadata, *_alert_columns)

# ################################################################################################################################

# The AS4 message partition channels - the messages a partner is to pull rather than be sent,
# each waiting on the channel it was queued on until a pull request asks for it. A row claimed by
# a pull stays in flight until the receipt for it arrives, and one whose receipt never arrives goes
# back to waiting, so a pull that was answered but never acknowledged is not a message lost.
_as4_pull_queue_columns = [
    Column('id', _id_column_type, primary_key=True, autoincrement=True),
    Column('mpc', _endpoint_column),
    Column('from_party', _short_column),
    Column('to_party', _short_column),
    Column('message_id', _short_column),
    Column('conversation_id', _short_column),
    Column('service', _short_column),
    Column('action', _short_column),
    Column('state', _short_column),
    Column('pull_count', Integer),
    Column('queued_iso', _short_column),
    Column('claimed_iso', _short_column),
    Column('data', Text),
    Index('idx_as4_pull_queue_mpc_state', 'mpc', 'state', 'id'),
    Index('idx_as4_pull_queue_message_id', 'message_id', unique=True),
    Index('idx_as4_pull_queue_state_claimed', 'state', 'claimed_iso'),
]

as4_pull_queue_table = Table('as4_pull_queue', metadata, *_as4_pull_queue_columns)

# ################################################################################################################################
# ################################################################################################################################

# Markers meaning a failure is transient - resubmitting the message as-is can work
_transient_markers = (
    'timeout', 'timed out', 'connection', 'refused', 'unreachable', 'reset', 'unavailable', 'temporar',
    f'{REQUEST_TIMEOUT}', f'{TOO_MANY_REQUESTS}', f'{BAD_GATEWAY}', f'{SERVICE_UNAVAILABLE}', f'{GATEWAY_TIMEOUT}',
)

# Markers meaning a failure is permanent - the message needs to change before another attempt
_permanent_markers = (
    'validation', 'invalid', 'malformed', 'parse', 'schema', 'unauthorized', 'forbidden', 'not found', 'duplicate',
    f'{BAD_REQUEST}', f'{UNAUTHORIZED}', f'{FORBIDDEN}', f'{NOT_FOUND}', f'{UNPROCESSABLE_ENTITY}',
)

# ################################################################################################################################

def derive_classification(outcome:'str', status:'str' = '', application_outcome:'str' = '') -> 'str':
    """ Derives the transient-vs-permanent classification of a failure out of its platform
    and application outcomes. Successful events and failures matching no known marker stay unclassified.
    """

    # Only failures are classified ..
    if outcome != AuditOutcome.Error:
        return ''

    # .. both outcome layers contribute to the match ..
    combined = f'{status} {application_outcome}'.lower()

    # .. a transient failure means resubmitting the message as-is can work ..
    for marker in _transient_markers:
        if marker in combined:
            out = AuditClassification.Transient
            break

    # .. a permanent one means the message needs to change first ..
    else:
        for marker in _permanent_markers:
            if marker in combined:
                out = AuditClassification.Permanent
                break

        # .. and anything unmatched stays unclassified.
        else:
            out = ''

    return out

# ################################################################################################################################
# ################################################################################################################################
