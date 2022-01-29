# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import basicConfig, getLogger, DEBUG
from unittest import main

# Zato
from zato.common.test.config import TestConfig
from zato.common.test.rest_client import RESTClientTestCase

# ################################################################################################################################
# ################################################################################################################################

basicConfig(level=DEBUG, format='%(asctime)s - %(message)s')
logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Config:
    SchedulerAddress = '127.0.0.1:31530{}'

# ################################################################################################################################
# ################################################################################################################################

class SchedulerBrokerClientTestCase(RESTClientTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.rest_client.base_address = TestConfig.scheduler_address

# ################################################################################################################################

    def test_server_to_scheduler(self):

        # This will check whether the scheduler replies with the expected metadata
        _ = self.post('/')

# ################################################################################################################################

    def test_server_to_scheduler_invalid_request(self):

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
