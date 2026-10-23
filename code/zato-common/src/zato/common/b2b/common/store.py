# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import datetime
from logging import getLogger
from threading import Lock
from typing import NamedTuple

# SQLAlchemy
from sqlalchemy import and_, BigInteger, Boolean, Column, create_engine, Index, Integer, LargeBinary, MetaData, select, String, \
    Table, UniqueConstraint
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import StaticPool

# Zato
from zato.common.b2b.common.exceptions import B2BException

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import any_
    any_ = any_
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

class MessageIdentity(NamedTuple):
    """ What makes one received message the same message when it arrives again.
    """
    protocol:   str
    from_party: str
    to_party:   str
    message_id: str

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class StoredResponse:
    """ The response signal that answered a received message, kept so that a duplicate gets the same one.
    """
    status_code:    int
    content_type:   str
    body:           bytes
    is_synchronous: bool

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class StoredMessage:
    """ One received message as the store remembers it.
    """
    status:      str
    received_at: 'datetime'
    expires_at:  'datetime'
    response:    StoredResponse

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class HeldMessage:
    """ A received message whose delivery waits for the messages that precede it in its sequence.
    """
    content_type: str
    body:         bytes

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Maximum length of the identifier columns.
_short_column_len = 255

# Retention runs after every that many claims.
_retention_check_interval = 1000

# The URL of an in-memory SQLite database.
_memory_url = 'sqlite://'

# ################################################################################################################################
# ################################################################################################################################

metadata = MetaData()

# Row identifiers are 64-bit, except under SQLite where the autoincrement
# primary key must be a plain INTEGER to become an alias of the built-in rowid.
_sqlite_id_column_type = Integer()
_id_column_type = BigInteger().with_variant(_sqlite_id_column_type, 'sqlite')

_short_column = String(_short_column_len)

# ################################################################################################################################

message_table = Table('b2b_message', metadata,
    Column('id', _id_column_type, primary_key=True, autoincrement=True),
    Column('protocol', _short_column, nullable=False),
    Column('from_party', _short_column, nullable=False),
    Column('to_party', _short_column, nullable=False),
    Column('message_id', _short_column, nullable=False),
    Column('status', _short_column, nullable=False),
    Column('received_iso', _short_column, nullable=False),
    Column('expires_iso', _short_column, nullable=False),
    Column('response_status_code', Integer, nullable=False),
    Column('response_content_type', _short_column, nullable=False),
    Column('response_body', LargeBinary, nullable=False),
    Column('response_is_synchronous', Boolean, nullable=False),
    UniqueConstraint('protocol', 'from_party', 'to_party', 'message_id', name='uq_b2b_message_identity'),

    # Retention deletes on the expiry time, which without this index means reading the whole table on every run.
    Index('idx_b2b_message_expires', 'expires_iso'),
)

sequence_table = Table('b2b_sequence', metadata,
    Column('conversation', _short_column, primary_key=True),
    Column('next_sequence', BigInteger, nullable=False),
)

held_message_table = Table('b2b_held_message', metadata,
    Column('id', _id_column_type, primary_key=True, autoincrement=True),
    Column('conversation', _short_column, nullable=False),
    Column('sequence_number', BigInteger, nullable=False),
    Column('content_type', _short_column, nullable=False),
    Column('body', LargeBinary, nullable=False),
    UniqueConstraint('conversation', 'sequence_number', name='uq_b2b_held_message'),
)

# ################################################################################################################################
# ################################################################################################################################

def _to_iso(when:'datetime') -> 'str':
    """ Returns a UTC datetime in the one ISO form the timestamp columns are compared in.
    """
    out = when.isoformat(timespec='microseconds')
    return out

# ################################################################################################################################

def _identity_condition(identity:'MessageIdentity') -> 'any_':
    """ Returns the condition that selects the row of one message identity.
    """
    out = and_(
        message_table.c.protocol == identity.protocol,
        message_table.c.from_party == identity.from_party,
        message_table.c.to_party == identity.to_party,
        message_table.c.message_id == identity.message_id,
    )

    return out

