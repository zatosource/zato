# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone
from logging import getLogger

# gevent
from gevent.event import Event

# SQLAlchemy
from sqlalchemy import and_, exists, select

# Zato
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
    from zato.common.typing_ import any_, anydict, intlist, optional, strlist, strset

    auditlognone       = optional[AuditLog]
    cryptomanagernone  = optional[CryptoManager]

    # Dummy assignments to satisfy type checkers
    Connection = Connection
    Engine = Engine

sub_event_dict = dict[str, Event]

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

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
        audit_log:'auditlognone' = None,
        crypto_manager:'cryptomanagernone' = None,
        encrypt_at_rest:'bool' = False,
        ) -> 'None':

        # The audit log is injected by the server and is None in backend-only tests
        self.audit_log = audit_log

        # Payloads are encrypted before insert and decrypted after select when configured
        self.crypto_manager = crypto_manager
        self.encrypt_at_rest = encrypt_at_rest

        # Names of topics whose audit log was turned off explicitly - publications,
        # receptions and deliveries involving these topics write no audit events.
        self.audit_disabled_topics:'strset' = set()

        # One wake-up event per subscriber - publish sets them and blocking fetches wait on them,
        # which works because exactly one server process ever uses one pub/sub database.
        self._sub_events:'sub_event_dict' = {}

# ################################################################################################################################

    @property
    def engine(self) -> 'Engine':
        """ The engine behind the current Zato_PubSub_DB_* configuration - resolved on each
        access, with the per-configuration cache in db_env making the lookup cheap, so changing
        the variables at runtime redirects all new operations to the new database.
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
        The payload column is NULL once the message is fully delivered - and Oracle DB
        additionally stores empty strings as NULLs - so a missing payload reads as ''.
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
        query = select(topic_sub_table.c.sub_key)
        query = query.where(topic_sub_table.c.topic_name == topic_name)

        out:'strlist' = []

        for row in connection.execute(query):
            out.append(row.sub_key)

        return out

# ################################################################################################################################

    def _get_message_ids(self, connection:'Connection', msg_ids:'strlist') -> 'intlist':
        """ Maps public message identifiers to their primary keys, read within the caller's transaction.
        """
        query = select(message_table.c.id)
        query = query.where(message_table.c.msg_id.in_(msg_ids))

        out:'intlist' = []

        for row in connection.execute(query):
            out.append(row.id)

        return out

# ################################################################################################################################

    def _drop_fully_delivered_payloads(self, connection:'Connection', message_ids:'intlist') -> 'int':
        """ Sets the payload to NULL for each of the given messages that no subscriber needs anymore.
        The row itself stays behind as the delivered-message trace for counts, the publish timeline
        and delivered-message browsing. Returns how many payloads were dropped.
        """
        # A message is still in flight while any delivery row references it ..
        still_needed = exists()
        still_needed = still_needed.where(delivery_table.c.message_id == message_table.c.id)

        # .. so drop the payloads of the given messages that have none left.
        update_statement = message_table.update()
        update_statement = update_statement.where(and_(
            message_table.c.id.in_(message_ids),
            message_table.c.payload.isnot(None),
            ~still_needed,
        ))
        update_statement = update_statement.values(payload=None, payload_encrypted=False)

        result = connection.execute(update_statement)

        out = result.rowcount
        return out

# ################################################################################################################################

    def ack_messages(self, sub_key:'str', msg_ids:'strlist') -> 'int':
        """ Acknowledges many messages for one subscriber in a single transaction.
        Returns how many of them became fully delivered, i.e. no subscriber needs them anymore.
        """
        if not msg_ids:
            return 0

        with self.engine.begin() as connection:

            # Map the public identifiers to primary keys ..
            message_ids = self._get_message_ids(connection, msg_ids)

            if not message_ids:
                return 0

            # .. remove this subscriber's delivery rows ..
            delete_statement = delivery_table.delete()
            delete_statement = delete_statement.where(and_(
                delivery_table.c.sub_key == sub_key,
                delivery_table.c.message_id.in_(message_ids),
            ))
            _ = connection.execute(delete_statement)

            # .. and drop the payloads of messages that no subscriber needs anymore.
            out = self._drop_fully_delivered_payloads(connection, message_ids)

        logger.info('ack_messages -> sub_key:%s, acked:%d, fully_delivered:%d', sub_key, len(msg_ids), out)

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
