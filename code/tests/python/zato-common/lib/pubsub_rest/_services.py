# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# This file is hot-deployed into the server of a pub/sub suite, whose tests read through these services
# what the server keeps in its database, and publish with the retry settings of a message.

# stdlib
import time
from contextlib import closing

# SQLAlchemy
from sqlalchemy import bindparam, text

# Zato
from zato.common.audit_log.common import AuditEvent
from zato.common.db_env.database import get_database_engine
from zato.common.odb.model import PubSubSubscription, SecurityBase
from zato.common.pubsub.sql.counts import No_Publisher
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, Engine
    from zato.common.typing_ import any_, anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

# The isolation level in which the counts of a snapshot are read during traffic.
_snapshot_isolation_level = 'REPEATABLE READ'

# The raw counts and the stored counts that must equal them.
_raw_queue_query = text('select sub_key, topic_name, count(*) from pubsub_delivery group by sub_key, topic_name')
_stored_queue_query = text('select sub_key, topic_name, sum(depth) from pubsub_queue_count group by sub_key, topic_name')

_raw_topic_query = text('select topic_name, count(*) from pubsub_message group by topic_name')
_stored_topic_query = text('select topic_name, sum(total) from pubsub_topic_count group by topic_name')

_raw_publish_query = text(f"""
    select topic_name, pub_time_ms - pub_time_ms % 60000, coalesce(publisher, '{No_Publisher}'), count(*)
    from pubsub_message group by 1, 2, 3
""")
_stored_publish_query = text('select topic_name, minute_ms, publisher, sum(total) from pubsub_publish_count group by 1, 2, 3')

# The statistics of the tables, the WAL and the background writer of PostgreSQL.
_pg_tables_query = text("""
    select relname, n_live_tup, n_dead_tup, autovacuum_count from pg_stat_user_tables
    where relname in ('pubsub_message', 'pubsub_delivery')
""")
_pg_wal_query = text('select coalesce(sum(size), 0) from pg_ls_waldir()')
_pg_checkpoints_query = text('select checkpoints_timed + checkpoints_req from pg_stat_bgwriter')

# The rows of all the deliveries.
_delivery_rows_query = text('select count(*) from pubsub_delivery')

# The rows of one topic and of one queue.
_topic_message_query = text('select count(*) from pubsub_message where topic_name = :topic_name')
_topic_payload_query = text('select count(*) from pubsub_message where topic_name = :topic_name and not payload_dropped')
_topic_delivery_query = text('select count(*) from pubsub_delivery where topic_name = :topic_name')
_topic_sub_query = text('select count(*) from pubsub_topic_sub where topic_name = :topic_name')
_queue_depth_query = text('select count(*) from pubsub_delivery where sub_key = :sub_key')

# The messages whose delivery to a subscriber was given up.
_failed_events_query = text('select msg_id from event where event_type = :event_type and sub_key = :sub_key')

# The expirations of messages.
_expiration_query = text('select msg_id, expiration_ms from pubsub_message where msg_id in :msg_ids')
_expiration_query = _expiration_query.bindparams(bindparam('msg_ids', expanding=True))

# The locks that a cleanup sweep meets - the oldest messages of a topic.
_lock_rows_query = text("""
    select id from pubsub_message where topic_name = :topic_name order by id limit :row_count for update
""")

# The table of the messages, whose statistics PostgreSQL reports by its name.
_message_table = 'pubsub_message'

# ################################################################################################################################
# ################################################################################################################################

def _read_counts(connection:'Connection', query:'any_') -> 'anydict':
    out:'anydict' = {}

    for row in connection.execute(query):
        key = tuple(row[:-1])
        value = int(row[-1])
        if value:
            out[key] = value

    return out

# ################################################################################################################################

def _count(connection:'Connection', query:'any_', params:'anydict') -> 'int':
    out = connection.execute(query, params).scalar_one()
    return out

# ################################################################################################################################

