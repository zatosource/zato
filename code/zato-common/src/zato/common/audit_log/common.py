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
    AS2           = 'as2'
    AS4           = 'as4'
    X12           = 'x12'
    MCP           = 'mcp'
    HL7           = 'hl7'
    FHIR          = 'fhir'
    Config        = 'config'

# ################################################################################################################################

# The sources whose events are evidence rather than diagnostics, with how long each is kept for.
_source_retention_days = {
    AuditSource.AS2: _default_evidence_retention_days,
    AuditSource.AS4: _default_evidence_retention_days,
    AuditSource.X12: _default_evidence_retention_days,
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
    MCP_Initialize       = 'mcp-initialize'
    MCP_Tools_List       = 'mcp-tools-list'
    MCP_Tools_Call       = 'mcp-tools-call'
    MCP_Session_Delete   = 'mcp-session-delete'
    MCP_Batch            = 'mcp-batch'
    Bulk_Repair          = 'bulk-repair'
    Config_Created       = 'config-created'
    Config_Edited        = 'config-edited'
    Config_Deleted       = 'config-deleted'
    Content_Viewed       = 'content-viewed'

# ################################################################################################################################

class AuditOutcome:
    OK      = 'ok'
    Error   = 'error'
    Expired = 'expired'

# ################################################################################################################################

class AuditBody:
    """ The kinds of message bodies an event may carry - what was sent, what came back,
    and what the other side said when it failed.
    """
    Request  = 'request'
    Response = 'response'
    Error    = 'error'

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
    Index('idx_event_cid', 'cid', 'id'),
    Index('idx_event_msg_id', 'msg_id', 'id'),

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
    Column('created_iso', _short_column),
    Column('outcome', _short_column),
    Column('completed_iso', _short_column),
    Index('idx_event_dedup_key', 'dedup_key', unique=True),
    Index('idx_event_dedup_outcome', 'outcome'),
]

event_dedup_table = Table('event_dedup', metadata, *_event_dedup_columns)

# ################################################################################################################################

# Alerts with their dedup count and lifecycle - one row per (rule, object, kind) within
# the dedup window, repeated findings increment the count instead of adding rows,
# and acknowledgment is recorded in place, so an alert never exists twice half-resolved.
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
    Column('state', _short_column),
    Column('first_raised_iso', _short_column),
    Column('last_raised_iso', _short_column),
    Column('observed_by', _short_column),
    Column('observed_iso', _short_column),
    Column('resolved_by', _short_column),
    Column('resolved_iso', _short_column),
    Index('idx_alert_rule_object', 'rule_name', 'object_name', 'kind'),
    Index('idx_alert_state', 'state'),
]

alert_table = Table('alert', metadata, *_alert_columns)

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
