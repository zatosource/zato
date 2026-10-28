# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from logging import getLogger

# SQLAlchemy
from sqlalchemy import and_, bindparam, Boolean, case, delete, insert, LargeBinary, select, text, update
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.compiler import InsertmanyvaluesSentinelOpts

# Zato
from zato.common.audit_log.api import build_attr_rows, event_attr_table, event_body_table, event_table
from zato.common.audit_log.attachment import build_attachment_rows
from zato.common.b2b.common.exceptions import B2BException
from zato.common.b2b.common.records import MessageIdentity, to_iso
from zato.common.b2b.common.schema import message_table, open_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, Dialect
    from zato.common.audit_log.buffer import PendingEvent
    from zato.common.b2b.common.records import StoredMessage
    from zato.common.typing_ import any_, anylist, stranydict, strlist
    any_ = any_
    anylist = anylist
    Connection = Connection
    Dialect = Dialect
    PendingEvent = PendingEvent
    StoredMessage = StoredMessage
    stranydict = stranydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The databases whose claim statement is an upsert that returns the rows it claimed.
_returning_claim_dialects = ('postgresql', 'sqlite')

_dialect_mysql  = 'mysql'
_dialect_oracle = 'oracle'

# How many times a claim statement on Oracle DB is repeated when a concurrent transaction committed the same
# message between the match of its MERGE and its insert.
_oracle_merge_attempts = 3

# How many values one IN list holds, below the limit of 1,000 that Oracle DB has.
_in_list_size = 500

# The columns that make up the identity of a received message.
_identity_columns = ('protocol', 'from_party', 'to_party', 'message_id')

# The columns a claim replaces in an expired record. The expiry time comes last, because MySQL evaluates
# the assignments of ON DUPLICATE KEY UPDATE in order, and each of them compares against the expiry time of the old record.
_replaced_columns = (
    'status',
    'received_iso',
    'response_status_code',
    'response_content_type',
    'response_body',
    'response_is_synchronous',
    'commit_id',
    'expires_iso',
)

# The claim statement of Oracle DB. A MERGE with one source row is executed with an array of parameter sets.
_oracle_merge = """
MERGE INTO b2b_message t
USING (
    SELECT
        :protocol AS protocol,
        :from_party AS from_party,
        :to_party AS to_party,
        :message_id AS message_id,
        :status AS status,
        :received_iso AS received_iso,
        :expires_iso AS expires_iso,
        :response_status_code AS response_status_code,
        :response_content_type AS response_content_type,
        :response_body AS response_body,
        :response_is_synchronous AS response_is_synchronous,
        :commit_id AS commit_id
    FROM dual
) s
ON (
    t.protocol = s.protocol AND
    t.from_party = s.from_party AND
    t.to_party = s.to_party AND
    t.message_id = s.message_id
)
WHEN MATCHED THEN UPDATE SET
    t.status = s.status,
    t.received_iso = s.received_iso,
    t.expires_iso = s.expires_iso,
    t.response_status_code = s.response_status_code,
    t.response_content_type = s.response_content_type,
    t.response_body = s.response_body,
    t.response_is_synchronous = s.response_is_synchronous,
    t.commit_id = s.commit_id
    WHERE t.expires_iso <= s.received_iso
WHEN NOT MATCHED THEN INSERT (
    id, protocol, from_party, to_party, message_id, status, received_iso, expires_iso,
    response_status_code, response_content_type, response_body, response_is_synchronous, commit_id
) VALUES (
    b2b_message_id_seq.NEXTVAL, s.protocol, s.from_party, s.to_party, s.message_id, s.status, s.received_iso,
    s.expires_iso, s.response_status_code, s.response_content_type, s.response_body, s.response_is_synchronous,
    s.commit_id
)
"""

# ################################################################################################################################
# ################################################################################################################################

class WriteKind:
    """ What one write of a transaction does.
    """
    Claim  = 'claim'
    Status = 'status'
    Event  = 'event'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ClaimWrite:
    """ Records a received message under its identity, unless an unexpired record of it exists.
    The result of the write is True for the copy that recorded it.
    """
    identity: 'MessageIdentity'
    message:  'StoredMessage'

    kind = WriteKind.Claim

# ################################################################################################################################

