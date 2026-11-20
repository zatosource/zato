# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The statements of one batch of the pub/sub writer - how they are recorded by verb and table, with the transactions
# they run in, and the statements that each part of a batch is expected to run on each database.

# stdlib
from contextlib import contextmanager

# gevent
import gevent
from gevent import getcurrent
from gevent.monkey import get_original

# SQLAlchemy
from sqlalchemy import event as sa_event

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from gevent import Greenlet
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import any_, anydict, anylist, anytuple, callable_

    any_ = any_
    anydict = anydict
    anylist = anylist
    anytuple = anytuple
    callable_ = callable_
    Engine = Engine
    Greenlet = Greenlet

    recordergen = Iterator['TransactionRecorder']

# ################################################################################################################################
# ################################################################################################################################

# The identity of the native thread, which the greenlets of one thread share
_get_native_ident = get_original('_thread', 'get_ident')

# The statements that open and close a transaction and a savepoint
_begin     = ('BEGIN', '')
_commit    = ('COMMIT', '')
_savepoint = ('SAVEPOINT', '')
_release   = ('RELEASE', '')

# The verbs that are recorded, with the position of the table among the words of a statement or None for no table
_verb_table_position:'anydict' = {
    'INSERT': 2,
    'UPDATE': 1,
    'DELETE': 2,
    'COPY': 1,
    'BEGIN': None,
    'COMMIT': None,
    'ROLLBACK': None,
    'SAVEPOINT': None,
    'RELEASE': None,
}

# ################################################################################################################################
# ################################################################################################################################

# The statements of each part of a transaction, by verb and table, on each database. A publication writes
# its dedup record before its message, after the subscribers are read on SQLite and before on PostgreSQL.
statements_publication = {
    'sqlite': [
        ('SELECT', 'pubsub_topic_sub'), ('INSERT', 'zato_message_dedup'), ('INSERT', 'pubsub_message'),
        ('INSERT', 'pubsub_delivery'),
    ],
    'postgresql': [
        ('INSERT', 'zato_message_dedup'), ('SELECT', 'pubsub_topic_sub'), ('INSERT', 'pubsub_message'),
        ('INSERT', 'pubsub_delivery'),
    ],
}

statements_ack = [
    ('SELECT', 'pubsub_message'), ('SELECT', 'pubsub_delivery'), ('DELETE', 'pubsub_delivery'),
]

_statements_atomic_checks = {
    'sqlite': [
        ('SELECT', 'zato_message_dedup'), ('SELECT', 'pubsub_message'), ('SELECT', 'pubsub_delivery'),
    ],
    'postgresql': [
        ('SELECT', 'pubsub_message'), ('SELECT', 'zato_message_dedup'), ('SELECT', 'pubsub_delivery'),
    ],
}

_statements_atomic_writes = {
    'sqlite': [
        ('SELECT', 'pubsub_topic_sub'), ('INSERT', 'zato_message_dedup'), ('INSERT', 'pubsub_message'),
        ('INSERT', 'pubsub_delivery'), ('DELETE', 'pubsub_delivery'),
    ],
    'postgresql': [
        ('INSERT', 'zato_message_dedup'), ('SELECT', 'pubsub_topic_sub'), ('INSERT', 'pubsub_message'),
        ('INSERT', 'pubsub_delivery'), ('DELETE', 'pubsub_delivery'),
    ],
}

statements_attempts = [
    ('UPDATE', 'pubsub_delivery'),
]

statements_lease = [
    ('SELECT', 'pubsub_delivery'), ('UPDATE', 'pubsub_delivery'), ('SELECT', 'pubsub_message'),
]

statements_drop = {
    'sqlite': [
        ('UPDATE', 'pubsub_message'),
    ],
    'postgresql': [
        ('SELECT', 'pubsub_message'), ('SELECT', 'pubsub_message'), ('UPDATE', 'pubsub_message'),
    ],
}

_statement_payload_select   = ('SELECT', 'event_payload')
_statement_payload_insert   = ('INSERT', 'event_payload')
_statement_event_ids_select = ('SELECT', 'generate_series')
_statement_event_insert     = ('INSERT', 'event')

# ################################################################################################################################
# ################################################################################################################################

