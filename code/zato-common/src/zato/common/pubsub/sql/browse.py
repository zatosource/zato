# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# SQLAlchemy
from sqlalchemy import and_, exists, select

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.sql.core import SQLBackendCore
from zato.common.pubsub.sql.schema import delivery_table, message_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, dictnone

    browse_result = tuple['anylist', str]

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_default_page_size = PubSub.Message.Default_Max_Messages

# The cursor value meaning "start from the beginning" - or from the end when browsing in reverse.
_cursor_start = '-'

# The message columns every browse entry consumes.
_browse_columns = [
    message_table.c.id,
    message_table.c.msg_id,
    message_table.c.topic_name,
    message_table.c.priority,
    message_table.c.expiration,
    message_table.c.pub_time_iso,
    message_table.c.recv_time_iso,
    message_table.c.expiration_time_iso,
    message_table.c.data_size,
    message_table.c.data_preview,
    message_table.c.correl_id,
    message_table.c.in_reply_to,
    message_table.c.ext_client_id,
    message_table.c.publisher,
]

# The additional columns read only when the entry carries the full payload.
_browse_payload_columns = [
    message_table.c.payload,
    message_table.c.payload_encrypted,
    message_table.c.data_class,
]

def _get_browse_columns(needs_data:'bool') -> 'anylist':
    """ Returns the message columns a browse query selects.
    """
    if needs_data:
        out = _browse_columns + _browse_payload_columns
    else:
        out = list(_browse_columns)

    return out

_browse_state_handlers = {
    'pending':   '_browse_pending',
    'all':       '_browse_all',
    'delivered': '_browse_delivered',
}

# ################################################################################################################################
# ################################################################################################################################

class SQLBrowseAPI(SQLBackendCore):
    """ Cursor-based browsing of messages by delivery state - what the dashboard's
    message-list screens read. The cursor is the message's publication sequence number.
    """

    def browse_messages(
        self,
        topic_name:'str',
        sub_key:'str',
        state:'str' = 'pending',
        cursor:'str' = _cursor_start,
        page_size:'int' = _default_page_size,
        needs_data:'bool' = False,
        reverse:'bool' = False,
        ) -> 'browse_result':
        """ Browse messages in a topic filtered by delivery state.
        Dispatches to a state-specific handler method.
        Returns (messages, next_cursor) for cursor-based pagination.
        When reverse=True, returns newest messages first.
        """
        handler_name = _browse_state_handlers[state]
        handler = getattr(self, handler_name)
        out = handler(topic_name, sub_key, cursor, page_size, needs_data, reverse)

        return out

# ################################################################################################################################

    def _apply_cursor_and_order(self, query:'any_', id_column:'any_', cursor:'str', reverse:'bool') -> 'any_':
        """ Adds the cursor filter and the publication ordering to a browse query.
        """

        # Walking backwards starts from the newest message ..
        if reverse:
            if cursor != _cursor_start:
                query = query.where(id_column <= int(cursor))
            query = query.order_by(id_column.desc())

        # .. and walking forward starts from the oldest one.
        else:
            if cursor != _cursor_start:
                query = query.where(id_column >= int(cursor))
            query = query.order_by(id_column.asc())

        return query

# ################################################################################################################################

    def _compute_next_cursor(self, rows:'anylist', page_size:'int', reverse:'bool') -> 'str':
        """ Computes the next pagination cursor from the last row in the result set.
        An empty cursor means the walk is complete.
        """
        row_count = len(rows)

        if row_count < page_size:
            return ''

        # The next page starts right past the last message of this one,
        # in whichever direction the walk goes.
        last_row = rows[-1]

        if reverse:
            next_id = last_row.id - 1
        else:
            next_id = last_row.id + 1

        out = str(next_id)
        return out

# ################################################################################################################################

    def _build_browse_entry(self, row:'any_', needs_data:'bool') -> 'anydict':
        """ Builds one browse entry dict out of a message row.
        """

        # The always-present fields come first ..
        out:'anydict' = {
            'msg_id': row.msg_id,
            'sequence_id': row.id,
            'topic_name': row.topic_name,
            'priority': row.priority,
            'expiration': row.expiration,
            'pub_time_iso': row.pub_time_iso,
            'recv_time_iso': row.recv_time_iso,
            'expiration_time_iso': row.expiration_time_iso,
            'data_size': row.data_size,
            'data_preview': row.data_preview if row.data_preview else '',
        }

        # .. include optional metadata fields ..
        if row.correl_id:
            out['correl_id'] = row.correl_id

        if row.in_reply_to:
            out['in_reply_to'] = row.in_reply_to

        if row.ext_client_id:
            out['ext_client_id'] = row.ext_client_id

        if row.publisher:
            out['publisher'] = row.publisher

        # .. and optionally the full payload.
        if needs_data:
            out['data'] = self._load_payload_from_row(row)
            out['data_class'] = row.data_class if row.data_class else ''

        return out

