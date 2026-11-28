# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# SQLAlchemy
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert

# Zato
from zato.common.audit_log.payload import store_payloads
from zato.common.db_env.any_of import any_of
from zato.common.db_env.pg8000_copy import copy_rows
from zato.common.db_env.plain_sql import PlainStatement
from zato.common.pubsub.sql.dedup import rewrite_fingerprints, write_dedup_records
from zato.common.pubsub.sql.errors import PubSubDuplicateMsgID
from zato.common.pubsub.sql.payloads import get_chunks
from zato.common.pubsub.sql.schema import delivery_table, message_table, topic_sub_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from zato.common.pubsub.sql.fast_path import FastPath, FastPathClaims
    from zato.common.pubsub.sql.pending import pending_publication_list
    from zato.common.pubsub.subscription_list import pairlist
    from zato.common.typing_ import anydict, anylist, strlist, strstrdict
    from zato_common_core.zato_common_core import SubscriptionList

    # Dummy assignments to satisfy type checkers
    Connection = Connection
    FastPath = FastPath
    FastPathClaims = FastPathClaims
    pending_publication_list = pending_publication_list
    pairlist = pairlist
    SubscriptionList = SubscriptionList

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# From how many delivery rows on, a commit writes them with COPY rather than with multi-row inserts.
_copy_min_delivery_rows = 200

# The statements of a group commit are built once here, the bind parameters take their values at execution time.
_subscribers_query = select(topic_sub_table.c.topic_name, topic_sub_table.c.sub_key)
_subscribers_query = _subscribers_query.where(
    any_of(topic_sub_table.c.topic_name, 'write_topic_names'))

# An unsubscription deletes the subscription row and only then the pending deliveries,
# so its delete must wait until each publication that read the row has committed its deliveries.
_subscribers_query_plain = PlainStatement(_subscribers_query.with_for_update(read=True, key_share=True))

# The row of a pair pending in the subscription list, which a publication inserts in its own commit,
# leaving a row that a concurrent transaction committed first as it is.
_topic_sub_insert = postgresql_insert(topic_sub_table).on_conflict_do_nothing()
_topic_sub_insert_plain = PlainStatement(_topic_sub_insert)

# A message whose identifier exists already is not inserted, and the statement returns the messages it inserted ..
_message_insert = postgresql_insert(message_table).on_conflict_do_nothing(index_elements=[message_table.c.msg_id])
_message_insert = _message_insert.returning(message_table.c.id, message_table.c.msg_id)
_message_insert_plain = PlainStatement(_message_insert)

# .. and what a message that exists already was published with tells a repeated publication from a different message.
_existing_messages_query = select(message_table.c.msg_id, message_table.c.topic_name, message_table.c.payload_crc32)
_existing_messages_query = _existing_messages_query.where(
    any_of(message_table.c.msg_id, 'write_msg_ids'))
_existing_messages_query_plain = PlainStatement(_existing_messages_query)

_delivery_insert = PlainStatement(delivery_table.insert())

# ################################################################################################################################
# ################################################################################################################################

class PublicationInserts:
    """ The inserts of the messages of publications and of their delivery rows, in the transaction of a group commit.
    """

    # The subscriber and topic pairs of the configuration database, which decide the subscribers of each topic
    subscription_list: 'SubscriptionList'

    # The waiting pulls and the idle push greenlets that the publications of a commit claim
    fast_path: 'FastPath'

    def _get_subscribers(
        self,
        connection:'Connection',
        publications:'pending_publication_list',
        added_pairs:'pairlist',
        ) -> 'anydict':
        """ Returns the subscriber keys of each topic the publications go to, decided by the subscription list
        from the rows read and locked within the caller's transaction, and inserts the rows of the pending pairs.
        """
        topic_names:'anylist' = []

        for pending in publications:
            topic_name = pending.message_values['topic_name']

            if topic_name not in topic_names:
                topic_names.append(topic_name)

        row_sub_keys:'anydict' = {}

        for topic_name in topic_names:
            row_sub_keys[topic_name] = []

        # The rows of the topics are locked first ..
        for row in _subscribers_query_plain.execute(connection, {'write_topic_names': topic_names}):
            row_sub_keys[row.topic_name].append(row.sub_key)

        # .. the subscription list decides the subscribers of each topic only under that lock ..
        out:'anydict' = {}
        topic_sub_rows:'anylist' = []

        for topic_name in topic_names:
            sub_keys, added = self.subscription_list.decide_subscribers(topic_name, row_sub_keys[topic_name])

            if sub_keys:
                out[topic_name] = sub_keys

            for sub_key, added_topic_name in added:
                topic_sub_rows.append({'sub_key': sub_key, 'topic_name': added_topic_name})

            added_pairs.extend(added)

        # .. and the pending pairs receive their rows in the same commit as the messages.
        if topic_sub_rows:
            _ = _topic_sub_insert_plain.insert_rows(connection, topic_sub_rows)

        return out

