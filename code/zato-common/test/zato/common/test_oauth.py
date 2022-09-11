# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from unittest import main, TestCase

# Zato
from zato.common.oauth import OAuthTokenClient
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

class _BaseTestCase(TestCase):

    def setUp(self):

        self.test_config = {}

        username = os.environ.get('Zato_Test_OAuth_Username')
        if not username:
            return

        secret = os.environ.get('Zato_Test_OAuth_Secret')
        auth_server_url = os.environ.get('Zato_Test_OAuth_Auth_Server_URL')
        scopes = os.environ.get('Zato_Test_OAuth_Scopes')

        self.test_config['conn_name'] = 'OAuthTokenClientTestCase'
        self.test_config['username'] = username
        self.test_config['secret'] = secret
        self.test_config['auth_server_url'] = auth_server_url
        self.test_config['scopes'] = scopes

# ################################################################################################################################
# ################################################################################################################################

class OAuthTokenClientTestCase(_BaseTestCase):

    def xtest_obtain_token(self):

        if not self.test_config:
            return

        client = OAuthTokenClient(**self.test_config)
        token = cast_('stranydict', client.obtain_token())

        self.assertEqual(token['token_type'], 'Bearer')
        self.assertEqual(token['expires_in'], 3600)
        self.assertEqual(token['scope'], self.test_config['scopes'])

        self.assertIsInstance(token['access_token'], str)
        self.assertGreaterEqual(len(token['access_token']), 50)

# ################################################################################################################################
# ################################################################################################################################

class OAuthStoreTestCase(_BaseTestCase):

    def test_get_with_set(self):

        if not self.test_config:
            return

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
