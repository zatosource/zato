# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# requests
import requests

# Zato
from zato.common.api import REST_Server

# ################################################################################################################################
# ################################################################################################################################

class TestUnsubscribe(unittest.TestCase):

    def test_unsubscribe_success(self):
        topic_name = 'test.topic'
        sub_key = 'test-sub-key'

        url = f'http://localhost:{REST_Server.Default_Port}/unsubscribe/{topic_name}'
        auth = ('demo', 'demo')

        response = requests.post(url, auth=auth, json={'sub_key': sub_key})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

# ################################################################################################################################
# ################################################################################################################################
