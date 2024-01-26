# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main

# Zato
from zato.common.test.config import TestConfig
from zato.common.test.rest_client import RESTClientTestCase

# ################################################################################################################################
# ################################################################################################################################

class InvokeSchedulerRESTTestCase(RESTClientTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.rest_client.base_address = TestConfig.scheduler_address

# ################################################################################################################################

    def test_rest_invoke_server_to_scheduler(self):

        # This will check whether the scheduler replies with the expected metadata
        _ = self.post('/')

# ################################################################################################################################

    def test_rest_invoke_server_to_scheduler_invalid_request(self):

        # This will check whether the scheduler replies with the expected metadata
        response = self.post('/', {'invalid-key':'invalid-value'}, expect_ok=False)

        cid = response['cid'] # type: str

        self.assertTrue(cid.startswith('zsch'))
        self.assertGreaterEqual(len(cid), 20)
        self.assertEqual(response['status'], 'error')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
