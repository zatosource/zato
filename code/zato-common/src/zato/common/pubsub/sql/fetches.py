# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.sql.pull import delivered_topics_parameters, fetch_statement, outgoing_fetch_statement, \
    payload_statement
from zato.common.pubsub.sql.pulls import SQLPullAPI

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from zato.common.typing_ import anydict, anylist, strdict

    Connection = Connection

# ################################################################################################################################
# ################################################################################################################################

_default_max_messages = PubSub.Message.Default_Max_Messages
_default_max_len      = PubSub.Message.Default_Max_Len

# One second expressed in milliseconds.
_milliseconds_per_second = 1000

_outgoing_sub_key_prefix = PubSub.Outgoing.Sub_Key_Prefix

# ################################################################################################################################
# ################################################################################################################################

class SQLFetchAPI(SQLPullAPI):
    """ The reads of the messages of push subscribers and of the queues of outgoing connections, with the payloads
    that the payload cache does not keep.
    """

    def read_payload(self, message:'anydict') -> 'str':
        """ Reads the payload of one fetched message from the database, which is the payload of its most recent edit.
        """
        parameters = {'payload_message_ids': [message['sequence_id']]}

        with self.engine.connect() as connection:
            row = payload_statement.execute(connection, parameters).one()

        out = self._load_payload_from_row(row)
        return out

# ################################################################################################################################

    def _get_cached_payloads(self, rows:'anylist') -> 'tuple[strdict, anydict]':
        """ Returns the payloads of the given message rows that the payload cache keeps, by message ID,
        and the rows whose payloads it does not keep, by the primary keys of their messages.
        """
        payload_cache = self.payload_cache

        payloads:'strdict' = {}
        missing:'anydict' = {}

        for row in rows:
            payload = payload_cache.get(row.msg_id)
            if payload is None:
                missing[row.id] = row
            else:
                payloads[row.msg_id] = payload

        out = (payloads, missing)
        return out

# ################################################################################################################################

    def _read_missing_payloads(
        self,
        connection:'Connection',
        missing:'anydict',
        payloads:'strdict',
        read_epoch:'int',
        ) -> 'None':
        """ Reads in one query the payloads of the message rows that the payload cache does not keep, adds them
        to the given payloads, by message ID, and keeps those that were read under the given payload epoch.
        """
        payload_parameters = {'payload_message_ids': list(missing)}
        payload_rows = payload_statement.execute(connection, payload_parameters).fetchall()

        for payload_row in payload_rows:
            row = missing[payload_row.id]
            payload = self._load_payload_from_row(payload_row)
            payloads[row.msg_id] = payload

            # A payload that was dropped already is not kept.
            if payload_row.payload is not None:
                self.payload_cache.put(row.msg_id, payload, row.data_size, read_epoch)

        # A message that left the database between the two queries has no payload, the same as a dropped one.
        for row in missing.values():
            if row.msg_id not in payloads:
                payloads[row.msg_id] = ''

# ################################################################################################################################

    def _fetch_rows(self, sub_key:'str', max_messages:'int') -> 'tuple[anylist, strdict]':
        """ Reads the subscriber's deliverable messages in (priority highest-first,
        publication order) sequence - one index-ordered query no matter the backlog depth -
        and their payloads by msg_id, reading from the database only those that the payload cache does not have.
        """
        parameters = {
            'fetch_sub_key': sub_key,
            'fetch_max_messages': max_messages,
        }

        if sub_key.startswith(_outgoing_sub_key_prefix):
            statement = outgoing_fetch_statement
        else:
            statement = fetch_statement
            parameters['fetch_now_ms'] = self._database_now_ms()

            # A governed subscriber receives the messages of the topics that the subscription list hands out to it alone
            delivered_topics = delivered_topics_parameters(self.subscription_list, sub_key, 'fetch')
            parameters.update(delivered_topics)

        # A payload is kept only if no edit took place from this point to the moment it is kept
        read_epoch = self.payload_cache.get_epoch()

        with self.engine.connect() as connection:
            rows:'anylist' = []
            rows.extend(statement.execute(connection, parameters))

            # The payloads kept already are used as they are ..
            payloads, missing = self._get_cached_payloads(rows)

            # .. and the others are read in one more query.
            if missing:
                self._read_missing_payloads(connection, missing, payloads, read_epoch)

        return rows, payloads

# ################################################################################################################################

    def _build_claimed_messages(self, rows:'anylist', read_epoch:'int') -> 'anylist':
        """ Builds the messages of the rows that a push claim returned, each with the ID and the attempt number
        of its delivery row, reading the payloads that the payload cache does not keep under the given epoch.
        """
        out:'anylist' = []

        if not rows:
            return out

        payloads, missing = self._get_cached_payloads(rows)

        if missing:
            with self.engine.connect() as connection:
                self._read_missing_payloads(connection, missing, payloads, read_epoch)

        for row in rows:
            data = payloads[row.msg_id]
            message = self._build_message_from_row(row, data)
            message['delivery_id'] = row.delivery_id
            message['delivery_attempt'] = row.attempt

            out.append(message)

        return out

# ################################################################################################################################

    def fetch_messages(
        self,
        sub_key:'str',
        max_messages:'int'=_default_max_messages,
        max_len:'int'=_default_max_len,
        block_ms:'int'=0,
    ) -> 'anylist':
        """ Fetch messages for a subscriber from all subscribed topics.
        Does not acknowledge messages - the caller is responsible for calling
        ack_message after successful processing. A non-zero block_ms makes an empty
        fetch wait for new messages up to that many milliseconds.
        """

        # The event is cleared before the query so a publish landing in between
        # leaves the event set and the wait returns immediately ..
        event = self.get_sub_event(sub_key)
        event.clear()

        # .. read whatever is deliverable right now ..
        rows, payloads = self._fetch_rows(sub_key, max_messages)

        # .. nothing yet - optionally wait for a publish to wake us up and look again.
        # .. A wait that times out without a wakeup means nothing was published,
        # .. so there is nothing to read and no query is issued - with thousands
        # .. of mostly idle subscribers this is what keeps the idle cost at zero ..
        if not rows:
            if block_ms:
                wait_seconds = block_ms / _milliseconds_per_second
                if event.wait(wait_seconds):
                    rows, payloads = self._fetch_rows(sub_key, max_messages)

        # .. convert the rows into message dicts, keeping within the total size budget, in the order of the queue,
        # .. except that a message larger than the budget goes out with the batch that reaches it, after the messages
        # .. ahead of it, and ends that batch, so that it never holds up its queue.
        out:'anylist' = []
        total_len = 0

        for row in rows:

            data_len = row.data_size
            is_oversized = data_len > max_len

            if out and total_len + data_len > max_len and not is_oversized:
                break

            total_len += data_len

            # The delivery row is what each push attempt is recorded in.
            data = payloads[row.msg_id]
            message = self._build_message_from_row(row, data)
            message['delivery_id'] = row.delivery_id
            message['delivery_attempt'] = row.attempt

            out.append(message)

            if is_oversized:
                break

        return out

# ################################################################################################################################

    def fetch_pending(self, sub_key:'str', max_messages:'int'=_default_max_messages) -> 'anylist':
        """ Fetch not-yet-acknowledged messages for a subscriber.
        Used on startup to pick up messages that were not delivered before the process
        stopped - after a restart or an active-standby takeover.
        """
        out = self.fetch_messages(sub_key, max_messages=max_messages)
        return out

# ################################################################################################################################
# ################################################################################################################################