def _hold_locks(engine:'Engine', query:'any_', params:'anydict', hold_seconds:'float') -> 'None':
    """ Takes the locks of the query and releases them after the given time, without a change to any row.
    """
    with engine.connect() as connection:
        _ = connection.execute(query, params)
        time.sleep(hold_seconds)
        connection.rollback()

# ################################################################################################################################
# ################################################################################################################################

class GetCountMismatches(Service):
    """ Returns each key whose stored count differs from the number of its rows - queues, topics and publications.
    All of them are read in one repeatable read transaction, which is consistent during traffic.
    """
    name = 'test.pubsub-rest.get-count-mismatches'

    def handle(self) -> 'None':

        engine = get_database_engine()
        engine = engine.execution_options(isolation_level=_snapshot_isolation_level)

        pairs = [
            ('queue', _raw_queue_query, _stored_queue_query),
            ('topic', _raw_topic_query, _stored_topic_query),
            ('publication', _raw_publish_query, _stored_publish_query),
        ]

        mismatches:'strlist' = []

        with engine.connect() as connection:
            for name, raw_query, stored_query in pairs:

                raw = _read_counts(connection, raw_query)
                stored = _read_counts(connection, stored_query)

                for key in sorted(set(raw) | set(stored)):

                    # A key without rows or without a stored count counts as zero.
                    if key in raw:
                        raw_value = raw[key]
                    else:
                        raw_value = 0

                    if key in stored:
                        stored_value = stored[key]
                    else:
                        stored_value = 0

                    if raw_value != stored_value:
                        mismatches.append(f'{name} {key}: {stored_value} stored, {raw_value} rows')

        self.response.payload = {'mismatches': mismatches}

# ################################################################################################################################
# ################################################################################################################################

class GetDatabaseStatistics(Service):
    """ Returns the sizes of the tables of messages and deliveries, the size of the WAL, the dead rows
    of the two tables, the number of autovacuum runs and the number of checkpoints so far.
    """
    name = 'test.pubsub-rest.get-database-statistics'

    def handle(self) -> 'None':

        engine = get_database_engine()

        out:'anydict' = {
            'message_rows': 0,
            'delivery_rows': 0,
            'wal_bytes': 0,
            'checkpoints': 0,
            'autovacuums': 0,
            'dead_tuples': {},
        }

        with engine.connect() as connection:

            for row in connection.execute(_pg_tables_query):
                if row.relname == _message_table:
                    out['message_rows'] = row.n_live_tup
                else:
                    out['delivery_rows'] = row.n_live_tup

                out['autovacuums'] += row.autovacuum_count
                out['dead_tuples'][row.relname] = [row.n_live_tup, row.n_dead_tup]

            out['wal_bytes'] = int(connection.execute(_pg_wal_query).scalar_one())
            out['checkpoints'] = connection.execute(_pg_checkpoints_query).scalar_one()

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

class GetTopicRows(Service):
    """ Returns the messages of a topic, those of them that keep their payload, its deliveries and its subscriptions.
    """
    name = 'test.pubsub-rest.get-topic-rows'

    def handle(self) -> 'None':

        params = {'topic_name': self.request.payload['topic_name']}

        with get_database_engine().connect() as connection:
            self.response.payload = {
                'messages': _count(connection, _topic_message_query, params),
                'payloads': _count(connection, _topic_payload_query, params),
                'deliveries': _count(connection, _topic_delivery_query, params),
                'subscriptions': _count(connection, _topic_sub_query, params),
            }

# ################################################################################################################################
# ################################################################################################################################

class GetDeliveryCount(Service):
    """ Returns how many deliveries all the queues hold, counted row by row.
    """
    name = 'test.pubsub-rest.get-delivery-count'

    def handle(self) -> 'None':

        with get_database_engine().connect() as connection:
            delivery_count = connection.execute(_delivery_rows_query).scalar_one()

        self.response.payload = {'delivery_count': delivery_count}

