# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from dataclasses import dataclass
from datetime import timedelta
from logging import getLogger

# SQLAlchemy
from sqlalchemy import and_, select

# Zato
from zato.common.api import PubSub
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource
from zato.common.marshal_.api import Model
from zato.common.pubsub.sql.admin import SQLAdminAPI
from zato.common.pubsub.sql.config import get_batch_size
from zato.common.pubsub.sql.schema import delivery_table, message_table, topic_sub_table
from zato.common.util.api import new_msg_id, utcnow
from zato.common.util.time_ import datetime_to_ms
from zato.server.metrics import zato_pubsub_messages_delivered_total, zato_pubsub_messages_published_total

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, intlist, strnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_default_priority     = PubSub.Message.Priority_Default
_default_expiration   = PubSub.Message.Default_Expiration
_default_max_messages = PubSub.Message.Default_Max_Messages
_default_max_len      = PubSub.Message.Default_Max_Len
_data_preview_len     = PubSub.Message.Data_Preview_Len

# One second expressed in milliseconds - blocking fetches receive their timeout in milliseconds
_milliseconds_per_second = 1000

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PublishResult:
    msg_id: 'str'

# ################################################################################################################################
# ################################################################################################################################

class SQLPubSubBackend(SQLAdminAPI):
    """ SQL-based pub/sub backend - messages, queues and delivery state live
    in their own relational database, SQLite by default and MySQL, PostgreSQL
    or Oracle DB when configured through the Zato_PubSub_DB_* environment variables.
    Payloads are stored in the database itself and dropped once every subscriber
    has acknowledged a message, leaving the row behind as the delivered-message trace.
    """

    def publish(
        self,
        topic_name:'str',
        data:'any_',
        *,
        priority:'int'=_default_priority,
        expiration:'int'=_default_expiration,
        correl_id:'strnone'=None,
        in_reply_to:'strnone'=None,
        ext_client_id:'strnone'=None,
        publisher:'strnone'=None,
        pub_time:'strnone'=None,
        cid:'strnone'=None,
    ) -> 'PublishResult':
        """ Publish a message to a topic.
        """

        # Normalize topic name to lowercase for case-insensitivity ..
        topic_name = topic_name.lower()

        # .. generate message ID ..
        message_id = new_msg_id()

        # .. build timestamps ..
        now = utcnow()
        now_iso = now.isoformat()

        if pub_time:
            pub_time_iso = pub_time
            pub_time_ms = self._iso_to_ms(pub_time)
        else:
            pub_time_iso = now_iso
            now_ms_float = datetime_to_ms(now)
            pub_time_ms = int(now_ms_float)

        expiration_delta = timedelta(seconds=expiration)
        expiration_time = now + expiration_delta
        expiration_time_iso = expiration_time.isoformat()
        expiration_ms_float = datetime_to_ms(expiration_time)
        expiration_ms = int(expiration_ms_float)

        # .. serialize data ..
        data_class = ''

        if isinstance(data, str):
            serialized_data = data

        elif isinstance(data, Model):
            data_module = data.__class__.__module__
            data_class_name = data.__class__.__qualname__
            data_class = f'{data_module}.{data_class_name}'
            serialized_data = data.to_json().decode()

        else:
            serialized_data = json.dumps(data)

        data_size = len(serialized_data)
        data_preview = serialized_data[:_data_preview_len]

        # .. encrypt the payload at rest when configured to ..
        if self.encrypt_at_rest:
            payload = self._encrypt_payload(serialized_data)
            payload_encrypted = True
        else:
            payload = serialized_data
            payload_encrypted = False

        # .. everything the message row carries, with optional values stored
        # .. as NULLs so Oracle DB's empty-string handling never matters ..
        message_values:'anydict' = {
            'msg_id': message_id,
            'topic_name': topic_name,
            'payload': payload,
            'payload_encrypted': payload_encrypted,
            'data_class': data_class if data_class else None,
            'data_size': data_size,
            'data_preview': data_preview if data_preview else None,
            'priority': priority,
            'expiration': expiration,
            'pub_time_iso': pub_time_iso,
            'recv_time_iso': now_iso,
            'expiration_time_iso': expiration_time_iso,
            'pub_time_ms': pub_time_ms,
            'expiration_ms': expiration_ms,
            'publisher': publisher,
            'cid': cid,
            'correl_id': correl_id,
            'in_reply_to': in_reply_to,
            'ext_client_id': ext_client_id,
        }

        # .. one transaction inserts the message and its delivery rows so a fetch
        # .. can never see a message with only some of its subscribers recorded ..
        with self.engine.begin() as connection:

            # .. the subscribers as of this very publication ..
            subscriber_keys = self._get_subscriber_keys(connection, topic_name)

            # .. with no subscribers the payload is dropped immediately - the row
            # .. goes straight into its delivered-message trace form ..
            if not subscriber_keys:
                message_values['payload'] = None
                message_values['payload_encrypted'] = False

            insert_statement = message_table.insert().values(**message_values)
            result = connection.execute(insert_statement)

            primary_key = result.inserted_primary_key
            message_row_id = primary_key[0]

            # .. one delivery row per subscriber, with priority and expiration
            # .. denormalized so the fetch query needs no join for them ..
            if subscriber_keys:

                delivery_rows:'anylist' = []

                for sub_key in subscriber_keys:
                    delivery_rows.append({
                        'message_id': message_row_id,
                        'sub_key': sub_key,
                        'topic_name': topic_name,
                        'priority': priority,
                        'expiration_ms': expiration_ms,
                    })

                _ = connection.execute(delivery_table.insert(), delivery_rows)

        # .. the transaction is committed, so the subscribers may wake up now ..
        if subscriber_keys:
            self.notify_sub_keys(subscriber_keys)

        subscriber_count = len(subscriber_keys)

        logger.info('Published message -> msg_id:%s, topic_name:%s, subscriber_count:%d',
            message_id, topic_name, subscriber_count)

        # .. record the publish in the audit log, unless the topic's audit log is off ..
        if self.audit_log:
            if topic_name not in self.audit_disabled_topics:

                # These are all optional on input so they are normalized to strings here.
                if cid is None:
                    cid = ''
                if correl_id is None:
                    correl_id = ''
                if ext_client_id is None:
                    ext_client_id = ''
                if publisher is None:
                    publisher = ''

                self.audit_log.insert(AuditSource.PubSub, AuditEvent.Published, topic_name,
                    cid=cid,
                    msg_id=message_id,
                    correl_id=correl_id,
                    ext_client_id=ext_client_id,
                    pub_time_iso=pub_time_iso,
                    endpoint=publisher,
                    size=data_size,
                    priority=priority,
                    outcome=AuditOutcome.OK,
                    data=serialized_data,
                )

        # .. update the publish counter and return the result.
        counter = zato_pubsub_messages_published_total.labels(topic_name=topic_name)
        _ = counter.inc()

        out = PublishResult()
        out.msg_id = message_id

        return out

