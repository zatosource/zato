# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
from base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestPermissions(BaseTestCase):

    def run(self):
        client = self.get_client()
        forbidden_topic = self.config.topic_forbidden

        print('1. Publish to forbidden topic')
        result = client.publish(forbidden_topic, 'test message')
        self.assert_false(result.get('is_ok'), 'Publish to forbidden topic should fail')
        self.assert_equal(result.get('status'), 401, 'Should return 401 Unauthorized')

        print('2. Subscribe to forbidden topic')
        result = client.subscribe(forbidden_topic)
        self.assert_false(result.get('is_ok'), 'Subscribe to forbidden topic should fail')
        self.assert_equal(result.get('status'), 401, 'Should return 401 Unauthorized')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    import sys
    test = TestPermissions()
    success = test.execute()
    sys.exit(0 if success else 1)
