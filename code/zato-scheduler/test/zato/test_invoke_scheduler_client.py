# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.test.config import TestConfig
from zato.common.test.rest_client import RESTClientTestCase

# ################################################################################################################################
# ################################################################################################################################

class InvokeSchedulerClientTestCase(TestCase):

# ################################################################################################################################

    def test_client_invoke_server_to_scheduler(self):

        # This will check whether the scheduler replies with the expected metadata
        #_ = self.post('/')
        pass

# ################################################################################################################################

    def xtest_client_invoke_server_to_scheduler_invalid_request(self):

        # This will check whether the scheduler replies with the expected metadata
        response = self.post('/', {'invalid-key':'invalid-value'}, expect_ok=False)

        cid = response['cid'] # type: str

        self.assertTrue(cid.startswith('zsch'))
        self.assertGreaterEqual(len(cid), 20)
        self.assertEqual(response['status'], 'error')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
