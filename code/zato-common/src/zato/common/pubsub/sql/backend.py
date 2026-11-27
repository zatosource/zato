# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from logging import getLogger
from typing import NamedTuple

# SQLAlchemy
from sqlalchemy import and_, select

# Zato
from zato.common.api import PubSub
from zato.common.audit_log.api import is_audit_log_enabled
from zato.common.db_env.engine import call_database, execute_write
from zato.common.pubsub.delivery_scope import get_delivery_scope
from zato.common.pubsub.sql.admin import SQLAdminAPI
from zato.common.pubsub.sql.config import get_batch_size, get_pull_lease_seconds
from zato.common.pubsub.sql.publication import add_published_event, build_publication, check_scope_publication, \
    complete_publication, complete_publications
from zato.common.pubsub.sql.pull import delivered_topics_parameters, fetch_statement, has_lease_candidates, \
    outgoing_fetch_statement, payload_statement
from zato.common.pubsub.sql.schema import delivery_table, topic_sub_table
from zato.common.pubsub.sql.pending import new_fenced_ack, new_pending_atomic, new_pending_lease
from zato.common.pubsub.sql.subscription_sync import read_governed_pairs
from zato.common.typing_ import list_, tuple_
from zato.server.metrics import zato_pubsub_messages_delivered_total

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.pubsub.sql.pending import PendingAck, PendingLease, pending_publication_list
    from zato.common.pubsub.sql.publication import built_publication_list
    from zato.common.pubsub.subscription_list import pairlist
    from zato.common.typing_ import any_, anydict, anylist, anylistnone, intlist, intnone, strdict, strlist, strnone

    pairlist = pairlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_default_priority     = PubSub.Message.Priority_Default
_default_expiration   = PubSub.Message.Default_Expiration
_default_max_messages = PubSub.Message.Default_Max_Messages
_default_max_len      = PubSub.Message.Default_Max_Len

# One second expressed in milliseconds.
_milliseconds_per_second = 1000

# ################################################################################################################################
# ################################################################################################################################

_outgoing_sub_key_prefix = PubSub.Outgoing.Sub_Key_Prefix

# The message ID and the delivery attempt of each message that a pull client consumed
consumed_list = list_[tuple_[str, int]]

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PublishResult:
    msg_id: 'str'

# ################################################################################################################################

class AckPulledResult(NamedTuple):
    """ How many delivery rows an acknowledgement of a pull client removed and the message ID of each of its publications.
    """
    removed_count: 'int'
    published: 'strlist'

# ################################################################################################################################
# ################################################################################################################################

