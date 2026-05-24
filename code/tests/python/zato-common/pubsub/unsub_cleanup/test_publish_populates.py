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

class TestPublishPopulatesIndexes(BaseUnsubCleanupTestCase):
    """ Publish 1 message to topic with 2 subs - both indexes and expiry populated.
    """

    def test_publish_populates_all_indexes(self) -> 'None':

        # Subscribe two consumers ..
        sub_key_a = f'sk_unsub_a_{self._run_id}'
        sub_key_b = f'sk_unsub_b_{self._run_id}'

        self.subscribe(sub_key_a)
        self.subscribe(sub_key_b)

        # .. publish a message ..
        _ = self.publish()
        data_ref = self.get_data_ref_from_stream()

        # .. pending:{data_ref} contains both sub_keys ..
        has_a = self.has_pending_member(data_ref, sub_key_a)
        self.assertTrue(has_a)

        has_b = self.has_pending_member(data_ref, sub_key_b)
        self.assertTrue(has_b)

        # .. sub_pending:{sub_a} contains data_ref ..
        has_ref_a = self.has_sub_pending_member(sub_key_a, data_ref)
        self.assertTrue(has_ref_a)

        # .. sub_pending:{sub_b} contains data_ref ..
        has_ref_b = self.has_sub_pending_member(sub_key_b, data_ref)
        self.assertTrue(has_ref_b)

        # .. and pending_expiry contains data_ref.
        has_expiry = self.has_expiry_entry(data_ref)
        self.assertTrue(has_expiry)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
