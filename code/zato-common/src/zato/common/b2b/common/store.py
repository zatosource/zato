# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import and_, create_engine, select
from sqlalchemy.pool import StaticPool

# Zato
from zato.common.b2b.common.commit_group import get_writer, GroupCommitWriter
from zato.common.b2b.common.commit_sql import ClaimWrite, StatusWrite
from zato.common.b2b.common.records import MessageIdentity, StoredMessage, StoredResponse
from zato.common.b2b.common.schema import message_table
from zato.common.b2b.common.sequence import get_next_sequence

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.b2b.common.commit_sql import EventWrite
    from zato.common.typing_ import any_
    any_ = any_
    datetime = datetime
    EventWrite = EventWrite

# ################################################################################################################################
# ################################################################################################################################

__all__ = ['MessageIdentity', 'MessageStore', 'new_audit_store', 'new_memory_store', 'StoredMessage', 'StoredResponse']

# ################################################################################################################################
# ################################################################################################################################

# The URL of an in-memory SQLite database.
_memory_url = 'sqlite://'

# The writer of an in-memory store commits each write as soon as it arrives.
_memory_commit_interval_ms = 0

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

    def claim(self, identity:'MessageIdentity', message:'StoredMessage', event:'EventWrite | None'=None) -> 'bool':
        """ Records a received message under its identity. Returns True when this call was the first
        to record it, and False when a record of the same identity exists already that had not expired
        when the message was received. The event, if any, is committed with the claim and only if the claim succeeds.
        The call returns once the claim is committed.
        """
        write = ClaimWrite()
        write.identity = identity
        write.message = message
        write.event = event

        out = self.writer.write(write, write.row_count)
        return out

# ################################################################################################################################

    def _get(self, identity:'MessageIdentity', now:'datetime') -> 'StoredMessage | None':

        # Our response to produce
        out = None

        identity_condition = _identity_condition(identity)
        unexpired_condition = and_(identity_condition, message_table.c.expires_at > now)

        query = select(
            message_table.c.status,
            message_table.c.received_at,
            message_table.c.expires_at,
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
            out.received_at = row.received_at
            out.expires_at  = row.expires_at
            out.response    = response

        return out

# ################################################################################################################################

    def get(self, identity:'MessageIdentity', now:'datetime') -> 'StoredMessage | None':
        """ Returns the unexpired record of a received message, or None.
        """
        out = self.writer.call(self._get, identity, now)
        return out

# ################################################################################################################################

    def set_status(self, identity:'MessageIdentity', status:'str', event:'EventWrite | None'=None) -> 'None':
        """ Updates the status of a claimed message, together with the event, if any, and returns once the update
        is committed.
        """
        write = StatusWrite()
        write.identity = identity
        write.status = status
        write.event = event

        _ = self.writer.write(write, write.row_count)

# ################################################################################################################################

    def _get_next_sequence(self, conversation:'str') -> 'int | None':

        with self.engine.connect() as connection:
            out = get_next_sequence(connection, conversation)

        return out

# ################################################################################################################################

    def get_next_sequence(self, conversation:'str') -> 'int | None':
        """ Returns the sequence number expected next in an ordered conversation, or None
        when the conversation has no state yet.
        """
        out = self.writer.call(self._get_next_sequence, conversation)
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
