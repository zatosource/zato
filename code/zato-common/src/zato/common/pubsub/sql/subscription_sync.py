# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import and_, delete, func, select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert

# Zato
from zato.common.db_env.plain_sql import PlainStatement
from zato.common.pubsub.subscription_list import Governed_Sub_Key_Length, Governed_Sub_Key_Pattern
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
_topic_sub_insert = postgresql_insert(topic_sub_table).on_conflict_do_nothing()
_topic_sub_insert_plain = PlainStatement(_topic_sub_insert)

# The governed rows of the pub/sub database, which startup, reload and a full reconciliation compare with the list
_governed_pairs_query = select(topic_sub_table.c.sub_key, topic_sub_table.c.topic_name)
_governed_pairs_query = _governed_pairs_query.where(and_(
    topic_sub_table.c.sub_key.like(Governed_Sub_Key_Pattern),
    func.length(topic_sub_table.c.sub_key) == Governed_Sub_Key_Length,
))

# ################################################################################################################################
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
    for sync in syncs:

        if sync.added:
            rows:'anylist' = []

            for sub_key, topic_name in sync.added:
                rows.append({'sub_key': sub_key, 'topic_name': topic_name})

            _ = _topic_sub_insert_plain.insert_rows(connection, rows)

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