@dataclass(init=False)
class StatusWrite:
    """ Updates the status of a claimed message.
    """
    identity: 'MessageIdentity'
    status:   'str'

    kind = WriteKind.Status

# ################################################################################################################################

@dataclass(init=False)
class EventWrite:
    """ Inserts one audit event with its attributes and bodies, and opens or closes the records of the exchange
    and of the business transaction the event starts or ends. The result of the write is the identifier of the event.
    """
    pending: 'PendingEvent'

    # The kinds of open records the event closes and the kinds it opens.
    closes: 'strlist'
    opens:  'strlist'

    kind = WriteKind.Event

    def __init__(self) -> 'None':
        self.closes = []
        self.opens = []

    @property
    def row_count(self) -> 'int':
        """ How many rows the write inserts or deletes - the event, its attributes, its bodies and its open records.
        """
        pending = self.pending

        out = 1
        out += len(pending.attrs)
        out += len(pending.bodies)
        out += len(pending.attachments)
        out += len(self.closes)
        out += len(self.opens)

        return out

# ################################################################################################################################
# ################################################################################################################################

def _message_row(identity:'MessageIdentity', message:'StoredMessage', commit_id:'str') -> 'stranydict':
    response = message.response

    out:'stranydict' = {
        'protocol': identity.protocol,
        'from_party': identity.from_party,
        'to_party': identity.to_party,
        'message_id': identity.message_id,
        'status': message.status,
        'received_iso': to_iso(message.received_at),
        'expires_iso': to_iso(message.expires_at),
        'response_status_code': response.status_code,
        'response_content_type': response.content_type,
        'response_body': response.body,
        'response_is_synchronous': response.is_synchronous,
        'commit_id': commit_id,
    }

    return out

# ################################################################################################################################

def _identity_of(row:'any_') -> 'MessageIdentity':
    out = MessageIdentity(row.protocol, row.from_party, row.to_party, row.message_id)
    return out

# ################################################################################################################################

def _claimed_by_commit(connection:'Connection', commit_id:'str') -> 'set[MessageIdentity]':
    """ Returns the identities of the messages one transaction claimed, on the databases whose claim statement
    returns no rows.
    """
    query = select(message_table.c.protocol, message_table.c.from_party, message_table.c.to_party,
        message_table.c.message_id)
    statement = query.where(message_table.c.commit_id == commit_id)

    out:'set[MessageIdentity]' = set()

    for row in connection.execute(statement):
        identity = _identity_of(row)
        out.add(identity)

    return out

# ################################################################################################################################

def _upsert_returning(connection:'Connection', rows:'anylist') -> 'set[MessageIdentity]':
    """ Claims messages on PostgreSQL and SQLite - an upsert that replaces only an expired record
    and returns the rows it inserted or replaced.
    """
    if connection.dialect.name == 'postgresql':
        statement = postgresql_insert(message_table)
    else:
        statement = sqlite_insert(message_table)

    excluded = statement.excluded

    replaced:'stranydict' = {}

    for name in _replaced_columns:
        replaced[name] = excluded[name]

    is_expired = message_table.c.expires_iso <= excluded.received_iso

    statement = statement.on_conflict_do_update(index_elements=list(_identity_columns), set_=replaced, where=is_expired)
    statement = statement.returning(message_table.c.protocol, message_table.c.from_party, message_table.c.to_party,
        message_table.c.message_id)

    out:'set[MessageIdentity]' = set()

    for row in connection.execute(statement, rows):
        identity = _identity_of(row)
        out.add(identity)

    return out

# ################################################################################################################################

def _upsert_mysql(connection:'Connection', rows:'anylist', commit_id:'str') -> 'set[MessageIdentity]':
    """ Claims messages on MySQL - an insert whose duplicates keep their record unless it expired,
    followed by one select of the rows that carry the identifier of this transaction.
    """
    statement = mysql_insert(message_table)
    inserted = statement.inserted

    is_expired = message_table.c.expires_iso <= inserted.received_iso

    assignments:'anylist' = []

    for name in _replaced_columns:
        new_value = inserted[name]
        old_value = message_table.c[name]
        value = case((is_expired, new_value), else_=old_value)
        assignments.append((name, value))

    statement = statement.on_duplicate_key_update(assignments)
    _ = connection.execute(statement, rows)

    out = _claimed_by_commit(connection, commit_id)
    return out

# ################################################################################################################################

