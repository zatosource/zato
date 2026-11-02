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
from sqlalchemy import bindparam

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource
from zato.common.db_env.common import Type_PostgreSQL, Type_SQLite
from zato.common.pubsub.sql.clock import get_engine_clock
from zato.common.pubsub.sql.config import get_pubsub_db_type, get_pubsub_engine
from zato.common.pubsub.sql.generation import take_over
from zato.common.pubsub.sql.schema import delivery_table
from zato.common.pubsub.sql.writes import drop_payloads, new_pending_ack, PubSubWriter
from zato.common.typing_ import cast_
from zato.common.util.memory_trim import start_memory_trimmer
from zato.common.util.time_ import datetime_to_ms

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, Engine
    from zato.common.audit_log.api import AuditLog
    from zato.common.crypto.api import CryptoManager
    from zato.common.pubsub.sql.clock import DatabaseClock
    from zato.common.pubsub.sql.generation import GenerationGuard
    from zato.common.pubsub.sql.writes import PendingAck
    from zato.common.typing_ import any_, anydict, intlist, intlistnone, strlist, strset

    # Dummy assignments to satisfy type checkers
    AuditLog = AuditLog
    Connection = Connection
    CryptoManager = CryptoManager
    DatabaseClock = DatabaseClock
    Engine = Engine
    GenerationGuard = GenerationGuard

sub_event_dict = dict[str, Event]

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_retry = HTTP_SOAP.Retry

# How long back-to-back SQLite calls may hold the event loop before the backend
# yields it, in seconds - see _yield_after_write.
_yield_interval_seconds = 0.005

# The object of the audit event that records a takeover of the pub/sub database.
_takeover_object_name = 'pubsub-database'

# What records one push attempt of a delivery row and returns its number.
_record_attempt_statement = delivery_table.update()
_record_attempt_statement = _record_attempt_statement.where(delivery_table.c.id == bindparam('attempt_delivery_id'))
_record_attempt_statement = _record_attempt_statement.values(attempt=delivery_table.c.attempt + 1)
_record_attempt_statement = _record_attempt_statement.returning(delivery_table.c.attempt)

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

        # Names of topics whose message payloads leave with the audit export
        self.audit_payload_topics:'strset' = set()

        # One wake-up event per subscriber - publish sets them and blocking fetches wait on them.
        self._sub_events:'sub_event_dict' = {}

        # When _yield_after_write last let the event loop run.
        self._last_yield = monotonic()

        # Publications and acknowledgements of concurrent callers share their commits.
        self._writer = PubSubWriter()

        # The generation that this server raised on PostgreSQL, if it took over the database.
        self.generation_guard:'GenerationGuard | None' = None

        # The engine of the pub/sub database, resolved on first access.
        self._engine:'Engine | None' = None

        # The memory that a burst of publications and deliveries freed returns to the operating system.
        start_memory_trimmer()

# ################################################################################################################################

    @property
    def engine(self) -> 'Engine':
        """ The engine of the pub/sub database that the Zato_PubSub_DB_* variables select, resolved on first access.
        Every transaction of this backend runs on the one engine that its generation guard is installed on.
        """
        out = self._engine

        if out is None:
            out = get_pubsub_engine()
            self._engine = out

        return out

# ################################################################################################################################

    @property
    def clock(self) -> 'DatabaseClock':
        """ The clock of the pub/sub database of this backend.
        """
        engine = self.engine

        out = get_engine_clock(engine)
        return out

# ################################################################################################################################

    def take_over(self) -> 'None':
        """ Makes this server the active one on PostgreSQL, whose database a standby server may take over,
        and guards each subsequent transaction with the generation raised. A SQLite file has only one server.
        """
        if get_pubsub_db_type() == Type_PostgreSQL:
            generation_guard = take_over(get_pubsub_engine)
            self.generation_guard = generation_guard

            # Each generation is one higher than the one it replaces, which the audit log records with the takeover.
            if self.audit_log:
                generation = generation_guard.generation
                previous_generation = generation - 1

                attrs = {
                    'previous_generation': f'{previous_generation}',
                    'generation': f'{generation}',
                }

                self.audit_log.insert(AuditSource.PubSub, AuditEvent.Takeover, _takeover_object_name,
                    outcome=AuditOutcome.OK, attrs=attrs)

# ################################################################################################################################

    @property
    def is_replaced(self) -> 'bool':
        """ Whether another server has taken over the pub/sub database of this one.
        """
        if self.generation_guard is None:
            out = False
        else:
            out = self.generation_guard.is_replaced

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

    def set_topic_payload_flag(self, topic_name:'str', is_export_payload_active:'bool') -> 'None':
        """ Registers whether a topic's message payloads leave with the audit export.
        """
        if is_export_payload_active:
            self.audit_payload_topics.add(topic_name)
        else:
            self.audit_payload_topics.discard(topic_name)

