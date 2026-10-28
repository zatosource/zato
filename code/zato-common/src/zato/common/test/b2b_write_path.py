# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from time import monotonic

# gevent
from gevent import sleep
from gevent.monkey import get_original

# SQLAlchemy
from sqlalchemy import create_engine, event as sa_event
from sqlalchemy.pool import StaticPool

# Zato
from zato.common.audit_log.api import metadata as audit_metadata
from zato.common.audit_log.common import AuditSource, B2BAttr
from zato.common.b2b.common.business_state import BusinessMessage
from zato.common.b2b.common.outcome import FinalState, Outcome, SignalKind
from zato.common.b2b.common.records import MessageIdentity, StoredMessage, StoredResponse
from zato.common.b2b.common.retry import RetryPolicy, RetryState
from zato.common.b2b.common.send_log import SentMessage

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import any_, anylist, strlist
    any_ = any_
    anylist = anylist
    Engine = Engine
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The moment the tests start from.
Start_Time = datetime(2026, 1, 1, tzinfo=timezone.utc)

Protocol   = 'b2b-test'
From_Party = 'b2b-partner'
To_Party   = 'b2b-host'
CPA_ID     = 'b2b-agreement'
Endpoint   = 'http://localhost/b2b'
Server     = 'b2b-server'
Source     = AuditSource.EbMS2

# How long a received message is remembered for duplicate detection.
Persist_Seconds = 3600

# The parts of the wire form of a message.
Content_Type = 'text/xml'
Wire_Body    = b'<Envelope>B2B message</Envelope>'
Signal_Body  = b'<Envelope>B2B signal</Envelope>'

# The width of the identifier columns of the B2B tables and of the audit log, and that of the columns
# of the identity of a received message.
Identifier_Width = 255
Identity_Width   = 191

# The non-ASCII texts the identifiers, attributes and bodies of the tests are made of.
Japanese_Text = '東京の受発注システムからの注文確認書'
Greek_Text    = 'Παραγγελία από την Αθήνα προς τον Πειραιά'

# How many times a text repeats in a body.
_body_repeat = 100

# The URL of an in-memory SQLite database.
_memory_url = 'sqlite://'

# The verbs that open the SQL statements the recorder classifies.
_statement_verbs = ('INSERT', 'UPDATE', 'DELETE', 'SELECT', 'MERGE')

# The events of the operating system, which a commit in the thread pool of the gevent hub waits on as well.
_Native_Event = get_original('threading', 'Event')

# How often a test checks whether a commit is waiting at the gate, in seconds.
_gate_poll_seconds = 0.005

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class RecordedStatement:
    """ One statement an engine sent to its database.
    """
    verb:        str
    table:       str
    sql:         str
    param_count: int

# ################################################################################################################################
# ################################################################################################################################

def _table_of(verb:'str', sql:'str') -> 'str':
    """ Returns the table a statement is about - the one it inserts into, updates, deletes from, merges into
    or, for a select, the first one it reads from.
    """
    upper = sql.upper()

    if verb == 'INSERT':
        marker = 'INTO '
    elif verb == 'UPDATE':
        marker = 'UPDATE '
    elif verb == 'MERGE':
        marker = 'INTO '
    else:
        marker = 'FROM '

    start = upper.index(marker) + len(marker)
    rest = sql[start:].strip()
    name = rest.split()[0]
    name = name.strip('"`(').lower()

    out = name
    return out

# ################################################################################################################################
# ################################################################################################################################