# ################################################################################################################################
# ################################################################################################################################

class MessageStore:
    """ The state the B2B protocol layers keep between messages - received message identifiers
    with their responses and statuses, and the sequence state of ordered conversations - in a SQL database.
    The unique constraint on the message identity makes a claim atomic.
    """

    def __init__(self, engine:'Engine') -> 'None':
        self.engine = engine

        # The schema creation is idempotent.
        metadata.create_all(self.engine)

        # Counts claims so that retention runs periodically instead of on every write.
        self._claim_count_lock = Lock()
        self._claim_count = 0

# ################################################################################################################################

    def _insert(self, identity:'MessageIdentity', message:'StoredMessage') -> 'bool':
        """ Inserts the row of one message. Returns False when the identity has a row already.
        """
        values = {
            'protocol': identity.protocol,
            'from_party': identity.from_party,
            'to_party': identity.to_party,
            'message_id': identity.message_id,
            'status': message.status,
            'received_iso': _to_iso(message.received_at),
            'expires_iso': _to_iso(message.expires_at),
            'response_status_code': message.response.status_code,
            'response_content_type': message.response.content_type,
            'response_body': message.response.body,
            'response_is_synchronous': message.response.is_synchronous,
        }

        insert = message_table.insert()
        statement = insert.values(**values)

        # A constraint violation means the identity is already recorded.
        try:
            with self.engine.begin() as connection:
                _ = connection.execute(statement)
            out = True
        except IntegrityError:
            out = False

        return out

# ################################################################################################################################

    def claim(self, identity:'MessageIdentity', message:'StoredMessage', now:'datetime') -> 'bool':
        """ Records a received message under its identity. Returns True when this call was the first
        to record it, and False when an unexpired record of the same identity exists already.
        """

        # Try to record the message as new ..
        out = self._insert(identity, message)

        # .. if it exists already, it may be an expired record, which is replaced ..
        if not out:
            now_iso = _to_iso(now)
            identity_condition = _identity_condition(identity)
            expired_condition = and_(identity_condition, message_table.c.expires_iso <= now_iso)

            delete = message_table.delete()
            delete_statement = delete.where(expired_condition)

            with self.engine.begin() as connection:
                result = connection.execute(delete_statement)

            # .. and only a deleted expired record makes room for this one.
            if result.rowcount:
                out = self._insert(identity, message)

        # Periodically delete the expired records of all the messages.
        with self._claim_count_lock:
            self._claim_count += 1
            is_retention_due = self._claim_count % _retention_check_interval == 0

        if is_retention_due:
            self._run_retention(now)

        return out

# ################################################################################################################################

    def get(self, identity:'MessageIdentity', now:'datetime') -> 'StoredMessage | None':
        """ Returns the unexpired record of a received message, or None.
        """

        # Our response to produce
        out = None

        now_iso = _to_iso(now)
        identity_condition = _identity_condition(identity)
        unexpired_condition = and_(identity_condition, message_table.c.expires_iso > now_iso)

        query = select(
            message_table.c.status,
            message_table.c.received_iso,
            message_table.c.expires_iso,
            message_table.c.response_status_code,
            message_table.c.response_content_type,
            message_table.c.response_body,
            message_table.c.response_is_synchronous,
        )
        statement = query.where(unexpired_condition)

        with self.engine.connect() as connection:
            result = connection.execute(statement)
            row = result.first()

        if row is not None:

            response = StoredResponse()
            response.status_code    = row.response_status_code
            response.content_type   = row.response_content_type
            response.body           = row.response_body
            response.is_synchronous = row.response_is_synchronous

            out = StoredMessage()
            out.status      = row.status
            out.received_at = datetime.fromisoformat(row.received_iso)
            out.expires_at  = datetime.fromisoformat(row.expires_iso)
            out.response    = response

        return out

