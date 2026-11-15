# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import unittest
from threading import Thread
from time import monotonic, sleep

# Zato
from zato.common.test.conftest_base_multi_cpu import connection_to_slot, get_json, ModuleCtx as MultiCPUCtx, post_json, \
     SQLiteWriteLock
from zato.common.test.config_multi_cpu_pubsub import PubSubConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, list_

    floatlist = list_[float]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_pubsub.sqlite_lock')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The variable with the path of the pub/sub database, which is set only when the database is SQLite
    DB_Path_Env = 'Zato_PubSub_DB_Path'

    Publish_Path = '/test/multi-cpu/publish'

    # How long the test process holds the write lock, well above the short busy timeout, in seconds
    Lock_Duration = 6.0

    # How long the lock is held before the publication is sent, in seconds
    Publish_Delay = 0.5

    # How often the ping is sent while the lock is held, and the longest a ping may take, in seconds
    Ping_Interval = 0.2
    Ping_Latency_Max = 0.5

    # The slot that serves both the publication and the pings
    Slot = 0

# ################################################################################################################################
# ################################################################################################################################

class TestSQLiteLockContention(unittest.TestCase):
    """ A write lock of the pub/sub database held from outside the server delays the publication that waits for it
    and not the other requests of the same worker.
    """

    def test_lock_delays_only_the_affected_request(self) -> 'None':

        if ModuleCtx.DB_Path_Env not in os.environ:
            self.skipTest('The pub/sub database is not SQLite')

        publish_connection = connection_to_slot(ModuleCtx.Slot)
        ping_connection = connection_to_slot(ModuleCtx.Slot)

        lock = SQLiteWriteLock(os.environ[ModuleCtx.DB_Path_Env], ModuleCtx.Lock_Duration)
        lock.start()

        sleep(ModuleCtx.Publish_Delay)

        # The publication waits for the lock in a thread of its own ..
        published:'anylist' = []

        def _publish() -> 'None':
            request = {'topic_name': PubSubConfig.Lock_Topic, 'data': {'seq': 0}}
            published.append(post_json(publish_connection, ModuleCtx.Publish_Path, request))

        publish_thread = Thread(target=_publish, daemon=True)
        publish_thread.start()

        # .. while the same worker answers the pings within the latency limit for as long as the lock is held ..
        latencies:'floatlist' = []
        lock_end = monotonic() + ModuleCtx.Lock_Duration - ModuleCtx.Publish_Delay

        while monotonic() < lock_end:
            started = monotonic()
            response = get_json(ping_connection, MultiCPUCtx.Worker_Slot_Path)
            latencies.append(monotonic() - started)

            self.assertEqual(response['slot'], ModuleCtx.Slot)
            sleep(ModuleCtx.Ping_Interval)

        lock.wait()
        publish_thread.join()

        publish_connection.close()
        ping_connection.close()

        logger.info('Ping latencies under the lock -> max %.3fs of %s', max(latencies), len(latencies))

        # .. and the publication completes once the lock is released.
        self.assertLess(max(latencies), ModuleCtx.Ping_Latency_Max)
        self.assertEqual(published[0]['slot'], ModuleCtx.Slot)

# ################################################################################################################################
# ################################################################################################################################