def _merge_oracle(connection:'Connection', rows:'anylist', commit_id:'str') -> 'set[MessageIdentity]':
    """ Claims messages on Oracle DB - a MERGE that replaces only an expired record,
    followed by one select of the rows that carry the identifier of this transaction.
    """
    statement = text(_oracle_merge)
    statement = statement.bindparams(
        bindparam('response_body', type_=LargeBinary),
        bindparam('response_is_synchronous', type_=Boolean),
    )

    # A MERGE inserts a message that another transaction inserted after the MERGE matched it,
    # which the unique constraint refuses. The statement is repeated, and it matches the message this time.
    for attempt in range(1, _oracle_merge_attempts + 1):
        try:
            _ = connection.execute(statement, rows)
        except IntegrityError:
            if attempt == _oracle_merge_attempts:
                raise
            logger.info('B2B claim statement repeated after a concurrent claim, attempt %d', attempt)
        else:
            break

    out = _claimed_by_commit(connection, commit_id)
    return out

# ################################################################################################################################

def write_claims(connection:'Connection', writes:'anylist', commit_id:'str') -> 'anylist':
    """ Claims the messages of a transaction in one statement and returns the result of each write in their order.
    A copy of a message that another write of the same transaction claims is resolved here, without the database.
    """

    # The first copy of each message goes to the database ..
    first_copies:'dict[MessageIdentity, ClaimWrite]' = {}

    for write in writes:
        if write.identity not in first_copies:
            first_copies[write.identity] = write

    # .. in the order of the identities, so that two transactions lock the rows they share in the same order ..
    identities = sorted(first_copies)

    rows:'anylist' = []

    for identity in identities:
        write = first_copies[identity]
        row = _message_row(identity, write.message, commit_id)
        rows.append(row)

    dialect_name = connection.dialect.name

    if dialect_name in _returning_claim_dialects:
        claimed = _upsert_returning(connection, rows)
    elif dialect_name == _dialect_mysql:
        claimed = _upsert_mysql(connection, rows, commit_id)
    else:
        claimed = _merge_oracle(connection, rows, commit_id)

    # .. and only the first copy of a claimed message is the one that claimed it.
    out:'anylist' = []

    for write in writes:
        is_claimed = write.identity in claimed and first_copies[write.identity] is write
        out.append(is_claimed)

    return out

# ################################################################################################################################

def _existing_identities(connection:'Connection', identities:'list[MessageIdentity]') -> 'set[MessageIdentity]':
    """ Returns which of the given messages have a record.
    """
    out:'set[MessageIdentity]' = set()

    message_ids:'strlist' = []

    for identity in identities:
        message_ids.append(identity.message_id)

    for start in range(0, len(message_ids), _in_list_size):

        chunk = message_ids[start:start + _in_list_size]

        query = select(message_table.c.protocol, message_table.c.from_party, message_table.c.to_party,
            message_table.c.message_id)
        statement = query.where(message_table.c.message_id.in_(chunk))

        for row in connection.execute(statement):
            identity = _identity_of(row)
            out.add(identity)

    return out

# ################################################################################################################################

def write_statuses(connection:'Connection', writes:'anylist') -> 'anylist':
    """ Updates the statuses of claimed messages in one statement and returns the result of each write in their order,
    an exception for a message that has no record.
    """
    conditions = and_(
        message_table.c.protocol == bindparam('b_protocol'),
        message_table.c.from_party == bindparam('b_from_party'),
        message_table.c.to_party == bindparam('b_to_party'),
        message_table.c.message_id == bindparam('b_message_id'),
    )
    statement = update(message_table).where(conditions).values(status=bindparam('b_status'))

    rows:'anylist' = []

    for write in writes:
        identity = write.identity
        rows.append({
            'b_protocol': identity.protocol,
            'b_from_party': identity.from_party,
            'b_to_party': identity.to_party,
            'b_message_id': identity.message_id,
            'b_status': write.status,
        })

    result = connection.execute(statement, rows)

    # Every write updated one row, unless a message has no record, which only a select tells apart.
    if result.rowcount == len(writes):
        existing = None
    else:
        identities:'list[MessageIdentity]' = []

        for write in writes:
            identities.append(write.identity)

        existing = _existing_identities(connection, identities)

    out:'anylist' = []

    for write in writes:
        if existing is None or write.identity in existing:
            out.append(None)
        else:
            identity = write.identity
            error = B2BException(f'Message `{identity.message_id}` from `{identity.from_party}` is not in the store')
            out.append(error)

    return out

