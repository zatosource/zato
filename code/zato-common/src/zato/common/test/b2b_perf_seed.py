# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone

# gevent
from gevent import joinall, spawn

# SQLAlchemy
from sqlalchemy import delete, insert

# Zato
from zato.common.audit_log.api import metadata as audit_metadata
from zato.common.audit_log.common import AuditEvent, AuditOutcome, AuditSource, event_table
from zato.common.b2b.common.business_log import BusinessLog
from zato.common.b2b.common.clock import SystemClock
from zato.common.b2b.common.schema import address_state_table, create_tables, held_message_table, message_table, \
    open_table, sequence_table
from zato.common.b2b.common.send_log import SendLog
from zato.common.test.b2b_perf_common import Host_Server_Name
from zato.common.test.b2b_write_path import new_business_message, new_sent_message

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent import Greenlet
    from sqlalchemy.engine import Engine
    from zato.common.b2b.common.commit_group import GroupCommitWriter
    from zato.common.typing_ import callable_, stranydict
    callable_ = callable_
    Engine = Engine
    Greenlet = Greenlet
    GroupCommitWriter = GroupCommitWriter
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

greenlet_list = list['Greenlet']
rowlist       = list['stranydict']

# ################################################################################################################################
# ################################################################################################################################

# What the audit log of a recovery read holds.
Seed_Transactions     = 45_000
Seed_Exchanges        = 2_000
Seed_Completed_Events = 1_000_000

# How many records are written by the greenlets of one batch, each of which waits for the commit of its record.
_record_batch_size = 1000

# How many completed events one insert writes, and how many inserts one transaction commits.
_insert_rows        = 1000
_inserts_per_commit = 10

# How long the business transactions of the seed have for their receipt, in seconds.
_receipt_seconds = 86400

# The agreement and the parties of the completed events.
_completed_cpa_id      = 'b2b-perf-completed'
_completed_data        = '{}'
_completed_event_types = (AuditEvent.Message_Sent, AuditEvent.Message_Completed)

# ################################################################################################################################
# ################################################################################################################################

def clear_database(engine:'Engine') -> 'None':
    """ Creates the B2B tables if needed and deletes every row of them and of the audit log.
    """
    create_tables(engine)

    with engine.begin() as connection:

        for table in (open_table, message_table, sequence_table, held_message_table, address_state_table):
            _ = connection.execute(delete(table))

        for table in reversed(audit_metadata.sorted_tables):
            _ = connection.execute(delete(table))

# ################################################################################################################################

def _run_batches(func:'callable_', prefix:'str', count:'int') -> 'None':
    """ Calls the function with each message identifier of the given prefix in greenlets, one batch at a time.
    """
    for batch_start in range(0, count, _record_batch_size):
        batch_limit = batch_start + _record_batch_size
        batch_end = min(batch_limit, count)
        greenlets:'greenlet_list' = []

        for index in range(batch_start, batch_end):
            message_id = f'{prefix}{index}'
            greenlet = spawn(func, message_id)
            greenlets.append(greenlet)

        _ = joinall(greenlets, raise_error=True)

# ################################################################################################################################

def _completed_rows(first_index:'int', now:'datetime') -> 'rowlist':
    """ Returns the rows of one insert of completed events - the sending and the completion of each message.
    """
    out:'rowlist' = []
    message_count = _insert_rows // len(_completed_event_types)

    for offset in range(message_count):
        index = first_index + offset
        message_id = f'b2b-perf-completed-{index}'

        for event_type in _completed_event_types:
            row:'stranydict' = {
                'cid': message_id,
                'source': AuditSource.EbMS2,
                'event_type': event_type,
                'object_name': _completed_cpa_id,
                'msg_id': message_id,
                'event_time': now,
                'server_name': Host_Server_Name,
                'outcome': AuditOutcome.OK,
                'data': _completed_data,
            }
            out.append(row)

    return out

# ################################################################################################################################

def _seed_completed(engine:'Engine') -> 'None':
    """ Writes the completed events of the seed in multi-row inserts.
    """
    now = datetime.now(timezone.utc)
    messages_per_insert = _insert_rows // len(_completed_event_types)
    message_count = Seed_Completed_Events // len(_completed_event_types)
    messages_per_commit = messages_per_insert * _inserts_per_commit

    for commit_start in range(0, message_count, messages_per_commit):

        with engine.begin() as connection:
            for insert_index in range(_inserts_per_commit):
                offset = insert_index * messages_per_insert
                first_index = commit_start + offset
                rows = _completed_rows(first_index, now)

                statement = insert(event_table).values(rows)
                _ = connection.execute(statement)

# ################################################################################################################################

def seed_recovery(engine:'Engine', writer:'GroupCommitWriter') -> 'None':
    """ Fills the audit log with what a recovery read is measured against - the awaiting business transactions,
    the open exchanges and the completed events.
    """
    clock = SystemClock()
    now = clock.now()

    business_log = BusinessLog(AuditSource.EbMS2, Host_Server_Name, writer)
    send_log = SendLog(AuditSource.EbMS2, Host_Server_Name, clock, writer, business_log)

    # Each business transaction awaits its receipt for a day ..
    def record_transaction(message_id:'str') -> 'None':
        message = new_business_message(message_id, now, _receipt_seconds)
        business_log.record_sent(message)

    # .. each exchange awaits its first acknowledgment ..
    def record_exchange(message_id:'str') -> 'None':
        sent_at = now - timedelta(seconds=1)
        sent = new_sent_message(message_id, sent_at)
        send_log.record_first_attempt(sent)

    _run_batches(record_transaction, 'b2b-perf-awaiting-', Seed_Transactions)
    _run_batches(record_exchange, 'b2b-perf-open-', Seed_Exchanges)

    # .. and the completed events are written in multi-row inserts.
    _seed_completed(engine)

# ################################################################################################################################
# ################################################################################################################################
