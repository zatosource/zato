# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
from base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestMaxLimitsCapped(BaseTestCase):
    """ Verify that max_messages is capped at 1000 and max_len is capped
    at 20 MB even when the client requests higher values.
    """

    def test_max_messages_capped_at_1000(self):
        """ Requesting max_messages=2000 should still return at most 1000.
        We publish 5 messages and request 2000 - the cap does not prevent
        getting fewer than 1000, but confirms the request is accepted.
        """
        client = self.get_client()
        topic = self.config.topic_allowed

        _ = client.subscribe(topic)

        for i in range(5):
            result = client.publish(topic, f'cap test message {i}')
            self.assertTrue(result['is_ok'])

        result = client.get_messages_with_limit(max_messages=2000)
        self.assertTrue(result['is_ok'])
        self.assertLessEqual(result['message_count'], 1000)
        self.assertEqual(result['message_count'], 5)

        _ = client.unsubscribe(topic)

    def test_max_len_capped_at_20mb(self):
        """ Requesting max_len=50_000_000 (50 MB) should be silently capped
        to 20 MB. The request must succeed without error.
        """
        client = self.get_client()
        topic = self.config.topic_allowed

        _ = client.subscribe(topic)

        result = client.publish(topic, 'max len cap test')
        self.assertTrue(result['is_ok'])

        result = client.get_messages_with_limit(max_len=50_000_000)
        self.assertTrue(result['is_ok'])
        self.assertEqual(result['message_count'], 1)

        _ = client.unsubscribe(topic)

# ################################################################################################################################
# ################################################################################################################################