class StatementRecorder:
    """ Records each statement, commit and rollback of an engine.
    """

    def __init__(self, engine:'Engine') -> 'None':
        self.engine = engine
        self.statements:'list[RecordedStatement]' = []
        self.commits = 0
        self.rollbacks = 0

        sa_event.listen(engine, 'before_cursor_execute', self._on_execute)
        sa_event.listen(engine, 'commit', self._on_commit)
        sa_event.listen(engine, 'rollback', self._on_rollback)

    def _on_execute(self, conn:'any_', cursor:'any_', sql:'str', parameters:'any_', context:'any_', executemany:'bool') -> 'None':

        first_word = sql.strip().split()[0].upper()

        if first_word not in _statement_verbs:
            return

        statement = RecordedStatement()
        statement.verb = first_word
        statement.table = _table_of(first_word, sql)
        statement.sql = sql

        if parameters is None:
            statement.param_count = 0
        else:
            statement.param_count = len(parameters)

        self.statements.append(statement)

    def _on_commit(self, conn:'any_') -> 'None':
        self.commits += 1

    def _on_rollback(self, conn:'any_') -> 'None':
        self.rollbacks += 1

    def clear(self) -> 'None':
        self.statements = []
        self.commits = 0
        self.rollbacks = 0

    def selects(self) -> 'list[RecordedStatement]':
        out:'list[RecordedStatement]' = []

        for statement in self.statements:
            if statement.verb == 'SELECT':
                out.append(statement)

        return out

    def reads(self) -> 'list[RecordedStatement]':
        """ Returns the selects other than those by which a commit reads the identifiers of the rows it wrote.
        """
        out:'list[RecordedStatement]' = []

        for statement in self.selects():
            if 'commit_id' not in statement.sql:
                out.append(statement)

        return out

    def writes(self) -> 'strlist':
        """ Returns the verb and the table of each statement that is not a select, in the order they were sent.
        """
        out:'strlist' = []

        for statement in self.statements:
            if statement.verb != 'SELECT':
                out.append(f'{statement.verb} {statement.table}')

        return out

    def stop(self) -> 'None':
        sa_event.remove(self.engine, 'before_cursor_execute', self._on_execute)
        sa_event.remove(self.engine, 'commit', self._on_commit)
        sa_event.remove(self.engine, 'rollback', self._on_rollback)

# ################################################################################################################################
# ################################################################################################################################

class CommitGate:
    """ Holds back each commit of an engine until it is opened, and tells when a commit has started waiting.
    """

    def __init__(self, engine:'Engine') -> 'None':
        self.engine = engine
        self._is_waiting = _Native_Event()
        self._opened = _Native_Event()

        sa_event.listen(engine, 'commit', self._on_commit)

    def _on_commit(self, conn:'any_') -> 'None':
        self._is_waiting.set()
        _ = self._opened.wait()

    def wait_for_commit(self, timeout:'float') -> 'bool':
        """ Waits until a commit is held back at the gate, yielding to the event loop under gevent,
        and says whether one was within the timeout.
        """
        deadline = monotonic() + timeout

        while not self._is_waiting.is_set():
            if monotonic() >= deadline:
                break
            sleep(_gate_poll_seconds)

        out = self._is_waiting.is_set()
        return out

    def open(self) -> 'None':
        self._opened.set()

    def stop(self) -> 'None':
        self.open()
        sa_event.remove(self.engine, 'commit', self._on_commit)

# ################################################################################################################################
# ################################################################################################################################

class FailingCommit:
    """ Makes each commit of an engine fail, so that its transaction is rolled back.
    """

    def __init__(self, engine:'Engine') -> 'None':
        self.engine = engine
        sa_event.listen(engine, 'commit', self._on_commit)

    def _on_commit(self, conn:'any_') -> 'None':
        raise CommitRefused('The commit is refused by the test')

    def stop(self) -> 'None':
        sa_event.remove(self.engine, 'commit', self._on_commit)

# ################################################################################################################################

class CommitRefused(Exception):
    """ The error a commit fails with in the tests.
    """

# ################################################################################################################################
# ################################################################################################################################

class FakeMonotonic:
    """ A monotonic clock that stands still until it is advanced explicitly.
    """

    def __init__(self) -> 'None':
        self.value = 0.0

    def __call__(self) -> 'float':
        return self.value

    def advance(self, seconds:'float') -> 'None':
        self.value += seconds

# ################################################################################################################################
# ################################################################################################################################

def new_memory_engine() -> 'Engine':
    """ Returns an in-memory SQLite database with the tables of the audit log.
    """
    out = create_engine(_memory_url, poolclass=StaticPool, connect_args={'check_same_thread': False})
    audit_metadata.create_all(out)

    return out

# ################################################################################################################################

def new_identity(message_id:'str', from_party:'str'=From_Party) -> 'MessageIdentity':
    out = MessageIdentity(Protocol, from_party, To_Party, message_id)
    return out

# ################################################################################################################################

def new_stored_message(received_at:'datetime'=Start_Time, persist_seconds:'int'=Persist_Seconds) -> 'StoredMessage':

    response = StoredResponse()
    response.status_code = 200
    response.content_type = Content_Type
    response.body = b'<Acknowledgment/>'
    response.is_synchronous = True

    out = StoredMessage()
    out.status = 'Received'
    out.received_at = received_at
    out.expires_at = received_at + timedelta(seconds=persist_seconds)
    out.response = response

    return out

# ################################################################################################################################

