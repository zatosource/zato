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
            logger.info(f'Checking diagnostics for topics (attempt {attempt}/{max_attempts})')

            data = self._call_diagnostics()
            if not data:
                logger.warning('No diagnostics data received')
                time.sleep(0.5)
                continue

            topics_data = data.get('data', {}).get('topics', {})
            if not topics_data:
                logger.warning('No topics section in diagnostics data')
                time.sleep(0.5)
                continue

            missing_topics = []
            for topic_name in self.test_topics:
                if topic_name not in topics_data:
                    missing_topics.append(topic_name)

            if not missing_topics:
                logger.info(f'All test topics found in diagnostics: {self.test_topics}')
                return data
            else:
                logger.info(f'Missing topics: {missing_topics}, retrying in 0.1s')
                time.sleep(0.5)

        logger.error(f'Timeout waiting for topics to appear in diagnostics after {max_attempts} attempts')
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