# ################################################################################################################################

    def subscribe(self, sub_key:'str', topic_name:'str') -> 'None':
        """ Subscribe a user to a topic. Only messages published from this point on
        are delivered to the subscriber.
        """

        # Normalize topic name to lowercase for case-insensitivity ..
        topic_name = topic_name.lower()

        with self.engine.begin() as connection:

            # .. subscribing twice is a no-op ..
            query = select(topic_sub_table.c.sub_key)
            query = query.where(and_(
                topic_sub_table.c.sub_key == sub_key,
                topic_sub_table.c.topic_name == topic_name,
            ))
            row = connection.execute(query).fetchone()

            if row:
                return

            # .. record the subscription.
            insert_statement = topic_sub_table.insert().values(sub_key=sub_key, topic_name=topic_name)
            _ = connection.execute(insert_statement)

        logger.info('Subscribed -> sub_key:%s, topic_name:%s', sub_key, topic_name)

# ################################################################################################################################

    def unsubscribe(self, sub_key:'str', topic_name:'str') -> 'None':
        """ Unsubscribe a user from a topic, cleaning up everything still pending for the pair.
        """

        # Normalize topic name to lowercase for case-insensitivity ..
        topic_name = topic_name.lower()

        # .. remove the subscription first so no new publish adds deliveries for this pair ..
        delete_statement = topic_sub_table.delete()
        delete_statement = delete_statement.where(and_(
            topic_sub_table.c.sub_key == sub_key,
            topic_sub_table.c.topic_name == topic_name,
        ))

        with self.engine.begin() as connection:
            _ = connection.execute(delete_statement)

        # .. then clean up the pending deliveries in bounded batches,
        # .. dropping the payloads of messages no subscriber needs anymore.
        batch_size = get_batch_size()
        cleaned_up_count = 0

        while True:

            with self.engine.begin() as connection:

                query = select(delivery_table.c.id, delivery_table.c.message_id)
                query = query.where(and_(
                    delivery_table.c.sub_key == sub_key,
                    delivery_table.c.topic_name == topic_name,
                ))
                query = query.limit(batch_size)

                rows = connection.execute(query).fetchall()

                if not rows:
                    break

                delivery_ids:'intlist' = []
                message_ids:'intlist' = []

                for row in rows:
                    delivery_ids.append(row.id)
                    message_ids.append(row.message_id)

                batch_delete = delivery_table.delete()
                batch_delete = batch_delete.where(delivery_table.c.id.in_(delivery_ids))
                _ = connection.execute(batch_delete)

                _ = self._drop_fully_delivered_payloads(connection, message_ids)

                cleaned_up_count += len(rows)

        logger.info('Unsubscribed -> sub_key:%s, topic_name:%s, cleaned_up_count:%d',
            sub_key, topic_name, cleaned_up_count)

