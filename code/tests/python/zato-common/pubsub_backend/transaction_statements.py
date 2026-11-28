# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The statements of one batch of the pub/sub writer - how they are recorded by verb and table, with the transactions
# they run in, and the statements that each part of a batch is expected to run.

# stdlib
from contextlib import contextmanager

# gevent
import gevent
from gevent import getcurrent

# SQLAlchemy
from sqlalchemy import event as sa_event

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from gevent import Greenlet
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import any_, anydict, anylist, anytuple, callable_, strlist

    any_ = any_
    anydict = anydict
    anylist = anylist
    anytuple = anytuple
    callable_ = callable_
    Engine = Engine
    strlist = strlist
    Greenlet = Greenlet

    recordergen = Iterator['TransactionRecorder']

# ################################################################################################################################
# ################################################################################################################################

# The statements that close a transaction and open and close a savepoint
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

# The words that precede UPDATE in a row lock clause, e.g. FOR UPDATE or FOR NO KEY UPDATE
_lock_clause_words = {'FOR', 'KEY'}

# ################################################################################################################################
# ################################################################################################################################

_statement_payload_select   = ('SELECT', 'event_payload')
_statement_payload_insert   = ('INSERT', 'event_payload')
_statement_event_insert     = ('INSERT', 'event')

# The statements of each part of a transaction, by verb and table. A publication writes its dedup record
# before it reads the subscribers, stores a new payload in the payload table of the audit log, and writes its message
# that references the payload.
statements_publication = [
    ('INSERT', 'zato_message_dedup'), ('SELECT', 'pubsub_topic_sub'), _statement_payload_select, _statement_payload_insert,
    ('INSERT', 'pubsub_message'), ('INSERT', 'pubsub_delivery'),
]

# A publication that hands the row of one subscriber over to a waiting pull or an idle push greenlet inserts that row
# first, leased or attempted once, and the rows of the other subscribers after it.
statements_publication_claimed = [
    ('INSERT', 'zato_message_dedup'), ('SELECT', 'pubsub_topic_sub'), _statement_payload_select, _statement_payload_insert,
    ('INSERT', 'pubsub_message'), ('INSERT', 'pubsub_delivery'), ('INSERT', 'pubsub_delivery'),
]

statements_ack = [
    ('SELECT', 'pubsub_message'), ('SELECT', 'pubsub_delivery'), ('DELETE', 'pubsub_delivery'),
]

_statements_atomic_checks = [
    ('SELECT', 'pubsub_message'), ('SELECT', 'zato_message_dedup'), ('SELECT', 'pubsub_delivery'),
]

_statements_atomic_writes = [
    ('INSERT', 'zato_message_dedup'), ('SELECT', 'pubsub_topic_sub'), _statement_payload_select, _statement_payload_insert,
    ('INSERT', 'pubsub_message'), ('INSERT', 'pubsub_delivery'), ('DELETE', 'pubsub_delivery'),
]

statements_attempts = [
    ('UPDATE', 'pubsub_delivery'),
]

# The lease is one statement, whose common table expressions lock, select and update the delivery rows
statements_lease = [
    ('UPDATE', 'pubsub_delivery'),
]

statements_drop = [
    ('SELECT', 'pubsub_message'), ('SELECT', 'pubsub_message'), ('UPDATE', 'pubsub_message'),
]

# ################################################################################################################################
# ################################################################################################################################

class TransactionRecorder:
    """ The statements that SQLAlchemy sends through an engine by verb and table, each with whether a transaction
    was open when it was sent, with the transactions they ran in.

    Only the transactions of the code under test are recorded - those of the greenlet that opened the recording
    and of the greenlets spawned through the recorder. The background tasks of the process that run their transactions
    on the same engine in a greenlet of their own, such as the merger of the search indexes of the audit log,
    are not recorded.
    """

    def __init__(self) -> 'None':
        self.statements:'anylist' = []
        self.in_transaction:'anylist' = []
        self.begin_count = 0
        self.commit_count = 0
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
        out = getcurrent() in self.greenlets
        return out

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

        # The commit goes through the driver, so it is recorded here rather than as a statement.
        self.commit_count += 1
        self.statements.append(_commit)
        self.in_transaction.append(True)

# ################################################################################################################################

def _get_modifying_verb_table(words:'strlist') -> 'anytuple | None':
    """ Returns the verb and the table of the first data-modifying statement of a statement with common
    table expressions, or None if it modifies no table. A row lock clause, e.g. FOR NO KEY UPDATE OF,
    is not a data-modifying statement.
    """
    for index, word in enumerate(words):
        if word == 'INSERT' and words[index + 1] == 'INTO':
            out = ('INSERT', words[index + 2].split('(')[0])
            return out

        if word == 'UPDATE' and words[index - 1] not in _lock_clause_words:
            out = ('UPDATE', words[index + 1])
            return out

        if word == 'DELETE' and words[index + 1] == 'FROM':
            out = ('DELETE', words[index + 2])
            return out

    return None

# ################################################################################################################################

def get_verb_table(statement:'str') -> 'anytuple | None':
    """ Returns the verb and the table of a statement, the verb alone for a statement of a transaction
    or a savepoint, and None for any other statement.
    """
    words = statement.split()
    verb = words[0]

    if verb == 'WITH':
        out = _get_modifying_verb_table(words)
        return out

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
    recorder = TransactionRecorder()

    sa_event.listen(engine, 'before_cursor_execute', recorder.on_execute)
    sa_event.listen(engine, 'begin', recorder.on_begin)
    sa_event.listen(engine, 'commit', recorder.on_commit)

    try:
        yield recorder
    finally:
        sa_event.remove(engine, 'before_cursor_execute', recorder.on_execute)
        sa_event.remove(engine, 'begin', recorder.on_begin)
        sa_event.remove(engine, 'commit', recorder.on_commit)

# ################################################################################################################################
# ################################################################################################################################

def get_expected(parts:'anylist') -> 'anylist':
    """ Returns the statements of a transaction of the given parts, in their order, followed by its commit.
    """
    out:'anylist' = []

    for part in parts:
        out.extend(part)

    out.append(_commit)
    return out

# ################################################################################################################################

def get_atomic_statements() -> 'anylist':
    """ Returns the statements of a fenced acknowledgement with one receipt, which runs in a savepoint.
    """
    out:'anylist' = [_savepoint]

    out.extend(_statements_atomic_checks)
    out.extend(_statements_atomic_writes)
    out.append(_release)

    return out

# ################################################################################################################################

def get_event_statements(has_new_payloads:'bool') -> 'anylist':
    """ Returns the statements of the audit events of a batch. The events take their ids from their sequence
    in the statement that inserts them, and a payload stored already by an earlier event is not inserted again.
    """
    out:'anylist' = [_statement_payload_select]

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
