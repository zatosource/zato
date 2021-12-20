# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main

# Zato
from zato.common.api import ZATO_OK
from zato.common.test.rest_client import RESTClientTestCase

# ################################################################################################################################
# ################################################################################################################################

class InvocationTestCase(RESTClientTestCase):

    needs_bunch = False
    needs_current_app = False
    payload_only_messages = False

# ################################################################################################################################

    def test_invoke_helpers_api_spec_user(self) -> 'None':

        # Prepare our request ..
        request = {
            'username': 'my.username'
        }

        # .. invoke the helper service ..
        response = self.get('/zato/api/invoke/helpers.api-spec.user', request)

        # .. and check the response.
        print(111, response)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