class TransactionRecorder:
    """ The statements of an engine by verb and table, with the transactions they ran in. On SQLite, these are
    the statements that the database runs, including the ones that run in Rust, with the consecutive runs
    of one statement recorded once, and on PostgreSQL, the statements that SQLAlchemy sends, each with whether
    a transaction was open when it was sent.

    Only the transactions of the code under test are recorded - those of the greenlet that opened the recording,
    of the greenlets spawned through the recorder, and of the thread pool of the hub, which runs the database calls
    of greenlets on SQLite and does not carry the identity of the greenlet whose call it runs. The background threads
    of the process that run their transactions on the same engine in a greenlet of their own, such as the merger
    of the search indexes of the audit log on PostgreSQL, are not recorded.
    """

    def __init__(self, is_sqlite:'bool') -> 'None':
        self.is_sqlite = is_sqlite
        self.statements:'anylist' = []
        self.in_transaction:'anylist' = []
        self.begin_count = 0
        self.commit_count = 0
        self.native_ident = _get_native_ident()
        self.greenlets:'anylist' = [getcurrent()]

    def spawn(self, func:'callable_', *args:'any_') -> 'Greenlet':
        """ Spawns a greenlet whose transactions are recorded.
        """
        out = gevent.spawn(func, *args)
        self.greenlets.append(out)
        return out

    def is_recorded(self) -> 'bool':
        """ Says whether the transaction that runs in the current greenlet is one of the code under test.
        """
        # A thread of the thread pool of the hub runs the call of a greenlet that waits for it ..
        if _get_native_ident() != self.native_ident:
            return True

        # .. whereas in the thread of the recording, only the greenlets of the recording run the code under test.
        out = getcurrent() in self.greenlets
        return out

    def on_trace(self, statement:'str') -> 'None':
        if verb_table := get_verb_table(statement):
            if not self.statements or self.statements[-1] != verb_table:
                self.statements.append(verb_table)

    def on_checkout(self, dbapi_connection:'any_', connection_record:'any_', connection_proxy:'any_') -> 'None':
        if self.is_recorded():
            dbapi_connection.set_trace_callback(self.on_trace)

    def on_checkin(self, dbapi_connection:'any_', connection_record:'any_') -> 'None':
        dbapi_connection.set_trace_callback(None)

    def on_execute(
        self,
        conn:'any_',
        cursor:'any_',
        statement:'str',
        parameters:'any_',
        context:'any_',
        executemany:'bool',
        ) -> 'None':
        if not self.is_recorded():
            return

        if verb_table := get_verb_table(statement):
            self.statements.append(verb_table)
            self.in_transaction.append(conn.in_transaction())

    def on_begin(self, conn:'any_') -> 'None':
        if self.is_recorded():
            self.begin_count += 1

    def on_commit(self, conn:'any_') -> 'None':
        if not self.is_recorded():
            return

        self.commit_count += 1

        # SQLite runs a statement of its own for the commit, which the trace records
        if self.is_sqlite:
            return

        # .. whereas PostgreSQL commits through the driver.
        self.statements.append(_commit)
        self.in_transaction.append(True)

# ################################################################################################################################

def get_verb_table(statement:'str') -> 'anytuple | None':
    """ Returns the verb and the table of a statement, the verb alone for a statement of a transaction
    or a savepoint, and None for any other statement.
    """
    words = statement.split()
    verb = words[0]

    if verb == 'SELECT':
        if 'FROM' in words:
            from_index = words.index('FROM')
            table_name = words[from_index + 1]
        else:
            table_name = words[1]
        table_name = table_name.split('(')[0]

    elif verb in _verb_table_position:
        position = _verb_table_position[verb]
        if position is None:
            table_name = ''
        else:
            table_name = words[position]

    else:
        return None

    out = (verb, table_name)
    return out

# ################################################################################################################################

@contextmanager
def record_transactions(engine:'Engine') -> 'recordergen':
    """ Records the statements, the transactions and the commits that the code under test runs on an engine
    for the duration of a block.
    """
    is_sqlite = engine.dialect.name == 'sqlite'
    recorder = TransactionRecorder(is_sqlite)

    if is_sqlite:
        sa_event.listen(engine, 'checkout', recorder.on_checkout)
        sa_event.listen(engine, 'checkin', recorder.on_checkin)
    else:
        sa_event.listen(engine, 'before_cursor_execute', recorder.on_execute)

    sa_event.listen(engine, 'begin', recorder.on_begin)
    sa_event.listen(engine, 'commit', recorder.on_commit)

    try:
        yield recorder
    finally:
        if is_sqlite:
            sa_event.remove(engine, 'checkout', recorder.on_checkout)
            sa_event.remove(engine, 'checkin', recorder.on_checkin)
        else:
            sa_event.remove(engine, 'before_cursor_execute', recorder.on_execute)

        sa_event.remove(engine, 'begin', recorder.on_begin)
        sa_event.remove(engine, 'commit', recorder.on_commit)

# ################################################################################################################################
# ################################################################################################################################

def get_expected(dialect_name:'str', parts:'anylist') -> 'anylist':
    """ Returns the statements of a transaction of the given parts, opened and committed. On SQLite, the driver opens
    the transaction before the first statement that writes, so the selects that precede it run before it.
    """
    out:'anylist' = []
    needs_begin = dialect_name == 'sqlite'

    for part in parts:
        for verb_table in part:

            # The first statement that writes opens the transaction on SQLite ..
            if needs_begin and verb_table[0] != 'SELECT':
                out.append(_begin)
                needs_begin = False

            out.append(verb_table)

    # .. and every transaction is committed.
    out.append(_commit)
    return out

# ################################################################################################################################

def get_atomic_statements(dialect_name:'str') -> 'anylist':
    """ Returns the statements of a fenced acknowledgement with one receipt, which PostgreSQL writes in a savepoint.
    """
    out:'anylist' = []

    if dialect_name == 'postgresql':
        out.append(_savepoint)

    out.extend(_statements_atomic_checks[dialect_name])
    out.extend(_statements_atomic_writes[dialect_name])

    if dialect_name == 'postgresql':
        out.append(_release)

    return out

# ################################################################################################################################

def get_event_statements(dialect_name:'str', event_count:'int', has_new_payloads:'bool') -> 'anylist':
    """ Returns the statements of the audit events of a batch. PostgreSQL reserves the ids of more than one event
    from its sequence, and a payload stored already by an earlier event is not inserted again.
    """
    out:'anylist' = [_statement_payload_select]

    if dialect_name == 'postgresql' and event_count > 1:
        out.append(_statement_event_ids_select)

    if has_new_payloads:
        out.append(_statement_payload_insert)

    out.append(_statement_event_insert)
    return out

# ################################################################################################################################

def assert_one_transaction(recorder:'TransactionRecorder', expected:'anylist') -> 'None':
    """ The batch ran the expected statements in one transaction, which it opened and committed once.
    """
    assert recorder.statements == expected, recorder.statements
    assert recorder.begin_count == 1, recorder.begin_count
    assert recorder.commit_count == 1, recorder.commit_count

    for is_open in recorder.in_transaction:
        assert is_open

# ################################################################################################################################
# ################################################################################################################################
