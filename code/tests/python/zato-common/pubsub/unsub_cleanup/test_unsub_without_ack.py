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

class TestUnsubWithoutAck(BaseUnsubCleanupTestCase):
    """ Publish 3 messages, 2 subs, unsubscribe A without acking -
        sub_pending:{sub_a} key gone, all 3 pending sets no longer contain sub_a, sub_b intact, all files exist.
    """

    def test_unsub_without_ack_clears_sub_a(self) -> 'None':

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

        # .. confirm sub_a is in all pending sets before unsubscribe ..
        for data_ref in data_refs:
            has_a = self.has_pending_member(data_ref, sub_key_a)
            self.assertTrue(has_a)

        # .. confirm sub_pending:{sub_a} has all 3 data_refs ..
        for data_ref in data_refs:
            has_ref = self.has_sub_pending_member(sub_key_a, data_ref)
            self.assertTrue(has_ref)

        # .. unsubscribe sub_a without acking anything ..
        self.backend.unsubscribe(sub_key_a, self.topic_name)

        # .. sub_pending:{sub_a} key is gone (no members) ..
        sub_pending_key = f'zato:pubsub:sub_pending:{sub_key_a}'
        count = self.redis.scard(sub_pending_key)
        self.assertEqual(count, 0)

        # .. all 3 pending sets no longer contain sub_a ..
        for data_ref in data_refs:
            has_a = self.has_pending_member(data_ref, sub_key_a)
            self.assertFalse(has_a)

        # .. sub_b is still in all 3 pending sets ..
        for data_ref in data_refs:
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
