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
from sqlalchemy import Column, Index, Integer, MetaData, Numeric, String, Table, Text

# ################################################################################################################################
# ################################################################################################################################

# The name of the SQLite file holding all audit events, shared by all sources
audit_db_file_name = 'audit.db'

# The environment variable overriding how many days of events are kept
Env_Retention_Days = 'Zato_Audit_Log_Retention_Days'

# How many days of events are kept when the environment does not say otherwise
_default_retention_days = 30

# Maximum length of short string columns
_short_column_len = 255

# Maximum length of the endpoint column - it may hold full addresses
_endpoint_column_len = 500

# Attribute values are capped so they always fit an indexable column
Attr_Value_Max_Len = _short_column_len

# ################################################################################################################################

def get_retention_days() -> 'int':
    """ Returns how many days of audit events are kept - also the widest window
    the reports run over. Configurable through an environment variable.
    """
    if value := os.environ.get(Env_Retention_Days, ''):
        out = int(value)
    else:
        out = _default_retention_days

    return out

# ################################################################################################################################
# ################################################################################################################################

class AuditSource:
    PubSub        = 'pubsub'
    REST_Channel  = 'rest-channel'
    SOAP_Channel  = 'soap-channel'
    REST_Outgoing = 'rest-outgoing'
    SOAP_Outgoing = 'soap-outgoing'
    Email_IMAP    = 'email-imap'
    AS2           = 'as2'
    X12           = 'x12'
    MCP           = 'mcp'
    HL7           = 'hl7'

# ################################################################################################################################

class AuditEvent:
    Published         = 'published'
    Delivered         = 'delivered'
    Delivery_Failed   = 'delivery-failed'
    Expired           = 'expired'
    Received          = 'received'
    Request_Received  = 'request-received'
    Response_Sent     = 'response-sent'
    Request_Sent      = 'request-sent'
    Response_Received = 'response-received'
    Message_Received  = 'message-received'
    Message_Marked_Seen = 'message-marked-seen'
    Message_Deleted     = 'message-deleted'
    Interchange_Sent     = 'interchange-sent'
    Interchange_Received = 'interchange-received'
    Ack_Sent             = 'ack-sent'
    Ack_Received         = 'ack-received'
    Message_Sent         = 'message-sent'
    MDN_Sent             = 'mdn-sent'
    MDN_Received         = 'mdn-received'
    Alert_Raised         = 'alert-raised'
    MCP_Initialize       = 'mcp-initialize'
    MCP_Tools_List       = 'mcp-tools-list'
    MCP_Tools_Call       = 'mcp-tools-call'
    MCP_Session_Delete   = 'mcp-session-delete'
    MCP_Batch            = 'mcp-batch'
    Bulk_Repair          = 'bulk-repair'

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

event_table = Table('event', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('cid', String(_short_column_len)),
    Column('cid_sequence', Integer),
    Column('source', String(_short_column_len)),
    Column('event_type', String(_short_column_len)),
    Column('object_name', String(_short_column_len)),
    Column('msg_id', String(_short_column_len)),
    Column('correl_id', String(_short_column_len)),
    Column('ext_client_id', String(_short_column_len)),
    Column('pub_time_iso', String(_short_column_len)),
    Column('event_time_iso', String(_short_column_len)),
    Column('server_name', String(_short_column_len)),
    Column('endpoint', String(_endpoint_column_len)),
    Column('sub_key', String(_short_column_len)),
    Column('size', Integer),
    Column('priority', Integer),
    Column('outcome', String(_short_column_len)),
    Column('application_outcome', String(_short_column_len)),
    Column('classification', String(_short_column_len)),
    Column('status', String(_short_column_len)),
    Column('duration_ms', Integer),
    Column('data', Text),
    Index('idx_event_source_object', 'source', 'object_name', 'id'),
    Index('idx_event_cid', 'cid', 'id'),
    Index('idx_event_msg_id', 'msg_id', 'id'),
)

# ################################################################################################################################

# Searchable attributes - any source declares indexed search fields with no schema changes.
# Values are stored as capped text, and numbers additionally go to a numeric column
# so aggregation queries can sum and group without casting.
event_attr_table = Table('event_attr', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('event_id', Integer),
    Column('name', String(_short_column_len)),
    Column('value', String(_short_column_len)),
    Column('value_number', Numeric(20, 6, asdecimal=False)),
    Index('idx_event_attr_event', 'event_id'),
    Index('idx_event_attr_name_value', 'name', 'value'),
    Index('idx_event_attr_name_number', 'name', 'value_number'),
)

# ################################################################################################################################

# Message bodies live in their own table referenced from event rows - metadata inserts stay small
# and pruning content is a bulk delete here rather than column surgery on the event table.
# The event time is denormalized so pruning never needs a join.
event_body_table = Table('event_body', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('event_id', Integer),
    Column('kind', String(_short_column_len)),
    Column('event_time_iso', String(_short_column_len)),
    Column('data', Text),
    Index('idx_event_body_event', 'event_id'),
    Index('idx_event_body_time', 'event_time_iso'),
)

# ################################################################################################################################

# Lineage between events - resubmissions, batch membership and aggregation.
# A link table because one event may have many parents.
event_link_table = Table('event_link', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('child_event_id', Integer),
    Column('parent_event_id', Integer),
    Column('link_type', String(_short_column_len)),
    Index('idx_event_link_child', 'child_event_id'),
    Index('idx_event_link_parent', 'parent_event_id'),
)

# ################################################################################################################################

# The resubmit dedup ledger - every resubmit acquires its key here before dispatch,
# so a double-click or two overlapping bulk operations cannot double-apply one message.
# A row acquired but never completed marks an interrupted resubmit, detectable as in-doubt.
event_dedup_table = Table('event_dedup', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('dedup_key', String(_short_column_len)),
    Column('cid', String(_short_column_len)),
    Column('action', String(_short_column_len)),
    Column('created_iso', String(_short_column_len)),
    Column('outcome', String(_short_column_len)),
    Column('completed_iso', String(_short_column_len)),
    Index('idx_event_dedup_key', 'dedup_key', unique=True),
    Index('idx_event_dedup_outcome', 'outcome'),
)

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

def derive_classification(outcome:'str', status:'str'='', application_outcome:'str'='') -> 'str':
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
