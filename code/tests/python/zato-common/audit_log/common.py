# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import contextmanager

# SQLAlchemy
from sqlalchemy import func, or_, select

# Zato
from live_sql.asserts import assert_mysql_connection_encrypted as assert_mysql_engine_encrypted, \
    assert_postgresql_connection_encrypted as assert_postgresql_engine_encrypted
from live_sql.env import database_env
from zato.common.audit_log.api import event_attr_table, event_body_table, event_link_table, event_table, \
    get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import anylist, stranydict

    envgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-audit-log-server'

# The channel most of the test events belong to
_channel_name = 'audit.test.channel'

# A second channel proving that filtering by object works
_other_channel_name = 'audit.test.other-channel'

# An event time old enough for retention to always delete it
_expired_event_time_iso = '2020-01-01T00:00:00+00:00'

# The prefix all the audit log database environment variables share
_env_prefix = 'Zato_Audit_Log_DB_'

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def audit_log_env(details:'stranydict') -> 'envgen':
    """ Points the Zato_Audit_Log_DB_* variables at one backend for the duration of a test.
    """
    with database_env(_env_prefix, details):
        yield

# ################################################################################################################################

def delete_all_events() -> 'None':
    """ Starts a scenario from empty tables because containers can be reused between test runs.
    """
    engine = get_audit_engine()

    with engine.begin() as connection:
        _ = connection.execute(event_attr_table.delete())
        _ = connection.execute(event_body_table.delete())
        _ = connection.execute(event_link_table.delete())
        _ = connection.execute(event_table.delete())

# ################################################################################################################################

def _escape_like(query:'str') -> 'str':
    """ The same LIKE escaping the web-admin reader applies to user queries.
    """
    out = query.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
    return out

# ################################################################################################################################

def _count_events(source:'str', object_name:'str', query:'str'='') -> 'int':
    """ Runs the same count query the web-admin poll view runs.
    """
    engine = get_audit_engine()

    where_conditions:'anylist' = [
        event_table.c.source == source,
        event_table.c.object_name == object_name,
    ]

    if query:
        escaped = _escape_like(query)
        like_value = f'%{escaped}%'

        like_parts:'anylist' = []

        for column_name in ('data', 'msg_id', 'correl_id', 'endpoint'):
            column = event_table.c[column_name]
            like_parts.append(column.like(like_value, escape='\\'))

        where_conditions.append(or_(*like_parts))

    count_query = select(func.count())
    count_query = count_query.select_from(event_table)
    count_query = count_query.where(*where_conditions)

    with engine.connect() as connection:
        count_result = connection.execute(count_query)
        out = count_result.scalar()

    return out

# ################################################################################################################################

def _get_page(source:'str', object_name:'str', page:'int', page_size:'int') -> 'anylist':
    """ Runs the same pagination query the web-admin poll view runs.
    """
    engine = get_audit_engine()

    offset = (page - 1) * page_size

    page_query = select(event_table.c.id, event_table.c.cid, event_table.c.data)
    page_query = page_query.where(event_table.c.source == source, event_table.c.object_name == object_name)
    page_query = page_query.order_by(event_table.c.id.desc())
    page_query = page_query.limit(page_size)
    page_query = page_query.offset(offset)

    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(page_query):
            out.append(tuple(row))

    return out

# ################################################################################################################################

