# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone
from logging import getLogger
from time import monotonic

# gevent
from gevent import sleep
from gevent.event import Event

# SQLAlchemy
from sqlalchemy import and_, bindparam, exists, select
from sqlalchemy.exc import DBAPIError

# Zato
from zato.common.db_env import Type_SQLite
from zato.common.pubsub.sql.config import get_pubsub_engine
from zato.common.pubsub.sql.schema import delivery_table, message_table, topic_sub_table
from zato.common.typing_ import cast_
from zato.common.util.time_ import datetime_to_ms, utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, Engine
    from zato.common.audit_log.api import AuditLog
    from zato.common.crypto.api import CryptoManager
    from zato.common.typing_ import any_, anydict, intlist, intlistnone, strlist, strset

    # Dummy assignments to satisfy type checkers
    AuditLog = AuditLog
    Connection = Connection
    CryptoManager = CryptoManager
    Engine = Engine

sub_event_dict = dict[str, Event]

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How many times a transaction rolled back as a deadlock victim is attempted in total,
# and how long the pause between the attempts is, in seconds.
_deadlock_attempt_count = 5
_deadlock_retry_sleep = 0.05

# How long back-to-back SQLite calls may hold the event loop before the backend
# yields it, in seconds - see _yield_after_write.
_yield_interval_seconds = 0.005

# The statements below run on every publish or delivery, so they are built once here,
# not per call - the bind parameters take their values at execution time.
_subscriber_keys_query = select(topic_sub_table.c.sub_key)
_subscriber_keys_query = _subscriber_keys_query.where(topic_sub_table.c.topic_name == bindparam('pub_topic_name'))

_message_id_query = select(message_table.c.id)
_message_id_query = _message_id_query.where(message_table.c.msg_id.in_(bindparam('lookup_msg_ids', expanding=True)))

_ack_delete_statement = delivery_table.delete()
_ack_delete_statement = _ack_delete_statement.where(and_(
    delivery_table.c.sub_key == bindparam('ack_sub_key'),
    delivery_table.c.message_id.in_(bindparam('ack_message_ids', expanding=True)),
))

# A message is still in flight while any delivery row references it -
# the update drops the payloads of the given messages that have none left.
_still_needed = exists()
_still_needed = _still_needed.where(delivery_table.c.message_id == message_table.c.id)

_drop_payloads_statement = message_table.update()
_drop_payloads_statement = _drop_payloads_statement.where(and_(
    message_table.c.id.in_(bindparam('drop_message_ids', expanding=True)),
    message_table.c.payload.isnot(None),
    ~_still_needed,
))
_drop_payloads_statement = _drop_payloads_statement.values(payload=None, payload_encrypted=False)

# ################################################################################################################################
# ################################################################################################################################

def _is_deadlock_error(error:'DBAPIError') -> 'bool':
    """ Tells whether the database rolled our transaction back as a deadlock victim -
    MySQL says 'Deadlock found', PostgreSQL says 'deadlock detected'.
    """
    error_text = str(error.orig).lower()
    out = 'deadlock' in error_text

    return out

# ################################################################################################################################
# ################################################################################################################################

class SQLBackendCore:
    """ The shared state and low-level operations of the SQL pub/sub backend -
    engine access, per-subscriber wake-up events, payload encryption at rest,
    row-to-message conversion and acknowledgements.
    """

    def __init__(
        self,
        *,
        audit_log:'AuditLog | None' = None,
        crypto_manager:'CryptoManager | None' = None,
        encrypt_at_rest:'bool' = False,
        ) -> 'None':

        # The audit log is injected by the server and is None in backend-only tests.
        self.audit_log = audit_log

        # Payloads are encrypted before insert and decrypted after select when configured.
        self.crypto_manager = crypto_manager
        self.encrypt_at_rest = encrypt_at_rest

        # Names of topics whose audit log was turned off explicitly - publications,
        # receptions and deliveries involving these topics write no audit events.
        self.audit_disabled_topics:'strset' = set()

        # One wake-up event per subscriber - publish sets them and blocking fetches wait on them.
        self._sub_events:'sub_event_dict' = {}

        # When _yield_after_write last let the event loop run.
        self._last_yield = monotonic()

        # Which engine _needs_write_yield was computed for and what it said -
        # the engine only changes when the environment repoints the backend.
        self._yield_engine:'Engine | None' = None
        self._needs_write_yield = False

# ################################################################################################################################

    @property
    def engine(self) -> 'Engine':
        """ The engine behind the current Zato_PubSub_DB_* configuration, resolved on each access.
        """
        out = get_pubsub_engine()
        return out

# ################################################################################################################################

    def close(self) -> 'None':
        """ Releases all pooled database connections, e.g. on server shutdown.
        """
        engine = self.engine
        engine.dispose()

