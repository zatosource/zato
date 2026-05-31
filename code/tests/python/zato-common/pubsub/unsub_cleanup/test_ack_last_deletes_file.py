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

class TestAckLastSubscriberDeletesFile(BaseUnsubCleanupTestCase):
    """ Ack from both subs - pending key gone, both sub_pending cleared, expiry gone, file deleted.
    """

    def test_ack_from_both_deletes_everything(self) -> 'None':

        # Subscribe two consumers ..
        sub_key_a = f'sk_unsub_a_{self._run_id}'
        sub_key_b = f'sk_unsub_b_{self._run_id}'

        self.subscribe(sub_key_a)
        self.subscribe(sub_key_b)

        # .. publish a message ..
        _ = self.publish()
        data_ref = self.get_data_ref_from_stream()

        # .. fetch and ack from sub_a ..
        messages_a = self.backend.fetch_messages(sub_key_a)
        logger.info('fetch_messages(sub_key_a) -> %s', messages_a)

        message_a = messages_a[0]
        stream_name_a = message_a['_stream_name']
        redis_id_a = message_a['_redis_message_id']
        data_ref_a = message_a['_data_ref']

        logger.info('ack_message input -> stream_name:%s, sub_key:%s, redis_id:%s, data_ref:%s',
            stream_name_a, sub_key_a, redis_id_a, data_ref_a)

        is_fully_cleaned_a = self.backend.ack_message(stream_name_a, sub_key_a, redis_id_a, data_ref_a)

        logger.info('ack_message output -> is_fully_cleaned:%s', is_fully_cleaned_a)
        self.assertFalse(is_fully_cleaned_a)

        # .. file still exists after first ack ..
        file_present = self.file_exists(data_ref)
        self.assertTrue(file_present)

        # .. fetch and ack from sub_b ..
        messages_b = self.backend.fetch_messages(sub_key_b)
        logger.info('fetch_messages(sub_key_b) -> %s', messages_b)

        message_b = messages_b[0]
        stream_name_b = message_b['_stream_name']
        redis_id_b = message_b['_redis_message_id']
        data_ref_b = message_b['_data_ref']

        logger.info('ack_message input -> stream_name:%s, sub_key:%s, redis_id:%s, data_ref:%s',
            stream_name_b, sub_key_b, redis_id_b, data_ref_b)

        is_fully_cleaned_b = self.backend.ack_message(stream_name_b, sub_key_b, redis_id_b, data_ref_b)

        logger.info('ack_message output -> is_fully_cleaned:%s', is_fully_cleaned_b)
        self.assertTrue(is_fully_cleaned_b)

        # .. pending:{data_ref} key is gone ..
        pending_count = self.get_pending_count(data_ref)
        self.assertEqual(pending_count, 0)

        # .. sub_pending:{sub_a} does not contain data_ref ..
        has_ref_a = self.has_sub_pending_member(sub_key_a, data_ref)
        self.assertFalse(has_ref_a)

        # .. sub_pending:{sub_b} does not contain data_ref ..
        has_ref_b = self.has_sub_pending_member(sub_key_b, data_ref)
        self.assertFalse(has_ref_b)

        # .. pending_expiry does not contain data_ref ..
        has_expiry = self.has_expiry_entry(data_ref)
        self.assertFalse(has_expiry)

        # .. and the file is deleted.
        file_present = self.file_exists(data_ref)
        self.assertFalse(file_present)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