# ################################################################################################################################

    def _fetch_rows(self, sub_key:'str', max_messages:'int') -> 'anylist':
        """ Reads the subscriber's deliverable messages in (priority highest-first,
        publication order) sequence - one index-ordered query no matter the backlog depth.
        """
        now_ms = self._utc_now_ms()

        joined = delivery_table.join(message_table, message_table.c.id == delivery_table.c.message_id)

        query = select(message_table)
        query = query.select_from(joined)
        query = query.where(and_(
            delivery_table.c.sub_key == sub_key,
            delivery_table.c.expiration_ms > now_ms,
        ))
        query = query.order_by(delivery_table.c.priority.desc(), delivery_table.c.message_id.asc())
        query = query.limit(max_messages)

        with self.engine.connect() as connection:
            out = connection.execute(query).fetchall()

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

        # The event is cleared before the query so a publish landing between the query
        # and the wait leaves the event set and the wait returns immediately - without
        # this ordering such a message would sit unnoticed until the timeout ..
        event = self.get_sub_event(sub_key)
        event.clear()

        # .. read whatever is deliverable right now ..
        rows = self._fetch_rows(sub_key, max_messages)

        # .. nothing yet - optionally wait for a publish to wake us up and look again ..
        if not rows:
            if block_ms:
                wait_seconds = block_ms / _milliseconds_per_second
                _ = event.wait(wait_seconds)
                rows = self._fetch_rows(sub_key, max_messages)

        # .. convert the rows into message dicts, keeping within the total size budget.
        out:'anylist' = []
        total_len = 0

        for row in rows:

            data_len = row.data_size

            if total_len + data_len > max_len:
                break

            total_len += data_len

            message = self._build_message_from_row(row)
            out.append(message)

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

    def format_messages_for_rest(self, messages:'anylist', sub_key:'str') -> 'anylist':
        """ Format raw messages into the {data, meta} structure expected by the REST API.
        Also acknowledges each message and increments delivery counters.
        """
        now = utcnow()

        out:'anylist' = []

        for message in messages:

            data_raw = message['data']

            # Deserialize JSON data if possible ..
            try:
                data = json.loads(data_raw)
            except (json.JSONDecodeError, TypeError):
                data = data_raw

            data_size = len(data_raw)

            pub_time_iso = message['pub_time_iso']
            recv_time_iso = message['recv_time_iso']

            time_since_pub = self._compute_time_since(pub_time_iso, now)
            time_since_recv = self._compute_time_since(recv_time_iso, now)

            meta = {
                'topic_name': message['topic_name'],
                'size': data_size,
                'priority': message['priority'],
                'expiration': message['expiration'],
                'msg_id': message['msg_id'],
                'sub_key': sub_key,
                'pub_time_iso': pub_time_iso,
                'recv_time_iso': recv_time_iso,
                'expiration_time_iso': message['expiration_time_iso'],
                'time_since_pub': time_since_pub,
                'time_since_recv': time_since_recv,
            }

            if correl_id := message.get('correl_id'):
                meta['correl_id'] = correl_id

            if in_reply_to := message.get('in_reply_to'):
                meta['in_reply_to'] = in_reply_to

            if ext_client_id := message.get('ext_client_id'):
                meta['ext_client_id'] = ext_client_id

            out.append({
                'data': data,
                'meta': meta
            })

            # .. acknowledge the message now that it is being handed over ..
            _ = self.ack_message(sub_key, message['msg_id'])

            # .. record the pull-based reception in the audit log, using the CID stored
            # .. at publish time so the reception cross-references the publish,
            # .. unless the topic's audit log is off ..
            if self.audit_log:
                if message['topic_name'] not in self.audit_disabled_topics:

                    # Messages published before CIDs were carried inside them have no CID stored.
                    message_cid = message.get('cid')
                    if message_cid is None:
                        message_cid = ''

                    self.audit_log.insert(AuditSource.PubSub, AuditEvent.Received, message['topic_name'],
                        cid=message_cid,
                        msg_id=message['msg_id'],
                        pub_time_iso=pub_time_iso,
                        sub_key=sub_key,
                        size=data_size,
                        priority=message['priority'],
                        outcome=AuditOutcome.OK,
                        data=data_raw,
                    )

            # .. update the delivery counter.
            counter = zato_pubsub_messages_delivered_total.labels(topic_name=message['topic_name'])
            _ = counter.inc()

        return out

# ################################################################################################################################
# ################################################################################################################################
