# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main

# Zato
from zato.common.test.rest_client import RESTClientTestCase

# ################################################################################################################################
# ################################################################################################################################

class InvocationTestCase(RESTClientTestCase):

    needs_bunch = False
    needs_current_app = False
    payload_only_messages = False

# ################################################################################################################################

    def test_invoke_helpers_api_spec_user(self) -> 'None':

        # Test data
        username = 'my.username'

        # Prepare our request ..
        request = {
            'username': username
        }

        # .. invoke the helper service ..
        response = self.get('/zato/api/invoke/helpers.api-spec.user', request)

        # .. and check the response.
        user          = response['user']
        parent_user   = response['parent_user']
        previous_user = response['previous_user']

        self.assertListEqual(user, [
            {'user_id': 222, 'username': 'username.222', 'display_name': 'display_name.222.' + username},
            {'user_id': 111, 'username': 'username.111', 'display_name': 'display_name.111.' + username}
        ])

        self.assertListEqual(parent_user,   [])
        self.assertListEqual(previous_user, [])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
