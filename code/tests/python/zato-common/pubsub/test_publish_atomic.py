# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import shutil
import tempfile
import time
import unittest

# redis
from redis import Redis

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.redis_backend import ModuleCtx, RedisPubSubBackend
from zato.common.pubsub.disk_store import DiskMessageStore

# ################################################################################################################################
# ################################################################################################################################

_test_redis_host = 'localhost'
_test_redis_port = 6379

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class TestPublishAckRaceWithLua(unittest.TestCase):
    """ Proves that the Lua-based atomic publish prevents the race condition
    where a fast ack between XADD and SADD causes premature disk file deletion.
    """

    def setUp(self) -> 'None':

        # Set up a real Redis connection ..
        self.redis = Redis(host=_test_redis_host, port=_test_redis_port, db=PubSub.Test_Redis_DB, decode_responses=True)

        # .. set up a temp directory for disk store ..
        self.test_dir = tempfile.mkdtemp()
        self.disk_store = DiskMessageStore(self.test_dir)

        # .. create the backend instance ..
        self.backend = RedisPubSubBackend(self.redis, self.disk_store)

        # .. use a unique topic name per test run to avoid collisions ..
        self._run_id = f'{int(time.time())}'
        self.topic_name = f'test.race.{self._run_id}'
        self.push_sk = f'sk_push_{self._run_id}'
        self.pull_sk = f'sk_pull_{self._run_id}'

        # .. subscribe both ..
        self.backend.subscribe(self.push_sk, self.topic_name)
        self.backend.subscribe(self.pull_sk, self.topic_name)

# ################################################################################################################################

    def tearDown(self) -> 'None':

        # Clean up Redis keys ..
        topic_subs_key = f'{ModuleCtx.Topic_Subs_Prefix}{self.topic_name}'
        stream_key = f'{ModuleCtx.Stream_Prefix}{self.topic_name}'
        _ = self.redis.delete(topic_subs_key)
        _ = self.redis.delete(stream_key)

        for sk in (self.push_sk, self.pull_sk):
            subs_key = f'{ModuleCtx.Subs_Prefix}{sk}'
            _ = self.redis.delete(subs_key)
            sub_pending_key = f'{ModuleCtx.Sub_Pending_Prefix}{sk}'
            _ = self.redis.delete(sub_pending_key)

        # .. and the temp directory.
        shutil.rmtree(self.test_dir)

# ################################################################################################################################

    def test_ack_after_publish_does_not_delete_file(self) -> 'None':
        """ With the Lua fix, acking from push_sk immediately after publish
        still leaves the file intact because pull_sk is in the pending set.
        """

        # Publish a message ..
        result = self.backend.publish(self.topic_name, 'race-test-payload')
        msg_id = result.msg_id

        # .. read the data_ref from the stream ..
        stream_key = f'{ModuleCtx.Stream_Prefix}{self.topic_name}'
        messages = self.redis.xrevrange(stream_key, count=1)
        _, message_data = messages[0]
        data_ref = message_data['data_ref']
        redis_message_id = messages[0][0]

        # .. simulate push greenlet acking immediately ..
        self.backend.ack_message(stream_key, self.push_sk, redis_message_id, data_ref)

        # .. pending set should still have pull_sk ..
        pending_key = f'{ModuleCtx.Pending_Prefix}{data_ref}'
        remaining = self.redis.scard(pending_key)
        self.assertEqual(remaining, 1)
        self.assertTrue(self.redis.sismember(pending_key, self.pull_sk))

        # .. disk file must still exist ..
        absolute_path = os.path.join(self.test_dir, data_ref)
        self.assertTrue(os.path.exists(absolute_path))

        # .. and loadable ..
        load_result = self.disk_store.load(data_ref)
        self.assertEqual(load_result.data, 'race-test-payload')

        # .. cleanup ..
        _ = self.redis.delete(pending_key)
        _ = self.redis.zrem(ModuleCtx.Pending_Expiry_Key, data_ref)

# ################################################################################################################################

    def test_old_non_atomic_path_triggers_race(self) -> 'None':
        """ Demonstrates that without the Lua script (individual commands in the
        old order: XADD first, then SADD), an inline ack between them causes
        premature disk file deletion.
        """

        # Manually replicate the old non-atomic publish sequence:
        # 1. Store on disk
        # 2. XADD (message becomes visible)
        # 3. Inline ack fires (simulating greenlet)
        # 4. SADD (too late, file already deleted)

        from zato.common.pubsub.redis_backend import _default_stream_max_len
        from zato.common.util.api import new_msg_id
        from datetime import datetime, timedelta, timezone

        message_id = new_msg_id()
        now = datetime.now(timezone.utc)
        expiration_time = now + timedelta(seconds=3600)
        data = 'race-trigger-payload'

        data_ref = self.disk_store.store(message_id, self.topic_name, data, '')

        stream_key = f'{ModuleCtx.Stream_Prefix}{self.topic_name}'

        message = {
            'msg_id': message_id,
            'data_ref': data_ref,
            'data_size': str(len(data)),
            'data_preview': data,
            'topic_name': self.topic_name,
            'priority': '5',
            'pub_time_iso': now.isoformat(),
            'recv_time_iso': now.isoformat(),
            'expiration': '3600',
            'expiration_time_iso': expiration_time.isoformat(),
        }

        # Step 1: XADD (old code did this first)
        redis_message_id = self.redis.xadd(stream_key, message, maxlen=_default_stream_max_len)

        # Step 2: Simulate the greenlet acking between XADD and SADD
        self.backend.ack_message(stream_key, self.push_sk, redis_message_id, data_ref)

        # At this point, pending_key does not exist yet (SADD hasn't run).
        # ack_message does SREM (returns 0 on non-existent key), SCARD (returns 0),
        # so remaining == 0 and the file gets deleted.

        absolute_path = os.path.join(self.test_dir, data_ref)
        self.assertFalse(os.path.exists(absolute_path))

        # .. cleanup the stream entry ..
        _ = self.redis.delete(stream_key)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()