def run_audit_log_scenario() -> 'None':
    """ The complete audit log scenario every backend must pass:
    schema creation, inserts, counting, pagination, free-text search with escaping,
    retention and attaching a second writer to an existing schema.
    """

    # Start from empty tables because containers can be reused between test runs ..
    engine = get_audit_engine()
    delete_all_events()

    # .. the schema was created and the writer connects ..
    audit_log = AuditLog(_server_name)

    # .. write a few events for the main test channel ..
    audit_log.insert(AuditSource.REST_Channel, AuditEvent.Request_Received, _channel_name,
        cid='cid-1', endpoint='/billing/invoices', size=120, outcome=AuditOutcome.OK,
        data='{"invoice_id": "INV-2026-001", "progress": "100% complete"}')

    audit_log.insert(AuditSource.REST_Channel, AuditEvent.Response_Sent, _channel_name,
        cid='cid-1', endpoint='/billing/invoices', size=64, outcome=AuditOutcome.OK,
        data='{"status": "accepted", "item_name": "value_a"}')

    audit_log.insert(AuditSource.REST_Channel, AuditEvent.Request_Received, _channel_name,
        cid='cid-2', endpoint='/billing/invoices', size=98, outcome=AuditOutcome.Error,
        data='{"invoice_id": "INV-2026-002", "progress": "100 percent complete", "item_name": "valuexa"}')

    # .. one event for another channel to prove filtering works ..
    audit_log.insert(AuditSource.REST_Channel, AuditEvent.Request_Received, _other_channel_name,
        cid='cid-3', endpoint='/crm/customers', size=42, outcome=AuditOutcome.OK,
        data='{"customer_id": "CUST-77"}')

    # .. counting is per source and object ..
    assert _count_events(AuditSource.REST_Channel, _channel_name) == 3
    assert _count_events(AuditSource.REST_Channel, _other_channel_name) == 1

    # .. pagination returns the newest events first ..
    first_page = _get_page(AuditSource.REST_Channel, _channel_name, 1, 2)
    second_page = _get_page(AuditSource.REST_Channel, _channel_name, 2, 2)

    assert len(first_page) == 2
    assert len(second_page) == 1

    first_page_ids:'anylist' = []

    for row in first_page:
        first_page_ids.append(row[0])

    second_page_row = second_page[0]

    assert first_page_ids[0] > first_page_ids[1]
    assert first_page_ids[1] > second_page_row[0]

    # .. the newest event on the first page is the last one written ..
    newest_row = first_page[0]
    assert newest_row[1] == 'cid-2'

    # .. free-text search matches LIKE wildcards literally - a query with a percent sign
    # .. matches only the row with a literal percent sign in its payload ..
    assert _count_events(AuditSource.REST_Channel, _channel_name, '100%') == 1

    # .. same for underscores - value_a must not match valuexa ..
    assert _count_events(AuditSource.REST_Channel, _channel_name, 'value_a') == 1

    # .. retention deletes events older than the window and keeps the recent ones ..
    expired_insert = event_table.insert().values(
        cid='cid-expired',
        source=AuditSource.REST_Channel,
        event_type=AuditEvent.Request_Received,
        object_name=_channel_name,
        msg_id='',
        correl_id='',
        ext_client_id='',
        pub_time_iso='',
        event_time_iso=_expired_event_time_iso,
        server_name=_server_name,
        endpoint='/billing/invoices',
        sub_key='',
        size=10,
        priority=0,
        outcome=AuditOutcome.OK,
        data='{"note": "this event is old enough to be deleted by retention"}',
    )

    with engine.begin() as connection:
        _ = connection.execute(expired_insert)

    assert _count_events(AuditSource.REST_Channel, _channel_name) == 4

    now = utcnow()
    audit_log._run_retention(now)

    assert _count_events(AuditSource.REST_Channel, _channel_name) == 3

    # .. and a second writer attaches to the existing schema without any errors.
    other_audit_log = AuditLog(_server_name)
    other_audit_log.insert(AuditSource.Email_IMAP, AuditEvent.Message_Received, 'audit.test.imap',
        cid='cid-4', endpoint='INBOX', msg_id='message-id-1', size=2048, outcome=AuditOutcome.OK,
        data='Subject: Monthly report')

    assert _count_events(AuditSource.Email_IMAP, 'audit.test.imap') == 1

# ################################################################################################################################

def assert_mysql_connection_encrypted() -> 'None':
    """ Confirms the current MySQL session really is encrypted.
    """
    engine = get_audit_engine()
    assert_mysql_engine_encrypted(engine)

# ################################################################################################################################

def assert_postgresql_connection_encrypted() -> 'None':
    """ Confirms the current PostgreSQL session really is encrypted.
    """
    engine = get_audit_engine()
    assert_postgresql_engine_encrypted(engine)

# ################################################################################################################################
# ################################################################################################################################