# ################################################################################################################################

    def set_topic_audit_flag(self, topic_name:'str', is_audit_log_active:'bool') -> 'None':
        """ Registers whether a topic's audit log is on or off.
        """
        if is_audit_log_active:
            self.audit_disabled_topics.discard(topic_name)
        else:
            self.audit_disabled_topics.add(topic_name)

# ################################################################################################################################

    def delete_topic_audit_flag(self, topic_name:'str') -> 'None':
        """ Forgets about a topic's audit log state, e.g. because the topic was deleted or renamed.
        """
        self.audit_disabled_topics.discard(topic_name)

# ################################################################################################################################

    def get_sub_event(self, sub_key:'str') -> 'Event':
        """ Returns the wake-up event of one subscriber, creating it on first use.
        """
        if event := self._sub_events.get(sub_key):
            out = event
        else:
            out = Event()
            self._sub_events[sub_key] = out

        return out

# ################################################################################################################################

    def notify_sub_keys(self, sub_keys:'strlist') -> 'None':
        """ Wakes up the blocking fetches of all the given subscribers.
        """
        for sub_key in sub_keys:
            event = self.get_sub_event(sub_key)
            event.set()

# ################################################################################################################################

    def _yield_after_write(self) -> 'None':
        """ Lets other greenlets run after a write transaction. Network databases
        yield to the event loop through their socket I/O with every statement,
        but SQLite runs its calls as blocking ones in the calling thread, so without
        an explicit yield a greenlet writing in a tight loop would starve every
        other greenlet in the process. The yield is time-based - one per interval,
        not one per call - so the loop can never be held longer than the interval
        while callers writing in bursts keep their throughput.
        """
        engine = self.engine

        # Only SQLite needs the yield - recheck only when the engine changed.
        if engine is not self._yield_engine:
            self._yield_engine = engine
            self._needs_write_yield = engine.dialect.name == Type_SQLite

        if not self._needs_write_yield:
            return

        now = monotonic()

        if now - self._last_yield >= _yield_interval_seconds:
            self._last_yield = now
            sleep(0)

# ################################################################################################################################

    def _encrypt_payload(self, data:'str') -> 'str':
        """ Encrypts a payload before it is written to the database.
        """
        crypto_manager = cast_('CryptoManager', self.crypto_manager)
        out = cast_('str', crypto_manager.encrypt(data, needs_str=True))

        return out

# ################################################################################################################################

    def _decrypt_payload(self, payload:'str') -> 'str':
        """ Decrypts a payload read from the database.
        """
        crypto_manager = cast_('CryptoManager', self.crypto_manager)
        out = cast_('str', crypto_manager.decrypt(payload))

        return out

# ################################################################################################################################

    def _load_payload_from_row(self, row:'any_') -> 'str':
        """ Returns the payload of one message row, decrypted if it was encrypted at rest.
        A missing payload reads as ''.
        """
        payload = row.payload

        if payload is None:
            out = ''
        elif row.payload_encrypted:
            out = self._decrypt_payload(payload)
        else:
            out = payload

        return out

# ################################################################################################################################

    def _build_message_from_row(self, row:'any_') -> 'anydict':
        """ Converts one fetched row into the message dict the delivery and REST layers consume.
        """
        data = self._load_payload_from_row(row)

        # The always-present fields come first ..
        out:'anydict' = {
            'msg_id': row.msg_id,
            'sequence_id': row.id,
            'topic_name': row.topic_name,
            'data': data,
            'data_class': row.data_class if row.data_class else '',
            'data_size': row.data_size,
            'data_preview': row.data_preview if row.data_preview else '',
            'priority': row.priority,
            'expiration': row.expiration,
            'pub_time_iso': row.pub_time_iso,
            'recv_time_iso': row.recv_time_iso,
            'expiration_time_iso': row.expiration_time_iso,
        }

        # .. and the optional ones are included only when they were given at publish time.
        if row.publisher:
            out['publisher'] = row.publisher

        if row.cid:
            out['cid'] = row.cid

        if row.correl_id:
            out['correl_id'] = row.correl_id

        if row.in_reply_to:
            out['in_reply_to'] = row.in_reply_to

        if row.ext_client_id:
            out['ext_client_id'] = row.ext_client_id

        return out

# ################################################################################################################################

    def _get_subscriber_keys(self, connection:'Connection', topic_name:'str') -> 'strlist':
        """ Returns all the subscriber keys of one topic, read within the caller's transaction.
        """
        out:'strlist' = []

        for row in connection.execute(_subscriber_keys_query, {'pub_topic_name': topic_name}):
            out.append(row.sub_key)

        return out

# ################################################################################################################################

    def _get_message_ids(self, connection:'Connection', msg_ids:'strlist') -> 'intlist':
        """ Maps public message identifiers to their primary keys, read within the caller's transaction.
        """
        out:'intlist' = []

        for row in connection.execute(_message_id_query, {'lookup_msg_ids': msg_ids}):
            out.append(row.id)

        return out

