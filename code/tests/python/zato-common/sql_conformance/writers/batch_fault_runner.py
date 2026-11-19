# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Runs one batch of the pub/sub writer with an item of every kind in a process of its own, under a fault of the database.
# The state that the batch refers to is written with no fault, the fault is turned on and the batch runs, after which
# the fault is cleared and the next batch runs on the same pool. A process that holds the write lock of the file
# commits one publication under a delay of its sync, and a process that waits for that lock writes one batch.
# Each process reports what it observed as the last line of its output.

# gevent
from gevent import monkey
_ = monkey.patch_all()

# stdlib
import json
import os
import sys
from time import sleep

sys.path.insert(0, os.path.dirname(__file__))

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import AuditLog
from zato.common.audit_log.common import event_payload_table, event_table
from zato.common.db_env.commit_ticket import CommitTicket
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.pending import new_fenced_ack, new_pending_ack, new_pending_atomic, new_pending_attempts, \
    new_pending_lease
from zato.common.pubsub.sql.publication import add_published_event, build_publication
from zato.common.pubsub.sql.schema import delivery_table, message_table, publish_count_table, queue_count_table, \
    topic_count_table, topic_sub_table, trace_table
from zato.common.test.zato_database import file_database_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.db_env.commit_ticket import commit_ticket_list
    from zato.common.typing_ import any_, anydict, anylist, intlist, strlist

    any_ = any_
    anydict = anydict
    anylist = anylist
    commit_ticket_list = commit_ticket_list
    Engine = Engine
    intlist = intlist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the fault library takes to read its control file again, in seconds, with a margin
    Control_Reload_Seconds = 0.3

    # Every fsync and fdatasync of a file under the directory fails with EIO, while the writes themselves proceed
    Control_Sync = 'prefix={directory}\nerror_percent=100\nerrno=EIO\ncalls=sync\n'

    # Every write of a file under the directory fails with ENOSPC, as on a file system that has no space left
    Control_Full = 'prefix={directory}\nerror_percent=100\nerrno=ENOSPC\ncalls=write\n'

    # Every fsync and fdatasync of a file under the directory takes longer than the busy timeout of SQLite
    Control_Hold = 'prefix={directory}\ndelay_us=8000000\ncalls=sync\n'

    # A control file without a prefix applies no fault
    Control_None = ''

    # The modes of the runner
    Mode_Sync = 'sync'
    Mode_Full = 'full'
    Mode_Constraint = 'constraint'
    Mode_Hold = 'hold'
    Mode_Locked = 'locked'

    # The lines that a process prints when it reaches a point that the test waits for, and the line that it waits for
    Line_Prepared = 'prepared'
    Line_Ready = 'ready'
    Line_Writing = 'writing'

    # The server that the audit events are written by
    Server_Name = 'batch-faults'

    # The topics and subscribers of the batches
    Topic_Main = 'batch.faults.main'
    Topic_In = 'batch.faults.input'
    Topic_Out = 'batch.faults.output'
    Topic_Pub = 'batch.faults.publish'

    Sub_Key_Main = 'zpsk.batch-faults.main'
    Sub_Key_In = 'zpsk.batch-faults.input'
    Sub_Key_Out = 'zpsk.batch-faults.output'
    Sub_Key_Pub = 'zpsk.batch-faults.publish'

    # The payloads of the messages
    Data_Main = 'Order ORD-{} for Maria Johnson'
    Data_Input = 'Order ORD-0100 for John Smith'
    Data_Pub = 'Invoice INV-0042 for Anna Miller'
    Data_Receipt = 'Receipt RCP-0100 for John Smith'
    Data_Hold = 'Order ORD-0200 for Jane Doe'

    # How many messages the main subscriber has, how many of them a lease takes at most, and for how long
    Main_Count = 3
    Lease_Max_Messages = 3
    Lease_Max_Len = 10_000_000
    Lease_Ms = 30_000

# The tables whose rows a failed batch leaves as they were
_tables = [message_table, delivery_table, topic_sub_table, queue_count_table, topic_count_table, publish_count_table,
    trace_table, event_table, event_payload_table]

# ################################################################################################################################
# ################################################################################################################################

class Prepared:
    """ The messages and delivery rows that the items of a batch refer to.
    """
    main_msg_ids: 'strlist'
    main_delivery_ids: 'intlist'
    input_msg_id: 'str'
    input_attempt: 'int'

# ################################################################################################################################

def _write_control(control_path:'str', template:'str', directory:'str') -> 'None':
    """ Applies the fault of a template to the files under the directory, once the library reads its control file again.
    """
    with open(control_path, 'w') as control_file:
        _ = control_file.write(template.format(directory=directory))

    sleep(ModuleCtx.Control_Reload_Seconds)

# ################################################################################################################################

