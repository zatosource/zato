# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from time import monotonic

# SQLAlchemy
from sqlalchemy import and_, BigInteger, cast, func, select

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.sql.browse import SQLBrowseAPI
from zato.common.pubsub.sql.config import get_batch_size
from zato.common.pubsub.sql.counts import Milliseconds_Per_Minute, No_Publisher
from zato.common.pubsub.sql.schema import delivery_table, message_table, publish_count_table, queue_count_table, \
    topic_count_table, topic_sub_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, dictlist, intlist, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How long the stored preview of each payload is.
_data_preview_len = PubSub.Message.Data_Preview_Len

# How many minutes of history the statistics cover unless told otherwise.
_default_since_minutes = 60

# ################################################################################################################################
# ################################################################################################################################

def _sum(column:'any_') -> 'any_':
    """ Adds up the rows of a count column. PostgreSQL returns the sum of a bigint column as a numeric,
    which the cast turns back into a bigint, so the statistics are integers on every database type.
    """
    out = cast(func.sum(column), BigInteger)
    return out

# ################################################################################################################################
# ################################################################################################################################

class SQLAdminAPI(SQLBrowseAPI):
    """ Queue administration and statistics - subscriber listings, depth counts,
    the publish timeline, queue clearing and whole-topic operations.
    All bulk work runs in bounded batches.
    """

    def get_subscribed_topics(self, sub_key:'str') -> 'strlist':
        """ Get list of topics a subscriber is subscribed to.
        """
        query = select(topic_sub_table.c.topic_name)
        query = query.where(topic_sub_table.c.sub_key == sub_key)

        out:'strlist' = []

        with self.engine.connect() as connection:
            for row in connection.execute(query):
                out.append(row.topic_name)

        return out

# ################################################################################################################################

    def get_sub_keys_by_prefix(self, prefix:'str') -> 'strlist':
        """ Returns every distinct subscriber key that starts with the given prefix, which is how
        subscriptions that live in memory only are found again when a server starts.
        """
        pattern = prefix + '%'

        query = select(topic_sub_table.c.sub_key)
        query = query.where(topic_sub_table.c.sub_key.like(pattern))
        query = query.distinct()

        out:'strlist' = []

        with self.engine.connect() as connection:
            for row in connection.execute(query):
                out.append(row.sub_key)

        return out

# ################################################################################################################################

    def get_pending_counts_by_prefix(self, prefix:'str') -> 'anydict':
        """ Returns how many messages wait for each subscriber key that starts with the given prefix - one grouped
        count over the delivery rows, which is how the queues of outgoing connections learn their depth at startup.
        A subscriber with nothing waiting is not in the result.
        """
        pattern = prefix + '%'
        depth = _sum(queue_count_table.c.depth)

        query = select(queue_count_table.c.sub_key, depth)
        query = query.where(queue_count_table.c.sub_key.like(pattern))
        query = query.group_by(queue_count_table.c.sub_key)
        query = query.having(depth > 0)

        out:'anydict' = {}

        with self.engine.connect() as connection:
            for sub_key, count in connection.execute(query):
                out[sub_key] = count

        return out

# ################################################################################################################################

    def get_topic_subscribers(self, topic_name:'str') -> 'strlist':
        """ Get list of subscribers for a topic.
        """
        topic_name = topic_name.lower()

        query = select(topic_sub_table.c.sub_key)
        query = query.where(topic_sub_table.c.topic_name == topic_name)

        out:'strlist' = []

        with self.engine.connect() as connection:
            for row in connection.execute(query):
                out.append(row.sub_key)

        return out

# ################################################################################################################################

    def get_topics_with_messages(self) -> 'strlist':
        """ Returns the names of all the topics that currently hold any message rows.
        """
        total = _sum(topic_count_table.c.total)

        query = select(topic_count_table.c.topic_name)
        query = query.group_by(topic_count_table.c.topic_name)
        query = query.having(total > 0)

        out:'strlist' = []

        with self.engine.connect() as connection:
            for row in connection.execute(query):
                out.append(row.topic_name)

        return out

# ################################################################################################################################

    def get_pending_depths(self, sub_topic_pairs:'anylist') -> 'anydict':
        """ Get the total pending depth for each subscriber across its topics.
        Accepts a list of (sub_key, topic_name) pairs.
        Returns a dict mapping sub_key to total pending message count.
        """

        # Every requested subscriber is present in the result, even with nothing pending ..
        out:'anydict' = {}
        requested_pairs = set()
        sub_keys:'strlist' = []

        for sub_key, topic_name in sub_topic_pairs:
            topic_name = topic_name.lower()
            requested_pairs.add((sub_key, topic_name))

            if sub_key not in out:
                out[sub_key] = 0
                sub_keys.append(sub_key)

        if not sub_keys:
            return out

        # .. one query reads the queue depths of all the requested subscribers ..
        query = select(queue_count_table.c.sub_key, queue_count_table.c.topic_name, queue_count_table.c.depth)
        query = query.where(queue_count_table.c.sub_key.in_(sub_keys))

        with self.engine.connect() as connection:
            rows = connection.execute(query).fetchall()

        # .. and only the requested (subscriber, topic) pairs count towards the totals.
        for row in rows:
            if (row.sub_key, row.topic_name) in requested_pairs:
                out[row.sub_key] = out[row.sub_key] + row.depth

        return out

