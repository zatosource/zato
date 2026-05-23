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

class TestAckAllThenUnsubLastDeletes(BaseUnsubCleanupTestCase):
    """ Publish 2 messages, 2 subs, sub B acks both, unsubscribe A -
        both files deleted (A was last pending), both pending keys gone, pending_expiry empty.
    """

    def test_ack_all_then_unsub_last_deletes_files(self) -> 'None':

        # Subscribe two consumers ..
        sub_key_a = f'sk_unsub_a_{self._run_id}'
        sub_key_b = f'sk_unsub_b_{self._run_id}'

        self.subscribe(sub_key_a)
        self.subscribe(sub_key_b)

        # .. publish 2 messages and collect their data_refs ..
        data_refs:'strlist' = []

        for _ in range(2):
            _ = self.publish()
            data_ref = self.get_data_ref_from_stream()
            data_refs.append(data_ref)

        # .. sub_b acks both messages ..
        messages_b = self.backend.fetch_messages(sub_key_b)

        for message in messages_b:
            self.backend.ack_message(
                message['_stream_name'], sub_key_b,
                message['_redis_message_id'], message['_data_ref'])

        # .. after sub_b acks, pending sets still contain sub_a, files still exist ..
        for data_ref in data_refs:
            has_a = self.has_pending_member(data_ref, sub_key_a)
            self.assertTrue(has_a)

            file_present = self.file_exists(data_ref)
            self.assertTrue(file_present)

        # .. now unsubscribe sub_a (the last pending subscriber) ..
        self.backend.unsubscribe(sub_key_a, self.topic_name)

        # .. both pending keys are gone ..
        for data_ref in data_refs:
            pending_count = self.get_pending_count(data_ref)
            self.assertEqual(pending_count, 0)

        # .. pending_expiry has neither data_ref ..
        for data_ref in data_refs:
            has_expiry = self.has_expiry_entry(data_ref)
            self.assertFalse(has_expiry)

        # .. and both files are deleted.
        for data_ref in data_refs:
            file_present = self.file_exists(data_ref)
            self.assertFalse(file_present)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
