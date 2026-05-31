# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import unittest

# test
from _base import BaseUnsubCleanupTestCase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class TestAckOneThenUnsub(BaseUnsubCleanupTestCase):
    """ Publish 3 messages, 2 subs, sub A acks message 1, then unsubscribe A -
        sub_pending:{sub_a} gone, all pending sets contain sub_b only, all files exist.
    """

    def test_ack_one_then_unsub_clears_sub_a(self) -> 'None':

        # Subscribe two consumers ..
        sub_key_a = f'sk_unsub_a_{self._run_id}'
        sub_key_b = f'sk_unsub_b_{self._run_id}'

        self.subscribe(sub_key_a)
        self.subscribe(sub_key_b)

        # .. publish 3 messages and collect their data_refs ..
        data_refs:'strlist' = []

        for _ in range(3):
            _ = self.publish()
            data_ref = self.get_data_ref_from_stream()
            data_refs.append(data_ref)

        # .. fetch messages for sub_a and ack only the first one ..
        messages = self.backend.fetch_messages(sub_key_a)
        first_message = messages[0]

        stream_name = first_message['_stream_name']
        redis_id = first_message['_redis_message_id']
        msg_data_ref = first_message['_data_ref']

        logger.info('ack_message input -> stream_name:%s, sub_key:%s, redis_id:%s, data_ref:%s',
            stream_name, sub_key_a, redis_id, msg_data_ref)

        is_fully_cleaned = self.backend.ack_message(stream_name, sub_key_a, redis_id, msg_data_ref)

        logger.info('ack_message output -> is_fully_cleaned:%s', is_fully_cleaned)
        self.assertFalse(is_fully_cleaned)

        # .. now unsubscribe sub_a ..
        self.backend.unsubscribe(sub_key_a, self.topic_name)

        # .. sub_pending:{sub_a} key is gone ..
        sub_pending_key = f'zato:pubsub:sub_pending:{sub_key_a}'
        count = self.redis.scard(sub_pending_key)
        self.assertEqual(count, 0)

        # .. all 3 pending sets contain only sub_b ..
        for data_ref in data_refs:
            has_a = self.has_pending_member(data_ref, sub_key_a)
            self.assertFalse(has_a)

            has_b = self.has_pending_member(data_ref, sub_key_b)
            self.assertTrue(has_b)

        # .. sub_pending:{sub_b} still has all 3 data_refs ..
        for data_ref in data_refs:
            has_ref = self.has_sub_pending_member(sub_key_b, data_ref)
            self.assertTrue(has_ref)

        # .. and all files still exist.
        for data_ref in data_refs:
            file_present = self.file_exists(data_ref)
            self.assertTrue(file_present)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
