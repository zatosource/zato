# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main

# Zato
from zato.common.api import ZATO_OK
from zato.common.test.rest_client import RESTClientTestCase

# ################################################################################################################################
# ################################################################################################################################

class PingTestCase(RESTClientTestCase):

    needs_bunch           = False
    needs_current_app     = False
    payload_only_messages = False

    def test_invoke_ping(self) -> 'None':

        # Invoke the default ping service ..
        response = self.get('/zato/ping')

        # .. and check all the detail.
        self.assertEqual(response['pong'], 'zato')
        self.assertEqual(response['zato_env']['result'],  ZATO_OK)
        self.assertEqual(response['zato_env']['details'], '')

        len_cid = len(response['zato_env']['cid'])
        self.assertTrue(len_cid >= 23) # We cannot be certain but it should be at least 23 characters of random data

# ################################################################################################################################
# ################################################################################################################################

class APIInvokeTestCase(RESTClientTestCase):

    needs_bunch           = False
    needs_current_app     = False
    payload_only_messages = False

    def setUp(self) -> None:
        super().setUp()
        self.rest_client.init()

    def test_api_invoke(self):
        response = self.rest_client.api_invoke('pub.zato.ping')
        self.assertDictEqual({'pong':'zato'}, response)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