def _prepare(backend:'SQLPubSubBackend', engine:'Engine') -> 'Prepared':
    """ Subscribes one subscriber to each topic, publishes the messages that the items of a batch refer to
    and pulls the input message.
    """
    backend.subscribe(ModuleCtx.Sub_Key_Main, ModuleCtx.Topic_Main)
    backend.subscribe(ModuleCtx.Sub_Key_In, ModuleCtx.Topic_In)
    backend.subscribe(ModuleCtx.Sub_Key_Out, ModuleCtx.Topic_Out)
    backend.subscribe(ModuleCtx.Sub_Key_Pub, ModuleCtx.Topic_Pub)

    out = Prepared()
    out.main_msg_ids = []

    for index in range(ModuleCtx.Main_Count):
        result = backend.publish(ModuleCtx.Topic_Main, ModuleCtx.Data_Main.format(f'{index:04d}'))
        out.main_msg_ids.append(result.msg_id)

    query = select(delivery_table.c.id).where(delivery_table.c.sub_key == ModuleCtx.Sub_Key_Main)
    query = query.order_by(delivery_table.c.id)

    with engine.connect() as connection:
        out.main_delivery_ids = list(connection.execute(query).scalars())

    _ = backend.publish(ModuleCtx.Topic_In, ModuleCtx.Data_Input)
    messages = backend.pull_messages(ModuleCtx.Sub_Key_In)

    out.input_msg_id = messages[0]['msg_id']
    out.input_attempt = messages[0]['delivery_attempt']

    return out

# ################################################################################################################################

def _new_batch(backend:'SQLPubSubBackend', prepared:'Prepared') -> 'anylist':
    """ Returns a publication, an acknowledgement, a fenced acknowledgement with one receipt, the push attempts
    of two deliveries and a lease, in the order of the kinds.
    """
    built = build_publication(backend, ModuleCtx.Topic_Pub, ModuleCtx.Data_Pub)
    add_published_event(backend, built)

    ack = new_pending_ack(ModuleCtx.Sub_Key_Main, [prepared.main_msg_ids[0]], None)

    fenced = new_fenced_ack(ModuleCtx.Sub_Key_In, [prepared.input_msg_id], [prepared.input_attempt])
    receipt = build_publication(backend, ModuleCtx.Topic_Out, ModuleCtx.Data_Receipt)
    add_published_event(backend, receipt)
    atomic = new_pending_atomic([receipt.pending], fenced, True)

    attempts = new_pending_attempts(prepared.main_delivery_ids[:2])

    now_ms = backend.clock.now_ms()
    lease = new_pending_lease(ModuleCtx.Sub_Key_Main, ModuleCtx.Lease_Max_Messages, ModuleCtx.Lease_Max_Len, now_ms,
        now_ms + ModuleCtx.Lease_Ms, backend._on_leased)

    out = [built.pending, ack, atomic, attempts, lease]
    return out

# ################################################################################################################################

def _write_batch(backend:'SQLPubSubBackend', items:'anylist') -> 'commit_ticket_list':
    """ Writes the items in one commit of the commit queue, as it writes the items of its concurrent callers,
    and returns the ticket of each item with the outcome that its caller receives.
    """
    commit_queue = backend._writer._commit_queue
    out:'commit_ticket_list' = []

    for item in items:
        ticket = CommitTicket(item, 1, False)
        out.append(ticket)

    runner = out[0]
    runner.batch = out
    runner.has_started = True

    with commit_queue._lock:
        commit_queue._in_flight += 1

    commit_queue._commit(runner)

    return out

# ################################################################################################################################

def _get_rows(engine:'Engine') -> 'anylist':
    """ Returns every row of every table that a batch writes to, table by table.
    """
    out:'anylist' = []

    with engine.connect() as connection:
        for table in _tables:
            query = select(table).order_by(*table.primary_key.columns)
            rows:'anylist' = []

            for row in connection.execute(query):
                rows.append(list(row))

            out.append([table.name, rows])

    return out

# ################################################################################################################################

def _is_in_transaction(engine:'Engine') -> 'bool':
    """ Returns whether the connection that the pool hands out next has a transaction open.
    """
    with engine.connect() as connection:
        dbapi_connection:'any_' = connection.connection.dbapi_connection
        out = dbapi_connection.in_transaction

    return out

# ################################################################################################################################

def _get_error(tickets:'commit_ticket_list') -> 'anydict':
    """ Returns the classes and the message of the error of a failed batch, and whether each of its callers received it.
    """
    error:'any_' = tickets[0].exception

    is_every_caller = True

    for ticket in tickets:
        if ticket.exception is not error:
            is_every_caller = False

    out = {
        'error_class': type(error).__name__,
        'error_base': type(error).__mro__[1].__name__,
        'orig_class': f'{type(error.orig).__module__}.{type(error.orig).__name__}',
        'orig_message': str(error.orig),
        'is_every_caller': is_every_caller,
    }

    return out

