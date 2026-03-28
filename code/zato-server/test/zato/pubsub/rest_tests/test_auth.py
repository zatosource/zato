# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
from base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestAuth(BaseTestCase):

    def run(self):
        topic = self.config.topic_allowed

        print('1. Publish with wrong password')
        client = self.get_client(self.config.user1_username, 'wrong_password')
        result = client.publish(topic, 'test message')
        self.assert_false(result.get('is_ok'), 'Publish with wrong password should fail')
        self.assert_equal(result.get('status'), 401, 'Should return 401 Unauthorized')

        print('2. Subscribe with wrong password')
        result = client.subscribe(topic)
        self.assert_false(result.get('is_ok'), 'Subscribe with wrong password should fail')
        self.assert_equal(result.get('status'), 401, 'Should return 401 Unauthorized')

        print('3. Publish with non-existent user')
        client = self.get_client('nonexistent_user', 'some_password')
        result = client.publish(topic, 'test message')
        self.assert_false(result.get('is_ok'), 'Publish with non-existent user should fail')
        self.assert_equal(result.get('status'), 401, 'Should return 401 Unauthorized')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    import sys
    test = TestAuth()
    success = test.execute()
    sys.exit(0 if success else 1)
