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

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.pubsub.sql.config import get_pubsub_engine
from zato.common.pubsub.sql.writes import drop_payloads_statement, new_pending_ack, PubSubWriter
from zato.common.typing_ import cast_
from zato.common.util.time_ import datetime_to_ms, utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, Engine
    from zato.common.audit_log.api import AuditLog
    from zato.common.crypto.api import CryptoManager
    from zato.common.pubsub.sql.writes import PendingAck
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

_retry = HTTP_SOAP.Retry

# How long back-to-back SQLite calls may hold the event loop before the backend
# yields it, in seconds - see _yield_after_write.
_yield_interval_seconds = 0.005

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

# ################################################################################################################################

    @property
    def engine(self) -> 'Engine':
        """ The engine behind the current Zato_PubSub_DB_Path, resolved on each access.
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
        result = connection.execute(drop_payloads_statement, {'drop_message_ids': message_ids})

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

        pending = self._ack(sub_key, msg_ids, sequence_ids)
        out = pending.fully_delivered_count

        logger.info('ack_messages -> sub_key:%s, acked:%d, fully_delivered:%d', sub_key, len(msg_ids), out)

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
