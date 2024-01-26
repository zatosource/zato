# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# This comes first
from gevent.monkey import patch_all
patch_all()

# stdlib
import os
from unittest import main, TestCase

# Zato
from zato.common.oauth import OAuthTokenClient, OAuthStore
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dictnone, stranydict

# ################################################################################################################################
# ################################################################################################################################

class _BaseTestCase(TestCase):

    def setUp(self) -> 'None':

        self.zato_test_config = {}

        username = os.environ.get('Zato_Test_OAuth_Username')
        if not username:
            return

        secret = os.environ.get('Zato_Test_OAuth_Secret')
        auth_server_url = os.environ.get('Zato_Test_OAuth_Auth_Server_URL')
        scopes = os.environ.get('Zato_Test_OAuth_Scopes')

        self.zato_test_config['conn_name'] = 'OAuthTokenClientTestCase'
        self.zato_test_config['username'] = username
        self.zato_test_config['secret'] = secret
        self.zato_test_config['auth_server_url'] = auth_server_url
        self.zato_test_config['scopes'] = scopes

# ################################################################################################################################

    def run_common_token_assertions(self, token:'dictnone') -> 'None':

        token = cast_('stranydict', token)

        self.assertEqual(token['token_type'], 'Bearer')
        self.assertEqual(token['expires_in'], 3600)
        self.assertEqual(token['scope'], self.zato_test_config['scopes'])

        self.assertIsInstance(token['access_token'], str)
        self.assertGreaterEqual(len(token['access_token']), 50)

# ################################################################################################################################
# ################################################################################################################################

class OAuthTokenClientTestCase(_BaseTestCase):

    def test_client_obtain_token_from_remote_auth_server(self) -> 'None':

        if not self.zato_test_config:
            return

        client = OAuthTokenClient(**self.zato_test_config)
        token = client.obtain_token()

        self.run_common_token_assertions(token)

# ################################################################################################################################
# ################################################################################################################################

class OAuthStoreTestCase(_BaseTestCase):

    def test_get_with_set(self) -> 'None':

        # This value can be any integer
        item_id = 123

        if not self.zato_test_config:
            return

        def get_config(ignored_item_id:'any_') -> 'stranydict':
            return self.zato_test_config

        max_obtain_iters = 1
        obtain_sleep_time = 0

        store = OAuthStore(get_config, OAuthTokenClient.obtain_from_config, max_obtain_iters, obtain_sleep_time)
        store.create(item_id)
        item = store.get(item_id)

        self.run_common_token_assertions(item.data)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
