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

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class TestAckRemovesFromBothIndexes(BaseUnsubCleanupTestCase):
    """ Ack from sub_a removes it from both pending and sub_pending, sub_b intact, file exists.
    """

    def test_ack_removes_from_both_indexes(self) -> 'None':

        # Subscribe two consumers ..
        sub_key_a = f'sk_unsub_a_{self._run_id}'
        sub_key_b = f'sk_unsub_b_{self._run_id}'

        self.subscribe(sub_key_a)
        self.subscribe(sub_key_b)

        # .. publish a message ..
        _ = self.publish()
        data_ref = self.get_data_ref_from_stream()

        # .. fetch and ack from sub_a ..
        messages = self.backend.fetch_messages(sub_key_a)
        logger.info('fetch_messages(sub_key_a) -> %s', messages)

        message = messages[0]
        self.backend.ack_message(message['_stream_name'], sub_key_a, message['_redis_message_id'], message['_data_ref'])

        # .. pending:{data_ref} no longer contains sub_a ..
        has_a = self.has_pending_member(data_ref, sub_key_a)
        self.assertFalse(has_a)

        # .. sub_pending:{sub_a} no longer contains data_ref ..
        has_ref_a = self.has_sub_pending_member(sub_key_a, data_ref)
        self.assertFalse(has_ref_a)

        # .. pending:{data_ref} still contains sub_b ..
        has_b = self.has_pending_member(data_ref, sub_key_b)
        self.assertTrue(has_b)

        # .. sub_pending:{sub_b} still contains data_ref ..
        has_ref_b = self.has_sub_pending_member(sub_key_b, data_ref)
        self.assertTrue(has_ref_b)

        # .. and the file still exists.
        file_present = self.file_exists(data_ref)
        self.assertTrue(file_present)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