# ################################################################################################################################

    def _drop_fully_delivered_payloads(self, connection:'Connection', message_ids:'intlist') -> 'int':
        """ Sets the payload to NULL for each of the given messages that no subscriber needs anymore.
        Returns how many payloads were dropped.
        """
        result = connection.execute(_drop_payloads_statement, {'drop_message_ids': message_ids})

        out = result.rowcount
        return out

# ################################################################################################################################

    def ack_messages(self, sub_key:'str', msg_ids:'strlist', sequence_ids:'intlistnone'=None) -> 'int':
        """ Acknowledges many messages for one subscriber in a single transaction.
        Callers that only hold public identifiers pass msg_ids alone.
        Returns how many of them became fully delivered.
        """
        if not msg_ids:
            return 0

        # The database may roll the transaction back as a deadlock victim -
        # it is idempotent and is simply run again.
        for attempt in range(_deadlock_attempt_count):
            try:
                out = self._ack_messages_once(sub_key, msg_ids, sequence_ids)
                break
            except DBAPIError as e:
                # Anything other than a deadlock rollback is a real error.
                if not _is_deadlock_error(e):
                    raise

                logger.info('ack_messages deadlock victim, attempt %d -> sub_key:%s', attempt + 1, sub_key)
                sleep(_deadlock_retry_sleep)
        else:
            raise Exception(f'ack_messages still a deadlock victim after {_deadlock_attempt_count} attempts -> sub_key:{sub_key}')

        # Let the other greenlets run now that the transaction is committed.
        self._yield_after_write()

        logger.info('ack_messages -> sub_key:%s, acked:%d, fully_delivered:%d', sub_key, len(msg_ids), out)

        return out

# ################################################################################################################################

    def _ack_messages_once(self, sub_key:'str', msg_ids:'strlist', sequence_ids:'intlistnone') -> 'int':
        """ One acknowledgement transaction - what ack_messages runs and,
        if the database picks it as a deadlock victim, runs again.
        """
        with self.engine.begin() as connection:

            # Map public identifiers to primary keys first - as a separate read,
            # not a subquery in the delete, whose shared InnoDB locks deadlock ..
            if sequence_ids is None:
                message_ids = self._get_message_ids(connection, msg_ids)
            else:
                message_ids = sequence_ids

            if not message_ids:
                return 0

            # .. remove this subscriber's delivery rows ..
            parameters = {
                'ack_sub_key': sub_key,
                'ack_message_ids': message_ids,
            }
            _ = connection.execute(_ack_delete_statement, parameters)

            # .. and drop the payloads of messages that no subscriber needs anymore.
            out = self._drop_fully_delivered_payloads(connection, message_ids)

        return out

# ################################################################################################################################

    def ack_message(self, sub_key:'str', msg_id:'str') -> 'bool':
        """ Acknowledges a single message after successful processing.
        Returns True if no subscribers remain and the payload was dropped.
        """
        fully_delivered_count = self.ack_messages(sub_key, [msg_id])

        out = fully_delivered_count > 0
        return out

# ################################################################################################################################

    @staticmethod
    def _compute_time_since(iso_timestamp:'str', now:'datetime') -> 'str':

        # Parse the ISO timestamp into a datetime ..
        normalized_iso = iso_timestamp.replace('Z', '+00:00')
        timestamp = datetime.fromisoformat(normalized_iso)

        # .. strip tzinfo from both sides so subtraction always works ..
        if timestamp.tzinfo:
            timestamp_naive = timestamp.replace(tzinfo=None)
        else:
            timestamp_naive = timestamp

        if now.tzinfo:
            now_naive = now.replace(tzinfo=None)
        else:
            now_naive = now

        # .. compute the delta, clamping negative values to zero.
        delta = now_naive - timestamp_naive

        if delta.total_seconds() < 0:
            delta = timedelta(0)

        out = str(delta)
        return out

# ################################################################################################################################

    @staticmethod
    def _iso_to_ms(iso_timestamp:'str') -> 'int':
        """ Converts an ISO-8601 timestamp to milliseconds since the Unix epoch,
        treating timestamps without timezone information as UTC.
        """
        normalized_iso = iso_timestamp.replace('Z', '+00:00')
        timestamp = datetime.fromisoformat(normalized_iso)

        if not timestamp.tzinfo:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        milliseconds = datetime_to_ms(timestamp)

        out = int(milliseconds)
        return out

# ################################################################################################################################

    @staticmethod
    def _utc_now_ms() -> 'int':
        """ Returns the current UTC time in milliseconds since the Unix epoch.
        """
        now = utcnow()
        milliseconds = datetime_to_ms(now)

        out = int(milliseconds)
        return out

# ################################################################################################################################
# ################################################################################################################################