# ################################################################################################################################

    def _build_browse_page(
        self,
        rows:'anylist',
        page_size:'int',
        needs_data:'bool',
        reverse:'bool',
        is_delivered:'bool',
        ) -> 'browse_result':
        """ Turns fetched rows into (entries, next_cursor) with a uniform delivery flag.
        """
        messages:'anylist' = []

        for row in rows:
            entry = self._build_browse_entry(row, needs_data)
            entry['is_delivered'] = is_delivered
            messages.append(entry)

        next_cursor = self._compute_next_cursor(rows, page_size, reverse)

        out = (messages, next_cursor)
        return out

# ################################################################################################################################

    def _browse_pending(
        self,
        topic_name:'str',
        sub_key:'str',
        cursor:'str',
        page_size:'int',
        needs_data:'bool',
        reverse:'bool' = False,
        ) -> 'browse_result':
        """ Returns messages that are still awaiting this subscriber's acknowledgement,
        i.e. the ones with a delivery row for the (subscriber, topic) pair.
        """

        # Normalize topic name ..
        topic_name = topic_name.lower()

        # .. pending messages are exactly the ones with a delivery row for this subscriber ..
        joined = delivery_table.join(message_table, message_table.c.id == delivery_table.c.message_id)

        query = select(*_get_browse_columns(needs_data))
        query = query.select_from(joined)
        query = query.where(and_(
            delivery_table.c.sub_key == sub_key,
            delivery_table.c.topic_name == topic_name,
        ))
        query = self._apply_cursor_and_order(query, message_table.c.id, cursor, reverse)
        query = query.limit(page_size)

        with self.engine.connect() as connection:
            rows = connection.execute(query).fetchall()

        out = self._build_browse_page(rows, page_size, needs_data, reverse, is_delivered=False)
        return out

# ################################################################################################################################

    def _browse_all(
        self,
        topic_name:'str',
        sub_key:'str',
        cursor:'str',
        page_size:'int',
        needs_data:'bool',
        reverse:'bool' = False,
        ) -> 'browse_result':
        """ Returns all messages in the topic regardless of delivery state,
        stamping each with whether this subscriber still has it pending.
        """

        # Normalize topic name ..
        topic_name = topic_name.lower()

        # .. a left join tells for each message whether this subscriber still needs it ..
        join_condition = and_(
            delivery_table.c.message_id == message_table.c.id,
            delivery_table.c.sub_key == sub_key,
        )
        joined = message_table.outerjoin(delivery_table, join_condition)

        delivery_row_id = delivery_table.c.id.label('delivery_row_id')

        query = select(*_get_browse_columns(needs_data), delivery_row_id)
        query = query.select_from(joined)
        query = query.where(message_table.c.topic_name == topic_name)
        query = self._apply_cursor_and_order(query, message_table.c.id, cursor, reverse)
        query = query.limit(page_size)

        with self.engine.connect() as connection:
            rows = connection.execute(query).fetchall()

        # .. build the entries, stamping delivery status per message.
        messages:'anylist' = []

        for row in rows:
            entry = self._build_browse_entry(row, needs_data)
            entry['is_delivered'] = row.delivery_row_id is None
            messages.append(entry)

        next_cursor = self._compute_next_cursor(rows, page_size, reverse)

        out = (messages, next_cursor)
        return out

# ################################################################################################################################

    def _browse_delivered(
        self,
        topic_name:'str',
        sub_key:'str',
        cursor:'str',
        page_size:'int',
        needs_data:'bool',
        reverse:'bool' = False,
        ) -> 'browse_result':
        """ Returns only messages this subscriber does not have pending anymore.
        """

        # Normalize topic name ..
        topic_name = topic_name.lower()

        # .. a message is delivered for this subscriber when no delivery row references it ..
        still_pending = exists()
        still_pending = still_pending.where(and_(
            delivery_table.c.message_id == message_table.c.id,
            delivery_table.c.sub_key == sub_key,
        ))

        query = select(*_get_browse_columns(needs_data))
        query = query.where(and_(
            message_table.c.topic_name == topic_name,
            ~still_pending,
        ))
        query = self._apply_cursor_and_order(query, message_table.c.id, cursor, reverse)
        query = query.limit(page_size)

        with self.engine.connect() as connection:
            rows = connection.execute(query).fetchall()

        out = self._build_browse_page(rows, page_size, needs_data, reverse, is_delivered=True)
        return out

# ################################################################################################################################

    def get_message_details(self, topic_name:'str', msg_id:'str') -> 'dictnone':
        """ Returns one message's full details, payload included, or None if it does not exist.
        """

        # Normalize topic name ..
        topic_name = topic_name.lower()

        # .. read the message row by its public identifier ..
        query = select(*_get_browse_columns(needs_data=True))
        query = query.where(and_(
            message_table.c.msg_id == msg_id,
            message_table.c.topic_name == topic_name,
        ))

        with self.engine.connect() as connection:
            row = connection.execute(query).fetchone()

        if row is None:
            return None

        # .. and build the full entry, payload included.
        out = self._build_browse_entry(row, needs_data=True)
        return out

# ################################################################################################################################
# ################################################################################################################################
