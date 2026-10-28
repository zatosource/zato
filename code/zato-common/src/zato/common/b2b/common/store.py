# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime

# SQLAlchemy
from sqlalchemy import and_, create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import StaticPool

# Zato
from zato.common.b2b.common.commit_group import get_writer, GroupCommitWriter
from zato.common.b2b.common.commit_sql import ClaimWrite, StatusWrite
from zato.common.b2b.common.records import HeldMessage, MessageIdentity, StoredMessage, StoredResponse, to_iso
from zato.common.b2b.common.schema import held_message_table, message_table, sequence_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from zato.common.typing_ import any_
    any_ = any_
    Connection = Connection

# ################################################################################################################################
# ################################################################################################################################

__all__ = [
    'HeldMessage', 'MessageIdentity', 'MessageStore', 'new_audit_store', 'new_memory_store', 'StoredMessage',
    'StoredResponse',
]

# ################################################################################################################################
# ################################################################################################################################

# The URL of an in-memory SQLite database.
_memory_url = 'sqlite://'

# The writer of an in-memory store commits each write as soon as it arrives.
_memory_commit_interval_ms = 0

# Each claim and each status update is one row.
_write_row_count = 1

# ################################################################################################################################
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
    Claims and status updates are committed through a group commit writer, and the unique constraint
    on the message identity makes a claim atomic.
    """

    def __init__(self, writer:'GroupCommitWriter') -> 'None':
        self.writer = writer
        self.engine = writer.engine

# ################################################################################################################################

    def claim(self, identity:'MessageIdentity', message:'StoredMessage') -> 'bool':
        """ Records a received message under its identity. Returns True when this call was the first
        to record it, and False when a record of the same identity exists already that had not expired
        when the message was received. The call returns once the claim is committed.
        """
        write = ClaimWrite()
        write.identity = identity
        write.message = message

        out = self.writer.write(write, _write_row_count)
        return out

# ################################################################################################################################

    def _get(self, identity:'MessageIdentity', now:'datetime') -> 'StoredMessage | None':

        # Our response to produce
        out = None

        now_iso = to_iso(now)
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

            # Oracle DB returns an empty value as NULL.
            content_type = row.response_content_type
            if content_type is None:
                content_type = ''

            body = row.response_body
            if body is None:
                body = b''

            response = StoredResponse()
            response.status_code    = row.response_status_code
            response.content_type   = content_type
            response.body           = body
            response.is_synchronous = row.response_is_synchronous

            out = StoredMessage()
            out.status      = row.status
            out.received_at = datetime.fromisoformat(row.received_iso)
            out.expires_at  = datetime.fromisoformat(row.expires_iso)
            out.response    = response

        return out

# ################################################################################################################################

    def get(self, identity:'MessageIdentity', now:'datetime') -> 'StoredMessage | None':
        """ Returns the unexpired record of a received message, or None.
        """
        out = self.writer.call(self._get, identity, now)
        return out

# ################################################################################################################################

    def set_status(self, identity:'MessageIdentity', status:'str') -> 'None':
        """ Updates the status of a claimed message, and returns once the update is committed.
        """
        write = StatusWrite()
        write.identity = identity
        write.status = status

        _ = self.writer.write(write, _write_row_count)

# ################################################################################################################################

    def _get_next_sequence(self, conversation:'str') -> 'int | None':

        query = select(sequence_table.c.next_sequence)
        statement = query.where(sequence_table.c.conversation == conversation)

        with self.engine.connect() as connection:
            result = connection.execute(statement)
            out = result.scalar()

        return out

# ################################################################################################################################

    def get_next_sequence(self, conversation:'str') -> 'int | None':
        """ Returns the sequence number expected next in an ordered conversation, or None
        when the conversation has no state yet.
        """
        out = self.writer.call(self._get_next_sequence, conversation)
        return out

# ################################################################################################################################

    def _set_next_sequence(self, conversation:'str', sequence_number:'int') -> 'None':

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

    def set_next_sequence(self, conversation:'str', sequence_number:'int') -> 'None':
        """ Sets the sequence number expected next in an ordered conversation.
        """
        self.writer.call(self._set_next_sequence, conversation, sequence_number)

# ################################################################################################################################

    def _hold(self, conversation:'str', sequence_number:'int', message:'HeldMessage') -> 'None':

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

    def hold(self, conversation:'str', sequence_number:'int', message:'HeldMessage') -> 'None':
        """ Keeps a message that arrived before the messages preceding it in its conversation.
        A message held already under the same number stays as it is.
        """
        self.writer.call(self._hold, conversation, sequence_number, message)

# ################################################################################################################################

    def _release(self, conversation:'str', sequence_number:'int') -> 'HeldMessage | None':

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

    def release(self, conversation:'str', sequence_number:'int') -> 'HeldMessage | None':
        """ Removes and returns the held message with the given sequence number, or None.
        """
        out = self.writer.call(self._release, conversation, sequence_number)
        return out

# ################################################################################################################################
# ################################################################################################################################

def new_audit_store() -> 'MessageStore':
    """ Returns a message store in the audit log database, written to through the group commit writer of the process,
    so that one transaction holds the claims and the audit events.
    """
    writer = get_writer()

    out = MessageStore(writer)
    return out

# ################################################################################################################################

def new_memory_store() -> 'MessageStore':
    """ Returns a message store in an in-memory SQLite database, which lasts as long as the current process.
    """
    # Each connection to an in-memory SQLite database opens a database of its own,
    # so all the callers share the one connection of a static pool.
    engine = create_engine(_memory_url, poolclass=StaticPool, connect_args={'check_same_thread': False})
    writer = GroupCommitWriter(engine, interval_ms=_memory_commit_interval_ms, is_started=False)

    out = MessageStore(writer)
    return out

# ################################################################################################################################
# ################################################################################################################################