# ################################################################################################################################

    def get_total_count(self, sub_key:'str', topic_name:'str', state:'str') -> 'int':
        """ Returns the total message count for a (sub_key, topic) pair by delivery state.
        """
        topic_name = topic_name.lower()

        if state == 'pending':
            out = self._count_pending(sub_key, topic_name)
            return out

        elif state == 'all':
            out = self._count_all(topic_name)
            return out

        elif state == 'delivered':

            # Delivered = total - pending ..
            total = self._count_all(topic_name)
            pending = self._count_pending(sub_key, topic_name)

            out = total - pending
            if out < 0:
                out = 0

            return out

        # .. anything else is not a recognized state.
        else:
            return 0

# ################################################################################################################################

    def _count_pending(self, sub_key:'str', topic_name:'str') -> 'int':
        """ Returns the number of delivery rows of one (subscriber, topic) pair.
        """
        query = select(_sum(queue_count_table.c.depth))
        query = query.where(and_(
            queue_count_table.c.sub_key == sub_key,
            queue_count_table.c.topic_name == topic_name,
        ))

        with self.engine.connect() as connection:
            depth = connection.execute(query).scalar()

        # A pair that never had a delivery row has no count either.
        if depth is None:
            depth = 0

        out = depth
        return out

# ################################################################################################################################

    def _count_all(self, topic_name:'str') -> 'int':
        """ Returns the number of message rows of one topic.
        """
        query = select(_sum(topic_count_table.c.total))
        query = query.where(topic_count_table.c.topic_name == topic_name)

        with self.engine.connect() as connection:
            total = connection.execute(query).scalar()

        # A topic that never had a message has no count either.
        if total is None:
            total = 0

        out = total
        return out

# ################################################################################################################################

    def _get_window_start(self, since_minutes:'int') -> 'int':
        """ Returns the start of the minute that began the given number of minutes ago, in milliseconds,
        which is where the publication statistics begin.
        """
        now_ms = self._database_now_ms()
        cutoff_ms = now_ms - since_minutes * Milliseconds_Per_Minute

        out = cutoff_ms - cutoff_ms % Milliseconds_Per_Minute
        return out

# ################################################################################################################################

    def get_publish_timeline(self, topic_names:'strlist', since_minutes:'int'=_default_since_minutes) -> 'dictlist':
        """ Return a per-minute publish count timeline aggregated across the given topics, starting with the minute
        that began since_minutes ago. Each entry is {'timestamp': <epoch_ms>, 'count': <int>}.
        """

        # Our response to produce
        out:'dictlist' = []

        if not topic_names:
            return out

        # Every minute from the start of the window counts ..
        window_start_ms = self._get_window_start(since_minutes)

        # .. normalize the topic names ..
        lowered_names:'strlist' = []

        for topic_name in topic_names:
            lowered_names.append(topic_name.lower())

        # .. add up the publication counts of each minute, across the topics and publishers ..
        minute = publish_count_table.c.minute_ms
        count = _sum(publish_count_table.c.total)

        query = select(minute, count)
        query = query.where(and_(
            publish_count_table.c.topic_name.in_(lowered_names),
            minute >= window_start_ms,
        ))
        query = query.group_by(minute)
        query = query.having(count > 0)
        query = query.order_by(minute)

        with self.engine.connect() as connection:
            rows = connection.execute(query).fetchall()

        # .. and return the minutes in ascending time order.
        for minute_ms, minute_count in rows:
            entry = {'timestamp': minute_ms, 'count': minute_count}
            out.append(entry)

        return out

