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
from zato.common.pubsub.redis_backend import ModuleCtx, RedisPubSubBackend
from zato.common.pubsub.disk_store import DiskMessageStore
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

_test_redis_host = 'localhost'
_test_redis_port = 6379
_test_redis_db   = 0

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class BaseUnsubCleanupTestCase(unittest.TestCase):
    """ Shared setUp, tearDown, and helpers for all unsub cleanup tests.
    """

    def setUp(self) -> 'None':

        # Set up a real Redis connection ..
        self.redis = Redis(host=_test_redis_host, port=_test_redis_port, db=_test_redis_db, decode_responses=True)

        # .. set up a temp directory for disk store ..
        self.test_dir = tempfile.mkdtemp()
        self.disk_store = DiskMessageStore(self.test_dir)

        # .. create the backend instance ..
        self.backend = RedisPubSubBackend(self.redis, self.disk_store)

        # .. use a unique topic name per test run to avoid collisions ..
        self._run_id = f'{int(time.time())}'
        self.topic_name = f'test.unsub.{self._run_id}'

        # .. track resources created during the test for cleanup.
        self.created_data_refs:'strlist' = []
        self.subscribed_keys:'strlist' = []

# ################################################################################################################################

    def tearDown(self) -> 'None':

        # Clean up all Redis keys created during the test ..
        for data_ref in self.created_data_refs:
            pending_key = f'{ModuleCtx.Pending_Prefix}{data_ref}'
            _ = self.redis.delete(pending_key)
            _ = self.redis.zrem(ModuleCtx.Pending_Expiry_Key, data_ref)

        # .. clean up subscriber, topic, and stream keys ..
        topic_subs_key = f'{ModuleCtx.Topic_Subs_Prefix}{self.topic_name}'
        stream_key = f'{ModuleCtx.Stream_Prefix}{self.topic_name}'
        _ = self.redis.delete(topic_subs_key)
        _ = self.redis.delete(stream_key)

        for sub_key in self.subscribed_keys:
            subs_key = f'{ModuleCtx.Subs_Prefix}{sub_key}'
            _ = self.redis.delete(subs_key)
            sub_pending_key = f'{ModuleCtx.Sub_Pending_Prefix}{sub_key}'
            _ = self.redis.delete(sub_pending_key)

        # .. and the temp directory.
        shutil.rmtree(self.test_dir)

# ################################################################################################################################

    def subscribe(self, sub_key:'str') -> 'None':
        """ Subscribe a sub_key to the test topic and track it for cleanup.
        """
        self.backend.subscribe(sub_key, self.topic_name)
        self.subscribed_keys.append(sub_key)
        logger.info('subscribe -> sub_key:%s, topic_name:%s', sub_key, self.topic_name)

# ################################################################################################################################

    def publish(self, data:'str'='test payload') -> 'str':
        """ Publish a message to the test topic and track its data_ref for cleanup.
        """
        result = self.backend.publish(self.topic_name, data)
        msg_id = result.msg_id
        logger.info('publish -> msg_id:%s, topic_name:%s', msg_id, self.topic_name)

        return msg_id

# ################################################################################################################################

    def get_data_ref_from_stream(self) -> 'str':
        """ Reads the last message from the stream and returns its data_ref.
        """
        stream_key = f'{ModuleCtx.Stream_Prefix}{self.topic_name}'
        messages:'anylist' = cast_('anylist', self.redis.xrevrange(stream_key, count=1))
        _, message_data = messages[0]
        data_ref = message_data['data_ref']

        self.created_data_refs.append(data_ref)
        logger.info('get_data_ref_from_stream -> data_ref:%s', data_ref)

        return data_ref

# ################################################################################################################################

    def has_pending_member(self, data_ref:'str', sub_key:'str') -> 'bool':
        """ Returns True if the sub_key is in the pending set for data_ref.
        """
        pending_key = f'{ModuleCtx.Pending_Prefix}{data_ref}'

        out = self.redis.sismember(pending_key, sub_key)
        logger.info('has_pending_member -> data_ref:%s, sub_key:%s, result:%s', data_ref, sub_key, out)

        return bool(out)

# ################################################################################################################################

    def has_sub_pending_member(self, sub_key:'str', data_ref:'str') -> 'bool':
        """ Returns True if the data_ref is in the sub_pending set for sub_key.
        """
        sub_pending_key = f'{ModuleCtx.Sub_Pending_Prefix}{sub_key}'

        out = self.redis.sismember(sub_pending_key, data_ref)
        logger.info('has_sub_pending_member -> sub_key:%s, data_ref:%s, result:%s', sub_key, data_ref, out)

        return bool(out)

# ################################################################################################################################

    def has_expiry_entry(self, data_ref:'str') -> 'bool':
        """ Returns True if the data_ref is still in the expiry sorted set.
        """
        score = self.redis.zscore(ModuleCtx.Pending_Expiry_Key, data_ref)
        logger.info('has_expiry_entry -> data_ref:%s, score:%s', data_ref, score)

        out = score is not None
        return out

# ################################################################################################################################

    def get_pending_count(self, data_ref:'str') -> 'int':
        """ Returns the number of subscribers still in the pending set.
        """
        pending_key = f'{ModuleCtx.Pending_Prefix}{data_ref}'

        out = cast_('int', self.redis.scard(pending_key))
        logger.info('get_pending_count -> data_ref:%s, count:%s', data_ref, out)

        return out

# ################################################################################################################################

    def file_exists(self, data_ref:'str') -> 'bool':
        """ Returns True if the disk file for the given data_ref exists.
        """
        absolute_path = os.path.join(self.test_dir, data_ref)

        out = os.path.exists(absolute_path)
        logger.info('file_exists -> data_ref:%s, exists:%s', data_ref, out)

        return out

# ################################################################################################################################
# ################################################################################################################################