# ################################################################################################################################

    def is_topic_payload_exported(self, topic_name:'str') -> 'bool':
        """ Whether a topic's message payloads leave with the audit export.
        """
        out = topic_name in self.audit_payload_topics
        return out

# ################################################################################################################################

    def delete_topic_audit_flag(self, topic_name:'str') -> 'None':
        """ Forgets about a topic's audit log state, e.g. because the topic was deleted or renamed.
        """
        self.audit_disabled_topics.discard(topic_name)
        self.audit_payload_topics.discard(topic_name)

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
        """ Lets other greenlets run after a write transaction. SQLite calls block
        the calling thread, so the backend yields once per interval.
        """
        now = monotonic()

        if now - self._last_yield >= _yield_interval_seconds:
            self._last_yield = now
            sleep(0)

# ################################################################################################################################

    def _yield_after_batch(self, batch_seconds:'float') -> 'None':
        """ Lets other greenlets run after one batch of an administrative operation. SQLite has a single writer,
        so on SQLite the pause lasts as long as the batch did and publications obtain at least half of the write time.
        """
        if self.engine.dialect.name == Type_SQLite:
            sleep(batch_seconds)
        else:
            self._yield_after_write()

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

        self._add_retry_settings(out, row)

        return out

# ################################################################################################################################

    def _add_retry_settings(self, out:'anydict', row:'any_') -> 'None':
        """ Adds to a message dict each retry setting its publisher gave, a setting left out being left out here too,
        so that the policy's defaults apply to it.
        """
        for name in _retry.FieldList:
            value = getattr(row, name)
            if value is not None:
                out[name] = value

# ################################################################################################################################

    def _drop_fully_delivered_payloads(self, connection:'Connection', message_ids:'intlist') -> 'int':
        """ Sets the payload to NULL for each of the given messages that no subscriber needs anymore.
        Returns how many payloads were dropped.
        """
        dropped = drop_payloads(connection, message_ids)

        out = len(dropped)
        return out

# ################################################################################################################################

    def ack_messages(self, sub_key:'str', msg_ids:'strlist', sequence_ids:'intlistnone'=None) -> 'int':
        """ Acknowledges many messages for one subscriber in a single transaction.
        Callers that only hold public identifiers pass msg_ids alone.
        Returns how many of them became fully delivered.
        """
        if not msg_ids:
            return 0

        pending = self._ack(sub_key, msg_ids, sequence_ids)
        out = pending.fully_delivered_count

        logger.info('ack_messages -> sub_key:%s, acked:%d, fully_delivered:%d', sub_key, len(msg_ids), out)

        return out

# ################################################################################################################################

    def ack_pulled(self, sub_key:'str', msg_ids:'strlist') -> 'int':
        """ Acknowledges messages that a pull handed out to one subscriber, removing them from its queue.
        Returns how many of them were still in the queue.
        """
        if not msg_ids:
            return 0

        pending = self._ack(sub_key, msg_ids, None)
        out = pending.removed_count

        logger.info('ack_pulled -> sub_key:%s, given:%d, removed:%d', sub_key, len(msg_ids), out)

        return out

# ################################################################################################################################

    def claim_message(self, sub_key:'str', msg_id:'str') -> 'bool':
        """ Acknowledges a single message on behalf of one of several callers that may act on it.
        Returns True only to the caller whose acknowledgement removed the subscriber's delivery row.
        """
        pending = self._ack(sub_key, [msg_id], None)
        out = pending.removed_count > 0

        logger.info('claim_message -> sub_key:%s, msg_id:%s, claimed:%s', sub_key, msg_id, out)

        return out

# ################################################################################################################################

    def _ack(self, sub_key:'str', msg_ids:'strlist', sequence_ids:'intlistnone') -> 'PendingAck':
        """ Writes one acknowledgement, in a commit of its own or shared with the other writes in progress.
        """
        out = new_pending_ack(sub_key, msg_ids, sequence_ids)
        self._writer.ack(out)

        return out

# ################################################################################################################################

    def record_attempt(self, message:'anydict') -> 'bool':
        """ Records the next push attempt of a fetched message before its request is sent and stores its number
        in the message. On PostgreSQL, the attempt is committed in a transaction of its own, which confirms
        the generation of this server first, so a server that was replaced sends nothing. On SQLite, which only
        one server uses, the attempts are counted in memory. Returns False when the message has left
        the subscriber's queue in the meantime.
        """
        engine = self.engine

        if engine.dialect.name == Type_SQLite:
            message['delivery_attempt'] += 1
            return True

        parameters = {'attempt_delivery_id': message['delivery_id']}

        with engine.begin() as connection:
            attempt = connection.execute(_record_attempt_statement, parameters).scalar()

        if attempt is None:
            out = False
        else:
            message['delivery_attempt'] = attempt
            out = True

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

    def _database_now_ms(self) -> 'int':
        """ Returns the time of the pub/sub database in milliseconds since the Unix epoch.
        """
        clock = self.clock

        out = clock.now_ms()
        return out

# ################################################################################################################################
# ################################################################################################################################
