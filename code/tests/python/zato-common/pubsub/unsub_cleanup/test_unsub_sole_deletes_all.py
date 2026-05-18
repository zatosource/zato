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

class TestUnsubSoleSubscriberDeletesAll(BaseUnsubCleanupTestCase):
    """ Publish 3 messages, 1 sub, unsubscribe -
        sub_pending gone, all 3 pending keys gone, pending_expiry clean, all 3 files deleted.
    """

    def test_unsub_sole_subscriber_deletes_everything(self) -> 'None':

        # Subscribe a single consumer ..
        sub_key = f'sub.unsub_sole.{self._run_id}'
        self.subscribe(sub_key)

        # .. publish 3 messages and collect their data_refs ..
        data_refs:'strlist' = []
        for _ in range(3):
            _ = self.publish()
            data_ref = self.get_data_ref_from_stream()
            data_refs.append(data_ref)

        # .. confirm all indexes are populated before unsubscribe ..
        for data_ref in data_refs:
            has_member = self.has_pending_member(data_ref, sub_key)
            self.assertTrue(has_member)

            has_ref = self.has_sub_pending_member(sub_key, data_ref)
            self.assertTrue(has_ref)

            has_expiry = self.has_expiry_entry(data_ref)
            self.assertTrue(has_expiry)

            file_present = self.file_exists(data_ref)
            self.assertTrue(file_present)

        # .. unsubscribe the sole subscriber ..
        self.backend.unsubscribe(sub_key, self.topic_name)

        # .. sub_pending:{sub_key} is gone ..
        sub_pending_key = f'zato:pubsub:sub_pending:{sub_key}'
        count = self.redis.scard(sub_pending_key)
        self.assertEqual(count, 0)

        # .. all 3 pending keys are gone ..
        for data_ref in data_refs:
            pending_count = self.get_pending_count(data_ref)
            self.assertEqual(pending_count, 0)

        # .. pending_expiry contains none of the 3 data_refs ..
        for data_ref in data_refs:
            has_expiry = self.has_expiry_entry(data_ref)
            self.assertFalse(has_expiry)

        # .. and all 3 files are deleted.
        for data_ref in data_refs:
            file_present = self.file_exists(data_ref)
            self.assertFalse(file_present)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