# ################################################################################################################################
# ################################################################################################################################

class GetQueueDepths(Service):
    """ Returns how many deliveries each of the given queues holds.
    """
    name = 'test.pubsub-rest.get-queue-depths'

    def handle(self) -> 'None':

        depths:'anydict' = {}

        with get_database_engine().connect() as connection:
            for sub_key in self.request.payload['sub_keys']:
                depths[sub_key] = _count(connection, _queue_depth_query, {'sub_key': sub_key})

        self.response.payload = {'depths': depths}

# ################################################################################################################################
# ################################################################################################################################

class GetFailedMessages(Service):
    """ Returns the messages of a subscriber whose delivery the audit log records as given up.
    """
    name = 'test.pubsub-rest.get-failed-messages'

    def handle(self) -> 'None':

        params = {'event_type': AuditEvent.Delivery_Failed, 'sub_key': self.request.payload['sub_key']}

        with get_database_engine().connect() as connection:
            rows = connection.execute(_failed_events_query, params).fetchall()

        msg_ids:'strlist' = []

        for row in rows:
            msg_ids.append(row.msg_id)

        self.response.payload = {'msg_ids': msg_ids}

# ################################################################################################################################
# ################################################################################################################################

class GetExpirations(Service):
    """ Returns the expiration that the server stored for each of the given messages, in milliseconds.
    """
    name = 'test.pubsub-rest.get-expirations'

    def handle(self) -> 'None':

        params = {'msg_ids': self.request.payload['msg_ids']}
        expirations:'anydict' = {}

        with get_database_engine().connect() as connection:
            for row in connection.execute(_expiration_query, params):
                expirations[row.msg_id] = row.expiration_ms

        self.response.payload = {'expirations': expirations}

# ################################################################################################################################
# ################################################################################################################################

class GetSubKeys(Service):
    """ Returns the subscription key of each subscriber, by the name of its security definition.
    """
    name = 'test.pubsub-rest.get-sub-keys'

    def handle(self) -> 'None':

        sub_keys:'anydict' = {}

        with closing(self.odb.session()) as session:
            query = session.query(SecurityBase.name, PubSubSubscription.sub_key)
            query = query.filter(PubSubSubscription.sec_base_id == SecurityBase.id)

            for sec_name, sub_key in query.all():
                sub_keys[sec_name] = sub_key

        self.response.payload = {'sub_keys': sub_keys}

# ################################################################################################################################
# ################################################################################################################################

class GetServerState(Service):
    """ Returns whether another server took over the pub/sub database of this one.
    """
    name = 'test.pubsub-rest.get-server-state'

    def handle(self) -> 'None':
        self.response.payload = {'is_replaced': self.server.pubsub_backend.is_replaced}

# ################################################################################################################################
# ################################################################################################################################

class HoldLocks(Service):
    """ Holds, for the given time, the locks that a cleanup sweep meets - row locks on the oldest messages of a topic.
    The database driver waits in the hub of this thread.
    """
    name = 'test.pubsub-rest.hold-locks'

    def handle(self) -> 'None':

        payload = self.request.payload
        hold_seconds = payload['hold_seconds']
        engine = get_database_engine()

        params = {'topic_name': payload['topic_name'], 'row_count': payload['row_count']}
        _hold_locks(engine, _lock_rows_query, params, hold_seconds)

        self.response.payload = {'is_held': True}

# ################################################################################################################################
# ################################################################################################################################

class Publish(Service):
    """ Publishes a message with the retry settings of its push deliveries, which the REST interface does not accept.
    """
    name = 'test.pubsub-rest.publish'

    def handle(self) -> 'None':

        payload = self.request.payload

        result = self.publish(
            payload['topic_name'],
            payload['data'],
            max_retries=payload['max_retries'],
            retry_sleep_time=payload['retry_sleep_time'],
        )

        self.response.payload = {'msg_id': result.msg_id}

# ################################################################################################################################
# ################################################################################################################################