# ################################################################################################################################

    def count_distinct_publishers(self, topic_names:'strlist', since_minutes:'int'=_default_since_minutes) -> 'int':
        """ Count distinct publisher identifiers across all given topics, starting with the minute
        that began since_minutes ago.
        """
        if not topic_names:
            return 0

        # Every minute from the start of the window counts ..
        window_start_ms = self._get_window_start(since_minutes)

        # .. normalize the topic names ..
        lowered_names:'strlist' = []

        for topic_name in topic_names:
            lowered_names.append(topic_name.lower())

        # .. find each publisher with anything that still exists in any of the minutes, adding up the counts
        # .. of each topic and minute, which PostgreSQL may hold in several rows ..
        publisher = publish_count_table.c.publisher
        total = _sum(publish_count_table.c.total)

        existing = select(publisher)
        existing = existing.where(and_(
            publish_count_table.c.topic_name.in_(lowered_names),
            publish_count_table.c.minute_ms >= window_start_ms,
            publisher != No_Publisher,
        ))
        existing = existing.group_by(publish_count_table.c.topic_name, publish_count_table.c.minute_ms, publisher)
        existing = existing.having(total > 0)
        existing = existing.subquery()

        # .. and count the distinct ones.
        query = select(func.count(func.distinct(existing.c.publisher)))

        with self.engine.connect() as connection:
            out = connection.execute(query).scalar()

        return out

# ################################################################################################################################

    def clear_queue(self, sub_key:'str') -> 'anydict':
        """ Clears all pending messages for a subscriber across all subscribed topics.
        Messages that no subscriber needs anymore lose their payloads and stay behind
        as delivered-message traces. Returns a dict with 'cleared_count'.
        """
        batch_size = get_batch_size()
        cleared_count = 0

        # Work in bounded batches ..
        while True:

            batch_started = monotonic()

            with self.engine.begin() as connection:

                # .. take the next batch of this subscriber's delivery rows ..
                query = select(delivery_table.c.id)
                query = query.where(delivery_table.c.sub_key == sub_key)
                query = query.limit(batch_size)

                rows = connection.execute(query).fetchall()

                if not rows:
                    break

                delivery_ids:'intlist' = []

                for row in rows:
                    delivery_ids.append(row.id)

                # .. remove the delivery rows that still exist - a consumer may have acknowledged some of them
                # .. after the batch was read, and those count as delivered, not as cleared ..
                delete_statement = delivery_table.delete()
                delete_statement = delete_statement.where(delivery_table.c.id.in_(delivery_ids))
                delete_statement = delete_statement.returning(delivery_table.c.message_id)

                deleted_rows = connection.execute(delete_statement).fetchall()

                message_ids:'intlist' = []

                for deleted_row in deleted_rows:
                    message_ids.append(deleted_row.message_id)

                # .. and drop the payloads of messages no subscriber needs anymore.
                _ = self._drop_fully_delivered_payloads(connection, message_ids)

                cleared_count += len(message_ids)

            # Let the other greenlets run between the batches.
            self._yield_after_batch(monotonic() - batch_started)

        logger.info('clear_queue -> sub_key:%s, cleared_count:%d', sub_key, cleared_count)

        out:'anydict' = {
            'cleared_count': cleared_count,
        }

        return out

# ################################################################################################################################

    def delete_message(self, sub_key:'str', topic_name:'str', msg_id:'str') -> 'bool':
        """ Deletes one message from a subscriber's queue. When no other subscriber
        needs the message, its row is removed entirely, trace included.
        Returns True if the message row itself was removed.
        """
        topic_name = topic_name.lower()

        with self.engine.begin() as connection:

            # Map the public identifier to the message row ..
            query = select(message_table.c.id)
            query = query.where(and_(
                message_table.c.msg_id == msg_id,
                message_table.c.topic_name == topic_name,
            ))
            row = connection.execute(query).fetchone()

            if row is None:
                return False

            message_id = row.id

            # .. remove this subscriber's delivery row ..
            delete_statement = delivery_table.delete()
            delete_statement = delete_statement.where(and_(
                delivery_table.c.sub_key == sub_key,
                delivery_table.c.message_id == message_id,
            ))
            _ = connection.execute(delete_statement)

            # .. check whether any other subscriber still needs the message ..
            remaining_query = select(func.count())
            remaining_query = remaining_query.select_from(delivery_table)
            remaining_query = remaining_query.where(delivery_table.c.message_id == message_id)

            remaining = connection.execute(remaining_query).scalar()

            if remaining:
                return False

            # .. no one does, so the whole row goes away, trace included.
            message_delete = message_table.delete()
            message_delete = message_delete.where(message_table.c.id == message_id)
            _ = connection.execute(message_delete)

        logger.info('delete_message -> sub_key:%s, topic_name:%s, msg_id:%s', sub_key, topic_name, msg_id)

        return True

