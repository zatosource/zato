# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from contextlib import contextmanager
from time import monotonic

# Zato
from live_sql.env import database_env
from zato.common.pubsub.sql.config import get_pubsub_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import callable_, stranydict

    envgen = Iterator[None]
    floatlist = list[float]

# ################################################################################################################################
# ################################################################################################################################

# The prefix all the pub/sub database environment variables share
_env_prefix = 'Zato_PubSub_DB_'

# Every user-visible operation must complete within this many seconds
Max_Operation_Seconds = 0.050

# The performance floor the whole backend must sustain
Min_Publish_Rate_Per_Second  = 100
Min_Delivery_Rate_Per_Second = 500

# The two scales the mass-drain scenario runs at - the main perf target uses
# the smaller one and the dedicated mass target the bigger one. With 100
# subscribers that is a total backlog of one million and ten million messages.
Mass_Drain_Backlog_Main = 10000
Mass_Drain_Backlog_Mass = 100000

# How long each scale may take before it is declared hung, in seconds
Mass_Drain_Deadline_Main = 600
Mass_Drain_Deadline_Mass = 3600

# The concurrent-publish floors of the two scales. The main scale holds the standard
# floor. At the mass scale publishes contend with a hundred continuously draining
# consumers for one serialized database - there the binding guarantee is the
# per-operation time bound, and the floor is what that bound implies
# for strictly serialized publishing.
Mass_Drain_Publish_Floor_Main = Min_Publish_Rate_Per_Second
Mass_Drain_Publish_Floor_Mass = int(1 / Max_Operation_Seconds)

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def pubsub_backend_env(details:'stranydict') -> 'envgen':
    """ Points the Zato_PubSub_DB_* variables at one backend for the duration of a test.
    """
    with database_env(_env_prefix, details):
        yield

# ################################################################################################################################

def cleanup_sqlite_db(db_path:'str') -> 'None':
    """ Removes the SQLite database of one test run so big perf databases never
    pile up on disk - pytest's own tmp_path retention keeps the last three runs,
    which at mass scale would hold many gigabytes.
    """

    # Release all pooled connections first so the files are free to go ..
    engine = get_pubsub_engine()
    engine.dispose()

    # .. and remove the database along with its WAL companions.
    for suffix in ('', '-wal', '-shm'):
        path = db_path + suffix

        if os.path.exists(path):
            os.remove(path)

# ################################################################################################################################

def measure_median_seconds(operation:'callable_', iterations:'int') -> 'float':
    """ Runs an operation repeatedly and returns its median duration in seconds -
    the median keeps one-off cache misses and scheduler blips out of the verdict.
    """
    timings:'floatlist' = []

    for _ in range(iterations):
        start = monotonic()
        _ = operation()
        elapsed = monotonic() - start
        timings.append(elapsed)

    timings.sort()

    middle_index = len(timings) // 2
    out = timings[middle_index]

    return out

# ################################################################################################################################
# ################################################################################################################################
