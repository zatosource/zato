# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The WAL segments of a new PostgreSQL container, created and recycled before the faults apply, so that a commit
# of a run never waits for a new segment to be zero-filled and flushed under the lock of the WAL.

# Zato
from zato.common.test.pubsub_database import connect

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# How long the connection waits for each statement, in seconds, which covers the checkpoint that recycles the segments.
_statement_timeout = 600

# The sizes of a segment and of the WAL that a checkpoint keeps for recycling, in bytes.
_segment_size_query = "select pg_size_bytes(current_setting('wal_segment_size'))"
_min_wal_size_query = "select pg_size_bytes(current_setting('min_wal_size'))"

# A WAL record without a transaction, which gives each switch a segment to close.
_wal_record_query = "select pg_logical_emit_message(false, 'zato.test.wal', '')"
_switch_query = 'select pg_switch_wal()'
_checkpoint_query = 'checkpoint'

# ################################################################################################################################
# ################################################################################################################################

def reserve_wal_segments(database:'PubSubDatabase') -> 'None':
    """ Creates as many WAL segments as min_wal_size holds and runs a checkpoint, which keeps all of them
    as recycled segments ahead of the current one.
    """
    connection = connect(database, is_admin=True, timeout=_statement_timeout)
    connection.autocommit = True

    try:
        cursor = connection.cursor()

        # Read the sizes of the container ..
        _ = cursor.execute(_segment_size_query)
        row:'any_' = cursor.fetchone()
        segment_size = row[0]

        _ = cursor.execute(_min_wal_size_query)
        row = cursor.fetchone()
        min_wal_size = row[0]

        # .. the current segment is one of those that min_wal_size holds ..
        segment_count = min_wal_size // segment_size
        segment_count -= 1

        # .. close one segment after another, each of which is created new ..
        for _ in range(segment_count):
            _ = cursor.execute(_wal_record_query)
            _ = cursor.execute(_switch_query)

        # .. and the checkpoint renames the closed segments to the names of the segments to come.
        _ = cursor.execute(_checkpoint_query)

    finally:
        connection.close()

# ################################################################################################################################
# ################################################################################################################################
