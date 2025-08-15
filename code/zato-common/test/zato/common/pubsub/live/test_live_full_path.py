# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import time
from unittest import main

# Zato
from zato.common.test.unittest_pubsub_requests import PubSubRESTServerBaseTestCase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class PubSubRESTServerTestCase(PubSubRESTServerBaseTestCase):
    """ Test cases for the pub/sub REST server.
    """

# ################################################################################################################################

    def _wait_for_objects_in_diagnostics(self) -> 'any_':
        """ Wait for all test objects to appear in diagnostics response.
        """
        max_attempts = 100_000_000
        attempt = 0
        data = None

        while attempt < max_attempts:
            attempt += 1
            logger.info(f'Checking diagnostics for objects (attempt {attempt}/{max_attempts})')

            data = self._call_diagnostics()
            if not data:
                logger.warning('No diagnostics data received')
                time.sleep(0.5)
                continue

            diagnostics_data = data.get('data', {})
            if not diagnostics_data:
                logger.warning('No data section in diagnostics response')
                time.sleep(0.5)
                continue

            missing_objects = []

            # Check topics
            if 'pubsub_topic' in self.config:
                topics_data = diagnostics_data.get('topics', {})
                for topic_config in self.config['pubsub_topic']:
                    topic_name = topic_config['name']
                    if topic_name not in topics_data:
                        missing_objects.append(f'topic:{topic_name}')

            # Check users
            if 'security' in self.config:
                users_data = diagnostics_data.get('users', {})
                for security_config in self.config['security']:
                    username = security_config['username']
                    if username not in users_data:
                        missing_objects.append(f'user:{username}')

            # Check permissions - pattern_matcher clients use usernames
            if 'pubsub_permission' in self.config:
                pattern_matcher_data = diagnostics_data.get('pattern_matcher', {})
                clients_data = pattern_matcher_data.get('clients', {})
                for permission_config in self.config['pubsub_permission']:
                    security_name = permission_config['security']
                    # Find the username that has this security definition
                    username = None
                    for user_config in self.config.get('security', []):
                        if user_config.get('name') == security_name:
                            username = user_config.get('username')
                            break
                    if username and username not in clients_data:
                        missing_objects.append(f'permission:{username}')

            # Check subscriptions
            if 'pubsub_subscription' in self.config:
                subscriptions_data = diagnostics_data.get('subscriptions', {})
                for subscription_config in self.config['pubsub_subscription']:
                    for topic_name in subscription_config['topic_list']:
                        if topic_name not in subscriptions_data:
                            missing_objects.append(f'subscription:{topic_name}')

            if not missing_objects:
                logger.info('All config objects found in diagnostics')
                return data
            else:
                logger.info(f'Missing objects: {missing_objects}, retrying in 0.5s')
                time.sleep(0.5)

        logger.error(f'Timeout waiting for objects to appear in diagnostics after {max_attempts} attempts')
        return data

# ################################################################################################################################

    def test_full_path(self) -> 'None':
        """ Test full path with enmasse configuration.
        """
        # Skip auto-unsubscribe for this test
        self.skip_auto_unsubscribe = True

        # Run enmasse
        self._wait_for_objects_in_diagnostics()

        print(111)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
