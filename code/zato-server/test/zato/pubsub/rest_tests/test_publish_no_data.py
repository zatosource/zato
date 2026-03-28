# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
from base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestPublishNoData(BaseTestCase):

    def test_publish_without_data_fails(self) -> 'None':
        """ Test that publishing without data returns 400.
        """
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.publish_empty(topic)
        self.assertEqual(result.get('status_code'), 400)

# ################################################################################################################################
# ################################################################################################################################