# ################################################################################################################################

def _get_next_batch(backend:'SQLPubSubBackend', prepared:'Prepared') -> 'anydict':
    """ Writes the next batch and returns the outcome of each of its items.
    """
    publication, ack, atomic, attempts, lease = _new_batch(backend, prepared)
    tickets = _write_batch(backend, [publication, ack, atomic, attempts, lease])

    exceptions:'anylist' = []

    for ticket in tickets:
        exceptions.append(repr(ticket.exception))

    out = {
        'exceptions': exceptions,
        'subscriber_keys': publication.subscriber_keys,
        'ack_removed_count': ack.removed_count,
        'atomic_removed_count': atomic.ack.removed_count,
        'attempts': sorted(attempts.attempts.items()),
        'leased_count': len(lease.messages),
        'is_outage_cleared': backend._writer._outage.failed_at is None,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def _run_fault(mode:'str', directory:'str', control_path:'str') -> 'anydict':
    """ Writes one batch under the fault of a mode and then the next batch with the fault cleared.
    """
    if mode == ModuleCtx.Mode_Sync:
        template = ModuleCtx.Control_Sync
    else:
        template = ModuleCtx.Control_Full

    with file_database_engine(directory) as engine:
        backend = SQLPubSubBackend(audit_log=AuditLog(ModuleCtx.Server_Name))
        prepared = _prepare(backend, engine)
        rows_before = _get_rows(engine)

        # The batch fails under the fault ..
        items = _new_batch(backend, prepared)

        _write_control(control_path, template, directory)
        tickets = _write_batch(backend, items)
        _write_control(control_path, ModuleCtx.Control_None, directory)

        out = _get_error(tickets)

        # .. leaving no row behind and no transaction open, with the outage recorded ..
        out['is_rows_unchanged'] = _get_rows(engine) == rows_before
        out['is_in_transaction'] = _is_in_transaction(engine)
        out['is_outage_recorded'] = backend._writer._outage.failed_at is not None

        # .. and the next batch commits on the same pool.
        out['next'] = _get_next_batch(backend, prepared)

    return out

# ################################################################################################################################

def _run_constraint(directory:'str') -> 'anydict':
    """ Writes a batch whose publication has no priority, which the table does not accept.
    """
    with file_database_engine(directory) as engine:
        backend = SQLPubSubBackend(audit_log=AuditLog(ModuleCtx.Server_Name))
        prepared = _prepare(backend, engine)
        rows_before = _get_rows(engine)

        items = _new_batch(backend, prepared)
        items[0].message_values['priority'] = None

        tickets = _write_batch(backend, items)

        out = _get_error(tickets)
        out['is_rows_unchanged'] = _get_rows(engine) == rows_before
        out['is_in_transaction'] = _is_in_transaction(engine)

    return out

# ################################################################################################################################

def _run_hold(directory:'str', control_path:'str') -> 'anydict':
    """ Prepares the state of the batch of the waiting process and then holds the write lock of the file
    for the time of one delayed sync, while committing one publication.
    """
    with file_database_engine(directory):
        backend = SQLPubSubBackend(audit_log=AuditLog(ModuleCtx.Server_Name))
        backend.subscribe(ModuleCtx.Sub_Key_Pub, ModuleCtx.Topic_Pub)

        print(ModuleCtx.Line_Prepared, flush=True)
        _ = sys.stdin.readline()

        _write_control(control_path, ModuleCtx.Control_Hold, directory)

        print(ModuleCtx.Line_Writing, flush=True)
        _ = backend.publish(ModuleCtx.Topic_Pub, ModuleCtx.Data_Hold)

    out = {'is_written': True}
    return out

# ################################################################################################################################

def _run_locked(directory:'str') -> 'anydict':
    """ Writes one publication once told to, while another process holds the write lock of the file.
    """
    with file_database_engine(directory):
        backend = SQLPubSubBackend(audit_log=AuditLog(ModuleCtx.Server_Name))

        print(ModuleCtx.Line_Ready, flush=True)
        _ = sys.stdin.readline()

        built = build_publication(backend, ModuleCtx.Topic_Pub, ModuleCtx.Data_Pub)
        add_published_event(backend, built)

        tickets = _write_batch(backend, [built.pending])
        out = _get_error(tickets)

    return out

# ################################################################################################################################

def main() -> 'None':
    mode, directory, control_path = sys.argv[1:]

    if mode == ModuleCtx.Mode_Constraint:
        result = _run_constraint(directory)
    elif mode == ModuleCtx.Mode_Hold:
        result = _run_hold(directory, control_path)
    elif mode == ModuleCtx.Mode_Locked:
        result = _run_locked(directory)
    else:
        result = _run_fault(mode, directory, control_path)

    print(json.dumps(result), flush=True)

    os._exit(0)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
