# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import unittest

# local
from zato.common.test.client import PublishClient
from config import TestConfig

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_push.publish_rejection')

# ################################################################################################################################
# ################################################################################################################################

class TestPublishRejection(unittest.TestCase):
    """ Tests for publish rejection scenarios - wrong credentials, nonexistent topic, empty data.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.publisher = PublishClient(
            TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

# ################################################################################################################################

    def test_wrong_credentials_returns_401(self) -> 'None':
        """ Publishing with wrong credentials must return 401.
        """

        topic_name = 'iam.user.created'

        # Publish with wrong credentials ..
        result = self.publisher.publish_raw(topic_name, 'rejected payload', username='wrong_user', password='wrong_pass')
        logger.info('Wrong credentials -> status_code:%d, body:%s', result.status_code, result.body)

        # .. must be rejected with 401.
        self.assertEqual(result.status_code, 401)

# ################################################################################################################################

    def test_nonexistent_topic_returns_error(self) -> 'None':
        """ Publishing to a nonexistent topic must return >= 400.
        """

        topic_name = 'nonexistent.topic.that.does.not.exist'

        # Publish to a topic that does not exist ..
        result = self.publisher.publish_raw(
            topic_name, 'rejected payload',
            username=TestConfig.publisher_username, password=TestConfig.publisher_password)

        logger.info('Nonexistent topic -> status_code:%d, body:%s', result.status_code, result.body)

        # .. must return an error status code.
        self.assertGreaterEqual(result.status_code, 400)

# ################################################################################################################################

    def test_empty_data_accepted(self) -> 'None':
        """ Publishing with empty data dict is valid and returns 200.
        """

        topic_name = 'iam.user.created'

        # Publish with empty data ..
        result = self.publisher.publish_raw(
            topic_name, {},
            username=TestConfig.publisher_username, password=TestConfig.publisher_password)

        logger.info('Empty data -> status_code:%d, body:%s', result.status_code, result.body)

        # .. the server accepts it as valid publish payload.
        self.assertEqual(result.status_code, 200)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