def new_sent_message(message_id:'str', sent_at:'datetime'=Start_Time, wire_body:'bytes'=Wire_Body) -> 'SentMessage':
    """ Returns a message as a send log records it before its first delivery.
    """
    policy = RetryPolicy()
    policy.retries = 3
    policy.retry_interval = timedelta(seconds=30)

    retry_state = RetryState()
    retry_state.attempt_count = 0
    retry_state.last_attempt_at = sent_at

    outcome = Outcome()

    out = SentMessage()
    out.message_id = message_id
    out.cpa_id = CPA_ID
    out.from_party = To_Party
    out.to_party = From_Party
    out.endpoint = Endpoint
    out.attrs = {B2BAttr.Service: 'b2b-service', B2BAttr.Action: 'b2b-action'}
    out.policy = policy
    out.retry_state = retry_state
    out.outcome = outcome
    out.details = {'conversation_id': 'b2b-conversation-' + message_id}
    out.wire_headers = {'Content-Type': Content_Type}
    out.wire_body = wire_body

    return out

# ################################################################################################################################

def new_business_message(
    message_id:'str',
    sent_at:'datetime'=Start_Time,
    receipt_seconds:'int'=0,
    response_seconds:'int'=0,
    ) -> 'BusinessMessage':
    """ Returns a business message sent, with deadlines that many seconds after it was sent, zero meaning none.
    """
    out = BusinessMessage()
    out.message_id = message_id
    out.cpa_id = CPA_ID
    out.conversation_id = 'b2b-conversation-' + message_id
    out.from_party = To_Party
    out.to_party = From_Party
    out.service = 'b2b-service'
    out.action = 'b2b-action'
    out.sent_at = sent_at

    if receipt_seconds:
        out.receipt_deadline = sent_at + timedelta(seconds=receipt_seconds)

    if response_seconds:
        out.response_deadline = sent_at + timedelta(seconds=response_seconds)

    return out

# ################################################################################################################################

def fill_width(text:'str', suffix:'str'='', width:'int'=Identifier_Width) -> 'str':
    """ Returns a text repeated to the full width of a column, ending in the suffix.
    """
    length = width - len(suffix)
    repeated = text * (length // len(text) + 1)

    out = repeated[:length] + suffix
    return out

# ################################################################################################################################

def non_ascii_body(text:'str') -> 'bytes':
    body = text * _body_repeat

    out = body.encode('utf8')
    return out

# ################################################################################################################################

def non_ascii_identity(suffix:'str') -> 'MessageIdentity':
    """ Returns an identity whose parties and message identifier are Greek and Japanese and fill their columns.
    """
    protocol = fill_width(Greek_Text, width=Identity_Width)
    from_party = fill_width(Greek_Text, width=Identity_Width)
    to_party = fill_width(Japanese_Text, width=Identity_Width)
    message_id = fill_width(Japanese_Text, suffix, Identity_Width)

    out = MessageIdentity(protocol, from_party, to_party, message_id)
    return out

# ################################################################################################################################

def non_ascii_sent_message(message_id:'str') -> 'SentMessage':
    """ Returns a message sent whose agreement, parties, attributes and bytes are Greek and Japanese.
    """
    out = new_sent_message(message_id, wire_body=non_ascii_body(Japanese_Text))
    out.cpa_id = fill_width(Greek_Text)
    out.from_party = fill_width(Japanese_Text)
    out.to_party = fill_width(Greek_Text)
    out.attrs = {B2BAttr.Service: fill_width(Greek_Text), B2BAttr.Action: fill_width(Japanese_Text)}
    out.details = {'conversation_id': fill_width(Greek_Text)}

    return out

# ################################################################################################################################

def non_ascii_business_message(message_id:'str', response_seconds:'int') -> 'BusinessMessage':
    """ Returns a business message whose agreement, parties, conversation, service and action are Greek and Japanese.
    """
    out = new_business_message(message_id, response_seconds=response_seconds)
    out.cpa_id = fill_width(Greek_Text)
    out.conversation_id = fill_width(Greek_Text)
    out.from_party = fill_width(Japanese_Text)
    out.to_party = fill_width(Greek_Text)
    out.service = fill_width(Greek_Text)
    out.action = fill_width(Japanese_Text)

    return out

# ################################################################################################################################

def receipt_outcome() -> 'Outcome':
    """ Returns the outcome of an exchange that a receipt ended.
    """
    out = Outcome()
    out.delivered = True
    out.signal_kind = SignalKind.Receipt
    out.final_state = FinalState.Delivered

    return out

# ################################################################################################################################
# ################################################################################################################################
