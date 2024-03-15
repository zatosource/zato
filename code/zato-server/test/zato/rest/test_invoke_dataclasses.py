# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
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

    def setUp(self) -> None:
        super().setUp()
        self.rest_client.init()

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

    def test_invoke_helpers_api_account_list_with_user_id(self) -> 'None':

        # Test data
        user_id    = 999
        account_id = 5555

        # Prepare our request ..
        request = {
            'user_id':    user_id,
            'account_id': account_id,
        }

        # .. invoke the helper service ..
        response = self.get('/zato/api/invoke/helpers.api-spec.account-list', request)

        # .. and check the response.
        user_account_list = response['user_account_list']
        account1 = user_account_list[0]
        account2 = user_account_list[1]

        self.assertDictEqual(account1, {
            'user': {'user_id': 222, 'username': 'username.222', 'display_name': 'display_name.222.999'},
            'account_id': 7575,
            'account_type': 2222
        })

        self.assertDictEqual(account2, {
            'user': {'user_id': 111, 'username': 'username.111', 'display_name': 'display_name.111.999'},
            'account_id': 6565,
            'account_type': 1111
        })

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
