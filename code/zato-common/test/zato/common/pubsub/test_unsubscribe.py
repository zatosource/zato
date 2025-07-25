# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# requests
import requests

# Zato
from zato.common.api import PubSub

# ################################################################################################################################
# ################################################################################################################################

class TestUnsubscribe(TestCase):

    def test_unsubscribe_success(self):

        topic_name = 'demo.1'

        url = f'http://localhost:{PubSub.REST_Server.Default_Port}/pubsub/unsubscribe/topic/{topic_name}'
        auth = ('demo', 'demo')

        response = requests.post(url, auth=auth)

        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertEqual(response_data['status'], 'success')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
