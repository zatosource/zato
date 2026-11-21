# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import and_, delete, func, select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

# Zato
from zato.common.db_env.common import Type_PostgreSQL, Type_SQLite
from zato.common.db_env.plain_sql import PlainStatement
from zato.common.pubsub.subscription_list import Governed_Sub_Key_Length, Governed_Sub_Key_Pattern, Lock_Timeout_Ms
from zato.common.pubsub.sql.schema import topic_sub_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from zato.common.pubsub.sql.pending import PendingSync, pending_sync_list
    from zato.common.pubsub.subscription_list import pairlist
    from zato.common.typing_ import anylist

    Connection = Connection
    PendingSync = PendingSync
    pending_sync_list = pending_sync_list
    pairlist = pairlist
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# The row of a pair pending in the subscription list, which a sync inserts, leaving a concurrent insert as it is
_topic_sub_inserts = {
    Type_PostgreSQL: PlainStatement(postgresql_insert(topic_sub_table).on_conflict_do_nothing()),
    Type_SQLite: PlainStatement(sqlite_insert(topic_sub_table).on_conflict_do_nothing()),
}

# The governed rows of the pub/sub database, which startup, reload and a full reconciliation compare with the list
_governed_pairs_query = select(topic_sub_table.c.sub_key, topic_sub_table.c.topic_name)
_governed_pairs_query = _governed_pairs_query.where(and_(
    topic_sub_table.c.sub_key.like(Governed_Sub_Key_Pattern),
    func.length(topic_sub_table.c.sub_key) == Governed_Sub_Key_Length,
))

# The lock timeout of every pub/sub transaction on PostgreSQL, equal to the busy timeout of SQLite writes
_lock_timeout_ms = Lock_Timeout_Ms

# ################################################################################################################################
# ################################################################################################################################

def set_lock_timeout(connection:'Connection') -> 'None':
    """ Sets the lock timeout of the open transaction on PostgreSQL, and does nothing on SQLite.
    """
    if connection.dialect.name == Type_PostgreSQL:
        _ = connection.exec_driver_sql(f'SET LOCAL lock_timeout = {_lock_timeout_ms}')

# ################################################################################################################################

def read_governed_pairs(connection:'Connection') -> 'pairlist':
    """ Returns the governed subscriber and topic pairs whose rows are committed in the pub/sub database.
    """
    out:'pairlist' = []

    for row in connection.execute(_governed_pairs_query):
        out.append((row.sub_key, row.topic_name))

    return out

# ################################################################################################################################

def apply_syncs(connection:'Connection', syncs:'pending_sync_list') -> 'None':
    """ Inserts and deletes the governed pairs of each sync item in the open transaction of the connection.
    """
    dialect_name = connection.dialect.name
    topic_sub_insert = _topic_sub_inserts[dialect_name]

    for sync in syncs:

        if sync.added:
            rows:'anylist' = []

            for sub_key, topic_name in sync.added:
                rows.append({'sub_key': sub_key, 'topic_name': topic_name})

            _ = topic_sub_insert.insert_rows(connection, rows)

        for sub_key, topic_name in sync.removed:
            statement = delete(topic_sub_table).where(and_(
                topic_sub_table.c.sub_key == sub_key,
                topic_sub_table.c.topic_name == topic_name,
            ))
            _ = connection.execute(statement)

        # The pairs count as written only after the caller commits, which fills these from the inputs of the item
        sync.committed_added = list(sync.added)
        sync.committed_removed = list(sync.removed)

# ################################################################################################################################
# ################################################################################################################################