# ################################################################################################################################

def _returns_ordered_ids(dialect:'Dialect') -> 'bool':
    """ Whether a dialect returns the identifiers of a multi-row insert in the order of its rows from one statement.
    A dialect without an implicit sentinel for an autoincrement key sends such an insert one row at a time.
    """
    if not dialect.insert_executemany_returning_sort_by_parameter_order:
        return False

    # The driver inserts the rows itself and returns their identifiers in order.
    if not dialect.use_insertmanyvalues:
        return True

    sentinel = dialect.insertmanyvalues_implicit_sentinel & InsertmanyvaluesSentinelOpts.ANY_AUTOINCREMENT

    out = bool(sentinel)
    return out

# ################################################################################################################################

def _insert_events(connection:'Connection', writes:'anylist', commit_id:'str') -> 'list[int]':
    """ Inserts the audit events of a transaction in one statement and returns their identifiers in the order
    of the writes, through RETURNING where the driver returns them from a multi-row insert, and otherwise
    through one select by the identifier of the transaction.
    """
    rows:'anylist' = []
    out:'list[int]' = []

    if _returns_ordered_ids(connection.dialect):

        for write in writes:
            rows.append(write.pending.values)

        statement = insert(event_table).returning(event_table.c.id, sort_by_parameter_order=True)
        result = connection.execute(statement, rows)

        for event_id in result.scalars():
            out.append(event_id)

    else:
        for write in writes:
            row = dict(write.pending.values)
            row['commit_id'] = commit_id
            rows.append(row)

        _ = connection.execute(insert(event_table), rows)

        query = select(event_table.c.id).where(event_table.c.commit_id == commit_id)
        statement = query.order_by(event_table.c.id)

        for event_id in connection.execute(statement).scalars():
            out.append(event_id)

    return out

# ################################################################################################################################

def write_events(connection:'Connection', writes:'anylist', commit_id:'str') -> 'anylist':
    """ Inserts the audit events of a transaction, then their attributes, their bodies and their open records,
    one statement for each table, and returns the identifier of each event in the order of the writes.
    """
    event_ids = _insert_events(connection, writes, commit_id)

    attr_rows:'anylist' = []
    body_rows:'anylist' = []
    close_rows:'anylist' = []
    open_rows:'anylist' = []

    for write, event_id in zip(writes, event_ids):

        pending = write.pending
        pending.event_id = event_id

        values = pending.values
        event_time_iso = values['event_time_iso']

        if pending.attrs:
            rows = build_attr_rows(event_id, pending.attrs)
            attr_rows.extend(rows)

        for kind, body_data in pending.bodies.items():
            body_rows.append({
                'event_id': event_id,
                'kind': kind,
                'event_time_iso': event_time_iso,
                'data': body_data,
            })

        if pending.attachments:
            rows = build_attachment_rows(event_id, event_time_iso, pending.attachments)
            body_rows.extend(rows)

        for kind in write.closes:
            close_rows.append({
                'b_kind': kind,
                'b_source': values['source'],
                'b_server_name': values['server_name'],
                'b_message_id': values['msg_id'],
            })

        for kind in write.opens:
            open_rows.append({
                'kind': kind,
                'source': values['source'],
                'server_name': values['server_name'],
                'message_id': values['msg_id'],
                'event_id': event_id,
            })

    if attr_rows:
        _ = connection.execute(insert(event_attr_table), attr_rows)

    if body_rows:
        _ = connection.execute(insert(event_body_table), body_rows)

    # A record is closed before one is opened, so that a message sent anew under the same identifier has one record.
    if close_rows:
        conditions = and_(
            open_table.c.kind == bindparam('b_kind'),
            open_table.c.source == bindparam('b_source'),
            open_table.c.server_name == bindparam('b_server_name'),
            open_table.c.message_id == bindparam('b_message_id'),
        )
        statement = delete(open_table).where(conditions)
        _ = connection.execute(statement, close_rows)

    if open_rows:
        _ = connection.execute(insert(open_table), open_rows)

    return event_ids

# ################################################################################################################################
# ################################################################################################################################