# ################################################################################################################################

    def _resolve_duplicates(self, connection:'Connection', duplicates:'pending_publication_list') -> 'None':
        """ Decides about each publication whose message identifier exists already. A message with the same topic
        and payload is a publication repeated after its outcome was unknown to its publisher, which receives
        the original result again, and any other message fails its own publisher alone.
        """
        msg_ids:'strlist' = []

        for pending in duplicates:
            msg_ids.append(pending.message_values['msg_id'])

        existing:'anydict' = {}

        for chunk in get_chunks(msg_ids):
            for row in _existing_messages_query_plain.execute(connection, {'write_msg_ids': chunk}):
                existing[row.msg_id] = row

        for pending in duplicates:

            message_values = pending.message_values
            msg_id = message_values['msg_id']
            row = existing.get(msg_id)

            # The cleanup removed the existing message after the insert met it, which happens only to a message
            # that was published and fully processed, so this one is its repetition.
            if row is None:
                logger.info('Repeated publication of a removed message -> msg_id:%s', msg_id)
                pending.is_repeat = True
                continue

            is_same_topic = row.topic_name == message_values['topic_name']
            is_same_payload = row.payload_crc32 == message_values['payload_crc32']

            if is_same_topic and is_same_payload:
                logger.info('Repeated publication of an existing message -> msg_id:%s', msg_id)
                pending.is_repeat = True
            else:
                message = f'Message ID `{msg_id}` belongs to a different message that exists already'
                pending.exception = PubSubDuplicateMsgID(message)

# ################################################################################################################################

    def _insert_deliveries(self, connection:'Connection', delivery_rows:'anylist') -> 'None':
        """ Inserts delivery rows with multi-row inserts or, when there are many of them, with COPY.
        """
        delivery_row_count = len(delivery_rows)

        if delivery_row_count >= _copy_min_delivery_rows:
            copy_rows(connection, delivery_table, delivery_rows)
        else:
            _ = _delivery_insert.insert_rows(connection, delivery_rows)

# ################################################################################################################################

    def _insert_publications(
        self,
        connection:'Connection',
        publications:'pending_publication_list',
        added_pairs:'pairlist',
        claims:'FastPathClaims | None',
        ) -> 'None':
        """ Writes the dedup records of the publications, then inserts the messages of those whose dedup records
        were written and one delivery row per message and subscriber. With claims given, the delivery rows of the
        subscribers whose pulls or push greenlets wait for messages are handed out by the fast path. The publications
        of a fenced acknowledgement, which a savepoint may undo, are given no claims.
        """

        # A publication whose dedup record remains from an earlier one inserts nothing ..
        publications = write_dedup_records(connection, publications)

        if not publications:
            return

        # .. the subscribers as of this very commit ..
        subscribers = self._get_subscribers(connection, publications, added_pairs)

        message_rows:'anylist' = []

        # The payloads of the messages that have subscribers, by their digests, with their search texts ..
        payloads:'strstrdict' = {}
        search_texts:'strstrdict' = {}
        with_payloads:'pending_publication_list' = []

        for pending in publications:

            message_values = pending.message_values
            topic_name = message_values['topic_name']

            # .. a topic without subscribers has its messages stored without their payloads,
            # and an empty payload, which has no digest, is not stored at all ..
            if topic_name in subscribers:
                pending.subscriber_keys = subscribers[topic_name]
                if pending.payload_digest is not None:
                    payloads[pending.payload_digest] = pending.payload
                    search_texts[pending.payload_digest] = pending.search_text
                    with_payloads.append(pending)
            else:
                pending.subscriber_keys = []
                message_values['payload_id'] = None
                message_values['payload_dropped'] = True
                message_values['payload_encrypted'] = False
                message_values['payload_base64'] = False

            message_rows.append(message_values)

        # .. the payloads are stored once each, in the payload table that the audit events reference as well,
        # and each message references the row of its payload ..
        if payloads:
            payload_ids = store_payloads(connection, payloads, search_texts)

            for pending in with_payloads:
                pending.message_values['payload_id'] = payload_ids[pending.payload_digest]

        # .. all the messages go in one statement, which returns the primary keys of those it inserted ..
        inserted:'anydict' = {}

        for row in _message_insert_plain.insert_rows(connection, message_rows):
            inserted[row.msg_id] = row.id

        # .. a message that was not inserted has an identifier that exists already ..
        delivery_rows:'anylist' = []
        duplicates:'pending_publication_list' = []

        # .. each publication that inserted its message, by the ID of the message ..
        published:'anydict' = {}

        for pending in publications:

            message_values = pending.message_values
            msg_id = message_values['msg_id']

            # .. only the first publication of an identifier within a commit can have inserted it ..
            if msg_id not in inserted:
                pending.subscriber_keys = []
                duplicates.append(pending)
                continue

            message_id = inserted.pop(msg_id)
            published[message_id] = pending

            for sub_key in pending.subscriber_keys:
                delivery_rows.append({
                    'message_id': message_id,
                    'sub_key': sub_key,
                    'topic_name': message_values['topic_name'],
                    'priority': message_values['priority'],
                    'expiration_ms': message_values['expiration_ms'],
                })

        # .. a message that met a stored one under the same ID gives its dedup record the fingerprint of the stored one ..
        if duplicates:
            self._resolve_duplicates(connection, duplicates)
            rewrite_fingerprints(connection, duplicates)

        # .. the subscribers that wait for messages are handed theirs ..
        if claims:
            delivery_rows = self.fast_path.claim(claims, connection, published, delivery_rows)

        # .. and all the other delivery rows go in one statement too.
        if delivery_rows:
            self._insert_deliveries(connection, delivery_rows)

# ################################################################################################################################
# ################################################################################################################################