# ################################################################################################################################

    def update_message(self, topic_name:'str', msg_id:'str', data:'str') -> 'bool':
        """ Replaces one message's payload - what the dashboard's message edit form saves.
        The size and preview follow the new payload, and encryption at rest is honored.
        Returns True if the message existed and was updated.
        """
        topic_name = topic_name.lower()

        data_size = len(data)
        data_preview = data[:_data_preview_len]

        # Encrypt the new payload at rest when configured to ..
        if self.encrypt_at_rest:
            payload = self._encrypt_payload(data)
            payload_encrypted = True
        else:
            payload = data
            payload_encrypted = False

        # .. and replace the payload with everything derived from it.
        update_statement = message_table.update()
        update_statement = update_statement.where(and_(
            message_table.c.msg_id == msg_id,
            message_table.c.topic_name == topic_name,
        ))
        update_statement = update_statement.values(
            payload=payload,
            payload_encrypted=payload_encrypted,
            data_size=data_size,
            data_preview=data_preview if data_preview else None,
        )

        with self.engine.begin() as connection:
            result = connection.execute(update_statement)

        out = result.rowcount > 0

        logger.info('update_message -> topic_name:%s, msg_id:%s, data_size:%d, updated:%s',
            topic_name, msg_id, data_size, out)

        return out

# ################################################################################################################################

    def _update_topic_name_in_batches(self, table:'any_', old_topic_name:'str', new_topic_name:'str') -> 'None':
        """ Renames a topic in one table, a bounded batch of rows at a time.
        """
        batch_size = get_batch_size()

        while True:

            batch_started = monotonic()

            with self.engine.begin() as connection:

                # Take the next batch of rows still carrying the old name ..
                query = select(table.c.id)
                query = query.where(table.c.topic_name == old_topic_name)
                query = query.limit(batch_size)

                rows = connection.execute(query).fetchall()

                if not rows:
                    break

                row_ids:'intlist' = []

                for row in rows:
                    row_ids.append(row.id)

                # .. and point them at the new name.
                update_statement = table.update()
                update_statement = update_statement.where(table.c.id.in_(row_ids))
                update_statement = update_statement.values(topic_name=new_topic_name)

                _ = connection.execute(update_statement)

            # Let the other greenlets run between the batches.
            self._yield_after_batch(monotonic() - batch_started)

# ################################################################################################################################

    def rename_topic(self, old_topic_name:'str', new_topic_name:'str') -> 'None':
        """ Renames a topic across messages, deliveries and subscriptions.
        """
        old_topic_name = old_topic_name.lower()
        new_topic_name = new_topic_name.lower()

        # Message and delivery rows can be numerous, so they go in batches ..
        self._update_topic_name_in_batches(message_table, old_topic_name, new_topic_name)
        self._update_topic_name_in_batches(delivery_table, old_topic_name, new_topic_name)

        # .. while subscriptions are few and move in one statement.
        update_statement = topic_sub_table.update()
        update_statement = update_statement.where(topic_sub_table.c.topic_name == old_topic_name)
        update_statement = update_statement.values(topic_name=new_topic_name)

        with self.engine.begin() as connection:
            result = connection.execute(update_statement)

        logger.info('rename_topic -> old:%s, new:%s, subscribers_updated:%d',
            old_topic_name, new_topic_name, result.rowcount)

# ################################################################################################################################

    def _delete_topic_rows_in_batches(self, table:'any_', topic_name:'str') -> 'None':
        """ Deletes all of one topic's rows from a table, a bounded batch at a time.
        """
        batch_size = get_batch_size()

        while True:

            batch_started = monotonic()

            with self.engine.begin() as connection:

                # Take the next batch of this topic's rows ..
                query = select(table.c.id)
                query = query.where(table.c.topic_name == topic_name)
                query = query.limit(batch_size)

                rows = connection.execute(query).fetchall()

                if not rows:
                    break

                row_ids:'intlist' = []

                for row in rows:
                    row_ids.append(row.id)

                # .. and delete them.
                delete_statement = table.delete()
                delete_statement = delete_statement.where(table.c.id.in_(row_ids))

                _ = connection.execute(delete_statement)

            # Let the other greenlets run between the batches.
            self._yield_after_batch(monotonic() - batch_started)

# ################################################################################################################################

    def delete_topic(self, topic_name:'str') -> 'None':
        """ Delete a topic and all its data - messages, deliveries and subscriptions.
        """
        topic_name = topic_name.lower()

        # Deliveries go first ..
        self._delete_topic_rows_in_batches(delivery_table, topic_name)

        # .. then the messages themselves ..
        self._delete_topic_rows_in_batches(message_table, topic_name)

        # .. and finally the topic's subscriptions.
        delete_statement = topic_sub_table.delete()
        delete_statement = delete_statement.where(topic_sub_table.c.topic_name == topic_name)

        with self.engine.begin() as connection:
            result = connection.execute(delete_statement)

        logger.info('delete_topic -> topic_name:%s, subscribers_removed:%d', topic_name, result.rowcount)

# ################################################################################################################################
# ################################################################################################################################
