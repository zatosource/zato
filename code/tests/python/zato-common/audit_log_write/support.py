# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import contextmanager
from datetime import datetime, timezone

# SQLAlchemy
from sqlalchemy import event as sa_event, select

# Zato
from zato.common.audit_log.api import event_attr_table, event_body_table, event_link_table, event_table, \
    get_audit_engine, AuditBody, AuditEvent, AuditLink, AuditOutcome, AuditSource
from zato.common.audit_log.attachment import build_attachment
from zato.common.audit_log.common import event_dedup_table
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from sqlalchemy.engine import Engine
    from sqlalchemy.sql.schema import Table
    from zato.common.audit_log.api import AuditLog
    from zato.common.audit_log.buffer import pending_event_list
    from zato.common.typing_ import any_, anylist, strlist

    any_ = any_
    anylist = anylist
    AuditLog = AuditLog
    Engine = Engine
    pending_event_list = pending_event_list
    strlist = strlist
    Table = Table

    recordergen = Iterator['StatementRecorder']

# ################################################################################################################################
# ################################################################################################################################

# The backends every test of this directory runs against
Backend_SQLite     = 'sqlite'
Backend_PostgreSQL = 'postgresql'

# The server all the test events are written under
Server_Name = 'test-audit-log-write-server'

# The channel all the test events belong to
Object_Name = 'audit.test.write-channel'

# The moment all the events of a comparison are stamped with
Event_Time = datetime(2026, 10, 29, 12, 0, 0, 123456, tzinfo=timezone.utc)

# The verbs of the statements that write or read rows
_row_verbs = ('INSERT', 'SELECT', 'COPY')

# ################################################################################################################################
# ################################################################################################################################

class StatementRecorder:
    """ The statements that write or read rows and the commits of an engine, each statement as its verb and its table.
    """

    def __init__(self) -> 'None':
        self.statements:'anylist' = []
        self.commit_count = 0

    def on_execute(
        self,
        conn:'any_',
        cursor:'any_',
        statement:'str',
        parameters:'any_',
        context:'any_',
        executemany:'bool',
        ) -> 'None':

        words = statement.split()
        verb = words[0]

        if verb not in _row_verbs:
            return

        if verb == 'INSERT':
            table_name = words[2]
        elif verb == 'COPY':
            table_name = words[1]
        else:
            from_index = words.index('FROM')
            table_name = words[from_index + 1]

        self.statements.append((verb, table_name))

    def on_commit(self, conn:'any_') -> 'None':
        self.commit_count += 1

# ################################################################################################################################

@contextmanager
def record_statements(engine:'Engine') -> 'recordergen':
    """ Records the statements and the commits of an engine for the duration of a block.
    """
    recorder = StatementRecorder()

    sa_event.listen(engine, 'before_cursor_execute', recorder.on_execute)
    sa_event.listen(engine, 'commit', recorder.on_commit)

    try:
        yield recorder
    finally:
        sa_event.remove(engine, 'before_cursor_execute', recorder.on_execute)
        sa_event.remove(engine, 'commit', recorder.on_commit)

# ################################################################################################################################
# ################################################################################################################################

def delete_all_rows() -> 'None':
    """ Starts a test from empty tables because the PostgreSQL container is shared by all the tests.
    """
    engine = get_audit_engine()

    with engine.begin() as connection:
        _ = connection.execute(event_attr_table.delete())
        _ = connection.execute(event_body_table.delete())
        _ = connection.execute(event_link_table.delete())
        _ = connection.execute(event_dedup_table.delete())
        _ = connection.execute(event_table.delete())

# ################################################################################################################################

def insert_seed_event(audit_log:'AuditLog') -> 'int':
    """ Writes the event the events of a batch link back to and returns its id.
    """
    event_id = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Message_Received, Object_Name,
        cid='cid-seed', msg_id='msg-seed', outcome=AuditOutcome.OK, data='Original order from John Smith')

    out = cast_('int', event_id)
    return out

# ################################################################################################################################

def new_batch(audit_log:'AuditLog', event_count:'int', seed_event_id:'int') -> 'pending_event_list':
    """ Returns events with attributes of every kind, two bodies each, an attachment on every tenth event
    and a link to the seed event on every second one, all stamped with the same moment.
    """
    out:'pending_event_list' = []

    for index in range(event_count):

        attachments:'anylist' = []
        parents:'anylist' = []

        if index % 10 == 0:
            attachment = build_attachment('invoice.pdf', 'application/pdf', b'%PDF-1.7 invoice for Maria Johnson')
            attachments.append(attachment)

        if index % 2 == 0:
            parents.append(seed_event_id)

        attrs = {
            'partner': 'Maria Johnson',
            'order_id': f'ORD-{index:04d}',
            'amount': index * 10.25,
            'quantity': index,
            'is_priority': index % 3 == 0,
        }

        bodies = {
            AuditBody.Request: f'{{"order": {index}, "customer": "John Smith"}}',
            AuditBody.Response: f'{{"order": {index}, "status": "accepted"}}',
        }

        pending = audit_log.new_pending_event(AuditSource.REST_Channel, AuditEvent.Message_Received, Object_Name,
            cid=f'cid-{index}', msg_id=f'msg-{index}', outcome=AuditOutcome.OK, data=f'Order {index} from John Smith',
            internal_data=f'{{"digest": "sha256-{index}"}}', attrs=attrs, bodies=bodies, attachments=attachments,
            parents=parents, parent_link_type=AuditLink.Resubmit_Of)

        pending.values['event_time'] = Event_Time
        out.append(pending)

    return out

# ################################################################################################################################

def read_rows(table:'Table') -> 'anylist':
    """ Returns all the rows of a table as dicts, in the order of their ids.
    """
    engine = get_audit_engine()

    query = select(table)
    query = query.order_by(table.c.id)

    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            values = dict(row._mapping)
            out.append(values)

    return out

# ################################################################################################################################
# ################################################################################################################################
