# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main

# Zato
from zato.common.test.config import TestConfig
from zato.common.test.rest_client import RESTClientTestCase

TestConfig = TestConfig

# ################################################################################################################################
# ################################################################################################################################

class InvocationTestCase(RESTClientTestCase):

    def test_invoke_get_user(self):
        request = {
            'user_id': 123,
        }

        response = self.get('/zato/invoke/zato.pub.ping', request, expect_ok=False)

        print(111, response)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
