# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc
from unittest import main, TestCase

# requests
import requests

# Zato
from zato.common.api import PubSub

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class TestUnsubscribe(TestCase):

    def test_unsubscribe_success(self):

        topic_name = 'demo.21'

        url = f'http://localhost:{PubSub.REST_Server.Default_Port}/pubsub/unsubscribe/topic/{topic_name}'
        auth = ('demo', 'demo')

        response = requests.post(url, auth=auth)

        try:
            response_data = response.json()
        except Exception:
            logger.warning(f'Could not load response from `{response.text}`: {format_exc()}')
            raise

        self.assertEqual(response.status_code, 200, f'Full response: {response_data}')
        self.assertEqual(response_data['status'], '200 OK', f'Full response: {response_data}')
        self.assertTrue(response_data['is_ok'], f'Full response: {response_data}')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