class SQLPubSubBackend(SQLAdminAPI):
    """ SQL-based pub/sub backend - messages, queues and delivery state are stored
    in the Zato database that the Zato_Database_* variables select.
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
        msg_id:'strnone'=None,
        max_retries:'intnone'=None,
        retry_sleep_time:'intnone'=None,
        retry_backoff_threshold:'intnone'=None,
        retry_backoff_multiplier:'intnone'=None,
        audit_events:'anylistnone'=None,
    ) -> 'PublishResult':
        """ Publish a message to a topic. A caller that needs to know the message's id before the message is
        stored, e.g. because the id travels inside the message itself, gives its own, otherwise one is generated.
        The retry settings, when given, travel with the message and the push delivery retries it as they say.
        The audit events, when given, commit with the message in addition to the one that records the publication.
        A subscriber service that publishes while it processes a push delivery batch receives the id of a message
        that is stored if and only if the batch commits. A batch that does not commit is delivered again.
        """
        topic_name = topic_name.lower()

        # A topic of the configuration database that is inactive is refused here, before any message is built
        if topic_name in self.inactive_topics:
            raise Exception(f'Topic `{topic_name}` is inactive')

        built = build_publication(
            self,
            topic_name,
            data,
            priority=priority,
            expiration=expiration,
            correl_id=correl_id,
            in_reply_to=in_reply_to,
            ext_client_id=ext_client_id,
            publisher=publisher,
            pub_time=pub_time,
            cid=cid,
            msg_id=msg_id,
            max_retries=max_retries,
            retry_sleep_time=retry_sleep_time,
            retry_backoff_threshold=retry_backoff_threshold,
            retry_backoff_multiplier=retry_backoff_multiplier,
        )

        pending = built.pending

        # The audit events commit with the message ..
        add_published_event(self, built)

        if audit_events:
            pending.audit_events.extend(audit_events)

        # .. the publications of a subscriber service that processes a push delivery batch commit
        # in the transaction that acknowledges the batch, which also runs what follows their commit,
        # and a message ID of the caller that stands for a different message is refused at once ..
        if scope := get_delivery_scope():
            if msg_id:
                check_scope_publication(self, scope.publications, pending)
            scope.publications.append(pending)

        # .. whereas any other message is inserted with one delivery row per subscriber in one transaction,
        # possibly shared with other callers, a topic without subscribers has its message stored without its payload,
        # and what follows the commit runs once it is committed.
        else:
            self._writer.publish(pending)
            complete_publication(self, built)

        out = PublishResult()
        out.msg_id = pending.message_values['msg_id']

        return out

# ################################################################################################################################

    def ack_with_publications(
        self,
        sub_key:'str',
        msg_ids:'strlist',
        publications:'anylist',
        audit_events:'anylist',
        ) -> 'None':
        """ Acknowledges the messages of a push delivery batch in one transaction with the publications that its
        subscriber services made, which commits all of them or none, and then runs what follows the commit
        of each publication. A batch whose delivery rows another delivery of the same messages already removed
        commits nothing, and if it would store a new message, it raises PubSubAckConflict. A publication whose
        message ID stands for a different message makes the batch commit nothing and raise PubSubDuplicateMsgID.
        The audit events of the deliveries of the batch commit in the same transaction, also when the acknowledgement
        fails its checks.
        """
        ack = new_fenced_ack(sub_key, msg_ids, None)
        atomic = new_pending_atomic(publications, ack, True)
        atomic.audit_events = audit_events

        self._writer.ack_atomic(atomic)
        self._log_concluded(ack)

        # A publication that only repeated an existing message was completed when that message was committed.
        completed:'pending_publication_list' = []

        for pending in publications:
            if not pending.is_repeat:
                completed.append(pending)

        complete_publications(self, completed)

        logger.info('ack_with_publications -> sub_key:%s, acked:%d, fully_delivered:%d, publications:%d',
            sub_key, len(msg_ids), ack.fully_delivered_count, len(publications))

# ################################################################################################################################

    def ack_delivered(self, sub_key:'str', msg_id:'str', delivery_attempt:'int') -> 'int':
        """ Acknowledges one pushed message of an outgoing connection's queue under the fence, with the delivery attempt
        that this server recorded for it. A message that another server has handed out again since
        raises PubSubAckConflict and stays in the queue. A message concluded already is removed by nothing.
        Returns how many messages became fully delivered.
        """
        expected_attempts = [delivery_attempt]

        ack = new_fenced_ack(sub_key, [msg_id], expected_attempts)
        atomic = new_pending_atomic([], ack, False)

        self._writer.ack_atomic(atomic)
        self._log_concluded(ack)

        out = ack.fully_delivered_count

        logger.info('ack_delivered -> sub_key:%s, msg_id:%s, attempt:%d, removed:%d, fully_delivered:%d',
            sub_key, msg_id, delivery_attempt, ack.removed_count, out)

        return out

# ################################################################################################################################

    def _log_concluded(self, ack:'PendingAck') -> 'None':
        """ Logs the messages of a committed fenced acknowledgement that an earlier delivery concluded.
        """
        if ack.concluded_msg_ids:
            logger.info('Fenced acknowledgement of concluded messages -> sub_key:%s, msg_ids:%s',
                ack.sub_key, ack.concluded_msg_ids)

# ################################################################################################################################

    def ack_pulled_with_publications(
        self,
        sub_key:'str',
        consumed:'consumed_list',
        publications:'built_publication_list',
        ) -> 'AckPulledResult':
        """ Acknowledges the messages that a pull client consumed, each with the delivery attempt that it was handed out with,
        in one transaction with the publications that the client produced from them. A message that another pull has
        handed out again or concluded since, and a publication whose message ID stands for a different message,
        roll the transaction back and raise. Returns how many delivery rows were removed and the message ID
        of each publication.
        """
        msg_ids:'strlist' = []
        expected_attempts:'intlist' = []

        for msg_id, delivery_attempt in consumed:
            msg_ids.append(msg_id)
            expected_attempts.append(delivery_attempt)

        ack = new_fenced_ack(sub_key, msg_ids, expected_attempts)

        pending_publications:'anylist' = []

        # Each publication commits with the audit event that records it
        for built in publications:
            add_published_event(self, built)
            pending_publications.append(built.pending)

        atomic = new_pending_atomic(pending_publications, ack, True)
        self._writer.ack_atomic(atomic)
        self._log_concluded(ack)

        # A publication that only repeated an existing message was completed when that message was committed.
        published:'strlist' = []
        completed:'pending_publication_list' = []

        for built in publications:

            if not built.pending.is_repeat:
                completed.append(built.pending)

            msg_id = built.pending.message_values['msg_id']
            published.append(msg_id)

        complete_publications(self, completed)

        logger.info('ack_pulled_with_publications -> sub_key:%s, consumed:%d, removed:%d, publications:%d',
            sub_key, len(consumed), ack.removed_count, len(publications))

        out = AckPulledResult(ack.removed_count, published)
        return out

# ################################################################################################################################

    def sync_subscription_pairs(self, added:'pairlist', removed:'pairlist') -> 'None':
        """ Inserts and deletes the governed pairs of the subscription list in one transaction of the commit queue.
        """
        self._writer.sync_pairs(added, removed)

# ################################################################################################################################

    def get_governed_pairs(self) -> 'pairlist':
        """ Returns the governed subscriber and topic pairs whose rows are committed in the pub/sub database.
        """
        with self.engine.connect() as connection:
            out = read_governed_pairs(connection)

        return out

# ################################################################################################################################

    def cleanup_pair_deliveries(self, removed:'pairlist') -> 'None':
        """ Removes the delivery rows of pairs whose subscription rows were deleted, a bounded batch at a time.
        """
        for sub_key, topic_name in removed:
            self._cleanup_pair_deliveries(sub_key, topic_name)

# ################################################################################################################################

    def _cleanup_pair_deliveries(self, sub_key:'str', topic_name:'str') -> 'None':
        """ Removes the pending deliveries of one pair that no longer has a subscription row.
        """
        batch_size = get_batch_size()
        cleaned_up_count = 0

        while True:

            batch_count = call_database(self.engine, self._unsubscribe_batch, self.engine, sub_key, topic_name, batch_size)

            if not batch_count:
                break

            cleaned_up_count += batch_count
            self._yield_after_write()

        if cleaned_up_count:
            logger.info('Cleaned up deliveries of a removed pair -> sub_key:%s, topic_name:%s, cleaned_up_count:%d',
                sub_key, topic_name, cleaned_up_count)

# ################################################################################################################################

    def subscribe(self, sub_key:'str', topic_name:'str') -> 'None':
        """ Subscribe a user to a topic. Only messages published from this point on
        are delivered to the subscriber. Mechanism-owned subscriptions alone use this path.
        """

        # Normalize topic name to lowercase for case-insensitivity ..
        topic_name = topic_name.lower()

        # .. and record the subscription unless it exists.
        if call_database(self.engine, self._subscribe, self.engine, sub_key, topic_name):
            logger.info('Subscribed -> sub_key:%s, topic_name:%s', sub_key, topic_name)

# ################################################################################################################################

    def _subscribe(self, engine:'Engine', sub_key:'str', topic_name:'str') -> 'bool':
        """ Records a subscription in a transaction of its own and returns whether it did not exist before.
        """
        with engine.begin() as connection:

            # Subscribing twice is a no-op ..
            query = select(topic_sub_table.c.sub_key)
            query = query.where(and_(
                topic_sub_table.c.sub_key == sub_key,
                topic_sub_table.c.topic_name == topic_name,
            ))
            row = connection.execute(query).fetchone()

            if row:
                return False

            # .. record the subscription.
            insert_statement = topic_sub_table.insert().values(sub_key=sub_key, topic_name=topic_name)
            _ = connection.execute(insert_statement)

        return True

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

        _ = execute_write(self.engine, delete_statement)

        # .. then clean up the pending deliveries in bounded batches, each committed in a transaction of its own.
        batch_size = get_batch_size()
        cleaned_up_count = 0

        while True:

            batch_count = call_database(self.engine, self._unsubscribe_batch, self.engine, sub_key, topic_name, batch_size)

            # An empty batch means nothing is pending for the pair anymore ..
            if not batch_count:
                break

            cleaned_up_count += batch_count

            # .. let the other greenlets run between the batches.
            self._yield_after_write()

        logger.info('Unsubscribed -> sub_key:%s, topic_name:%s, cleaned_up_count:%d',
            sub_key, topic_name, cleaned_up_count)

# ################################################################################################################################

    def _unsubscribe_batch(self, engine:'Engine', sub_key:'str', topic_name:'str', batch_size:'int') -> 'int':
        """ Deletes one bounded batch of the pending deliveries of a subscription that was removed,
        in a transaction of its own, and returns how many it deleted.
        """
        with engine.begin() as connection:

            query = select(delivery_table.c.id, delivery_table.c.message_id)
            query = query.where(and_(
                delivery_table.c.sub_key == sub_key,
                delivery_table.c.topic_name == topic_name,
            ))
            query = query.limit(batch_size)

            rows = connection.execute(query).fetchall()

            if not rows:
                return 0

            delivery_ids:'intlist' = []
            message_ids:'intlist' = []

            for row in rows:
                delivery_ids.append(row.id)
                message_ids.append(row.message_id)

            batch_delete = delivery_table.delete()
            batch_delete = batch_delete.where(delivery_table.c.id.in_(delivery_ids))
            _ = connection.execute(batch_delete)

            _ = self._drop_fully_delivered_payloads(connection, message_ids)

        out = len(rows)
        return out

# ################################################################################################################################

    def read_payload(self, message:'anydict') -> 'str':
        """ Reads the payload of one fetched message from the database, which is the payload of its most recent edit.
        """
        parameters = {'payload_message_ids': [message['sequence_id']]}

        with self.engine.connect() as connection:
            row = payload_statement.execute(connection, parameters).one()

        out = self._load_payload_from_row(row)
        return out

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

        payload_cache = self.payload_cache

        # A payload is kept only if no edit took place from this point to the moment it is kept
        read_epoch = payload_cache.get_epoch()

        payloads:'strdict' = {}
        missing:'anydict' = {}

        with self.engine.connect() as connection:
            rows:'anylist' = []
            rows.extend(statement.execute(connection, parameters))

            # The payloads kept already are used as they are ..
            for row in rows:
                payload = payload_cache.get(row.msg_id)
                if payload is None:
                    missing[row.id] = row
                else:
                    payloads[row.msg_id] = payload

            # .. and the others are read in one more query.
            if missing:
                payload_parameters = {'payload_message_ids': list(missing)}
                payload_rows = payload_statement.execute(connection, payload_parameters).fetchall()
            else:
                payload_rows = []

        for payload_row in payload_rows:
            row = missing[payload_row.id]
            payload = self._load_payload_from_row(payload_row)
            payloads[row.msg_id] = payload

            # A payload that was dropped already is not kept.
            if payload_row.payload is not None:
                payload_cache.put(row.msg_id, payload, row.data_size, read_epoch)

        # A message that left the database between the two queries has no payload, the same as a dropped one.
        for row in missing.values():
            if row.msg_id not in payloads:
                payloads[row.msg_id] = ''

        return rows, payloads

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

    def pull_messages(
        self,
        sub_key:'str',
        max_messages:'int'=_default_max_messages,
        max_len:'int'=_default_max_len,
    ) -> 'anylist':
        """ Hands a subscriber's deliverable messages over to one pulling client, leasing them in the same transaction,
        so that concurrent pulls never receive the same message. The messages stay in the queue until the subscriber
        acknowledges them, and a pull after their lease runs out hands them out again.
        """
        now_ms = self._database_now_ms()
        out:'anylist' = []

        # A pull that would hand out nothing does not wait for a commit ..
        if not has_lease_candidates(self.engine, self.subscription_list, sub_key, now_ms):
            return out

        # .. while any other one leases its messages in a commit that it may share with other writes.
        leased_until_ms = now_ms + get_pull_lease_seconds() * 1000

        lease = new_pending_lease(sub_key, max_messages, max_len, now_ms, leased_until_ms, self._on_leased)
        self._writer.lease(lease)

        out = lease.messages
        return out

# ################################################################################################################################

    def _on_leased(self, lease:'PendingLease') -> 'None':
        """ Builds the messages of the rows that a pull leased and the audit events of their reception,
        in the transaction that leases them, so that a reception is recorded if and only if its lease is committed.
        """
        # The receptions are recorded only while the audit log is on ..
        if is_audit_log_enabled():
            audit_log = self.audit_log
        else:
            audit_log = None

        # .. and each leased row becomes its message and the audit event of its reception.
        self._pulled_messages.build(lease, audit_log, self.crypto_manager)

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
        """ Formats messages that a pull leased into the {data, meta} structure expected by the REST API
        and increments the delivery counters. The lease recorded the reception of each of them.
        """
        clock = self.clock
        now = clock.now()

        out:'anylist' = []

        for message in messages:

            # The payload stays the text that the database stored, the encoder of the response places it in the response as it stands ..
            data = message['data']
            data_size = len(data)

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
                'delivery_attempt': message['delivery_attempt'],
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

            # .. and update the delivery counter.
            counter = zato_pubsub_messages_delivered_total.labels(topic_name=message['topic_name'])
            _ = counter.inc()

        return out

# ################################################################################################################################
# ################################################################################################################################