# ################################################################################################################################

    def set_status(self, identity:'MessageIdentity', status:'str') -> 'None':
        """ Updates the status of a claimed message.
        """

        identity_condition = _identity_condition(identity)

        update = message_table.update()
        update = update.where(identity_condition)
        statement = update.values(status=status)

        with self.engine.begin() as connection:
            result = connection.execute(statement)

        # Only a message that was claimed has a status to update.
        if not result.rowcount:
            raise B2BException(f'Message `{identity.message_id}` from `{identity.from_party}` is not in the store')

# ################################################################################################################################

    def get_next_sequence(self, conversation:'str') -> 'int | None':
        """ Returns the sequence number expected next in an ordered conversation, or None
        when the conversation has no state yet.
        """

        query = select(sequence_table.c.next_sequence)
        statement = query.where(sequence_table.c.conversation == conversation)

        with self.engine.connect() as connection:
            result = connection.execute(statement)
            out = result.scalar()

        return out

# ################################################################################################################################

    def set_next_sequence(self, conversation:'str', sequence_number:'int') -> 'None':
        """ Sets the sequence number expected next in an ordered conversation.
        """

        update = sequence_table.update()
        update = update.where(sequence_table.c.conversation == conversation)
        update_statement = update.values(next_sequence=sequence_number)

        insert = sequence_table.insert()
        insert_statement = insert.values(conversation=conversation, next_sequence=sequence_number)

        # Update the existing state, or create it for a conversation that has none yet.
        with self.engine.begin() as connection:
            result = connection.execute(update_statement)

            if not result.rowcount:
                _ = connection.execute(insert_statement)

# ################################################################################################################################

    def hold(self, conversation:'str', sequence_number:'int', message:'HeldMessage') -> 'None':
        """ Keeps a message that arrived before the messages preceding it in its conversation.
        A message held already under the same number stays as it is.
        """

        insert = held_message_table.insert()
        statement = insert.values(
            conversation=conversation,
            sequence_number=sequence_number,
            content_type=message.content_type,
            body=message.body,
        )

        try:
            with self.engine.begin() as connection:
                _ = connection.execute(statement)
        except IntegrityError:
            pass

# ################################################################################################################################

    def release(self, conversation:'str', sequence_number:'int') -> 'HeldMessage | None':
        """ Removes and returns the held message with the given sequence number, or None.
        """

        # Our response to produce
        out = None

        condition = and_(
            held_message_table.c.conversation == conversation,
            held_message_table.c.sequence_number == sequence_number,
        )

        query = select(held_message_table.c.content_type, held_message_table.c.body)
        select_statement = query.where(condition)

        delete = held_message_table.delete()
        delete_statement = delete.where(condition)

        with self.engine.begin() as connection:
            result = connection.execute(select_statement)
            row = result.first()

            if row is not None:
                _ = connection.execute(delete_statement)

                out = HeldMessage()
                out.content_type = row.content_type
                out.body = row.body

        return out

# ################################################################################################################################

    def _run_retention(self, now:'datetime') -> 'None':
        """ Deletes the records of messages whose duplicate detection window has passed.
        """
        now_iso = _to_iso(now)

        delete = message_table.delete()
        statement = delete.where(message_table.c.expires_iso <= now_iso)

        with self.engine.begin() as connection:
            result = connection.execute(statement)

        deleted_count = result.rowcount

        if deleted_count:

            if deleted_count == 1:
                suffix = 'record'
            else:
                suffix = 'records'

            logger.info('B2B message store retention deleted %d %s that expired before %s', deleted_count, suffix, now_iso)

# ################################################################################################################################
# ################################################################################################################################

def new_memory_store() -> 'MessageStore':
    """ Returns a message store in an in-memory SQLite database, which lasts as long as the current process.
    """
    # Each connection to an in-memory SQLite database opens a database of its own,
    # so all the callers share the one connection of a static pool.
    engine = create_engine(_memory_url, poolclass=StaticPool, connect_args={'check_same_thread': False})

    out = MessageStore(engine)
    return out

# ################################################################################################################################
# ################################################################################################################################
