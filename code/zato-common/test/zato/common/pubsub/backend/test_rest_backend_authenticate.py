# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import warnings
from base64 import b64encode
from unittest import main, TestCase

# Zato
from zato.common.pubsub.server.rest_base import BaseRESTServer, UnauthorizedException
from zato.broker.client import BrokerClient

# ################################################################################################################################
# ################################################################################################################################

class RESTBackendAuthenticateTestCase(TestCase):

    def setUp(self):

        # Suppress ResourceWarnings from gevent
        warnings.filterwarnings('ignore', category=ResourceWarning)

        self.broker_client = BrokerClient()
        self.rest_server = BaseRESTServer('localhost', 8080)

        # Test data constants
        self.test_cid = 'test-cid-123'
        self.test_username = 'test_user'
        self.test_password = 'secure_password_123'

        self.invalid_username = 'invalid_user'
        self.invalid_password = 'invalid_password'

        self.empty_username = ''
        self.empty_password = ''

        self.special_chars_username = 'user@domain.com'
        self.special_chars_password = 'password!@#$%'

        self.unicode_username = 'unicode_user_ñ'
        self.unicode_password = 'password_ü123'

        self.long_username = 'a' * 100
        self.long_password = 'b' * 200

        # Add test users to server
        self.rest_server.users[self.test_username] = {'sec_name': 'test_sec_def', 'password': self.test_password}
        self.rest_server.users[self.special_chars_username] = {'sec_name': 'special_sec_def', 'password': self.special_chars_password}
        self.rest_server.users[self.unicode_username] = {'sec_name': 'unicode_sec_def', 'password': self.unicode_password}
        self.rest_server.users[self.long_username] = {'sec_name': 'long_sec_def', 'password': self.long_password}

    def _create_basic_auth_header(self, username, password):
        """Helper method to create Basic Auth header"""
        credentials = f'{username}:{password}'
        encoded_credentials = b64encode(credentials.encode('utf-8')).decode('ascii')
        return f'Basic {encoded_credentials}'

    def _create_environ(self, auth_header=None, path_info='/test'):
        """Helper method to create WSGI environ dict"""
        environ = {
            'PATH_INFO': path_info,
            'REQUEST_METHOD': 'GET'
        }
        if auth_header:
            environ['HTTP_AUTHORIZATION'] = auth_header
        return environ

# ################################################################################################################################

    def test_authenticate_with_valid_credentials(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)
        environ = self._create_environ(auth_header)

        # Call the method under test
        result = self.rest_server.authenticate(self.test_cid, environ)

        # Assert authentication succeeded
        self.assertEqual(result, self.test_username)

# ################################################################################################################################

    def test_authenticate_with_invalid_username(self):

        # Create auth header with invalid username
        auth_header = self._create_basic_auth_header(self.invalid_username, self.test_password)
        environ = self._create_environ(auth_header)

        # Call the method under test and expect exception
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.authenticate(self.test_cid, environ)

        # Assert exception contains correct CID
        self.assertEqual(cm.exception.cid, self.test_cid)

# ################################################################################################################################

    def test_authenticate_with_invalid_password(self):

        # Create auth header with invalid password
        auth_header = self._create_basic_auth_header(self.test_username, self.invalid_password)
        environ = self._create_environ(auth_header)

        # Call the method under test and expect exception
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.authenticate(self.test_cid, environ)

        # Assert exception contains correct CID
        self.assertEqual(cm.exception.cid, self.test_cid)

# ################################################################################################################################

    def test_authenticate_with_no_authorization_header(self):

        # Create environ without auth header
        environ = self._create_environ()

        # Call the method under test and expect exception
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.authenticate(self.test_cid, environ)

        # Assert exception contains correct CID
        self.assertEqual(cm.exception.cid, self.test_cid)

# ################################################################################################################################

    def test_authenticate_with_empty_authorization_header(self):

        # Create environ with empty auth header
        environ = self._create_environ('')

        # Call the method under test and expect exception
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.authenticate(self.test_cid, environ)

        # Assert exception contains correct CID
        self.assertEqual(cm.exception.cid, self.test_cid)

# ################################################################################################################################

    def test_authenticate_with_malformed_authorization_header(self):

        # Create environ with malformed auth header
        environ = self._create_environ('NotBasic invalid_header')

        # Call the method under test and expect exception
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.authenticate(self.test_cid, environ)

        # Assert exception contains correct CID
        self.assertEqual(cm.exception.cid, self.test_cid)

# ################################################################################################################################

    def test_authenticate_with_empty_username(self):

        # Create auth header with empty username
        auth_header = self._create_basic_auth_header(self.empty_username, self.test_password)
        environ = self._create_environ(auth_header)

        # Call the method under test and expect exception
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.authenticate(self.test_cid, environ)

        # Assert exception contains correct CID
        self.assertEqual(cm.exception.cid, self.test_cid)

# ################################################################################################################################

    def test_authenticate_with_empty_password(self):

        # Add user with empty password
        empty_password_user = 'empty_password_user'
        self.rest_server.users[empty_password_user] = {'sec_name': 'empty_sec_def', 'password': self.empty_password}

        # Create auth header with empty password
        auth_header = self._create_basic_auth_header(empty_password_user, self.empty_password)
        environ = self._create_environ(auth_header)

        # Call the method under test
        result = self.rest_server.authenticate(self.test_cid, environ)

        # Assert authentication succeeded
        self.assertEqual(result, empty_password_user)

# ################################################################################################################################

    def test_authenticate_with_special_characters_in_credentials(self):

        # Create auth header with special characters
        auth_header = self._create_basic_auth_header(self.special_chars_username, self.special_chars_password)
        environ = self._create_environ(auth_header)

        # Call the method under test
        result = self.rest_server.authenticate(self.test_cid, environ)

        # Assert authentication succeeded
        self.assertEqual(result, self.special_chars_username)

# ################################################################################################################################

    def test_authenticate_with_unicode_characters(self):

        # Create auth header with unicode characters
        auth_header = self._create_basic_auth_header(self.unicode_username, self.unicode_password)
        environ = self._create_environ(auth_header)

        # Call the method under test
        result = self.rest_server.authenticate(self.test_cid, environ)

        # Assert authentication succeeded
        self.assertEqual(result, self.unicode_username)

# ################################################################################################################################

    def test_authenticate_with_long_credentials(self):

        # Create auth header with long credentials
        auth_header = self._create_basic_auth_header(self.long_username, self.long_password)
        environ = self._create_environ(auth_header)

        # Call the method under test
        result = self.rest_server.authenticate(self.test_cid, environ)

        # Assert authentication succeeded
        self.assertEqual(result, self.long_username)

# ################################################################################################################################

    def test_authenticate_with_colon_in_password(self):

        # Add user with colon in password
        colon_password_user = 'colon_password_user'
        colon_password = 'password:with:colons'
        self.rest_server.users[colon_password_user] = {'sec_name': 'colon_sec_def', 'password': colon_password}

        # Create auth header with colon in password
        auth_header = self._create_basic_auth_header(colon_password_user, colon_password)
        environ = self._create_environ(auth_header)

        # Call the method under test
        result = self.rest_server.authenticate(self.test_cid, environ)

        # Assert authentication succeeded
        self.assertEqual(result, colon_password_user)

# ################################################################################################################################

    def test_authenticate_with_different_path_info(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)
        environ = self._create_environ(auth_header, '/different/path')

        # Call the method under test
        result = self.rest_server.authenticate(self.test_cid, environ)

        # Assert authentication succeeded regardless of path
        self.assertEqual(result, self.test_username)

# ################################################################################################################################

    def test_authenticate_case_sensitive_username(self):

        # Create auth header with different case username
        auth_header = self._create_basic_auth_header(self.test_username.upper(), self.test_password)
        environ = self._create_environ(auth_header)

        # Call the method under test and expect exception (case sensitive)
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.authenticate(self.test_cid, environ)

        # Assert exception contains correct CID
        self.assertEqual(cm.exception.cid, self.test_cid)

# ################################################################################################################################

    def test_authenticate_case_sensitive_password(self):

        # Create auth header with different case password
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password.upper())
        environ = self._create_environ(auth_header)

        # Call the method under test and expect exception (case sensitive)
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.authenticate(self.test_cid, environ)

        # Assert exception contains correct CID
        self.assertEqual(cm.exception.cid, self.test_cid)

# ################################################################################################################################

    def test_authenticate_multiple_calls_same_credentials(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)
        environ = self._create_environ(auth_header)

        # Call the method multiple times
        result1 = self.rest_server.authenticate(self.test_cid, environ)
        result2 = self.rest_server.authenticate(self.test_cid, environ)
        result3 = self.rest_server.authenticate(self.test_cid, environ)

        # Assert all calls succeeded with same result
        self.assertEqual(result1, self.test_username)
        self.assertEqual(result2, self.test_username)
        self.assertEqual(result3, self.test_username)

# ################################################################################################################################

    def test_authenticate_with_bearer_token_header(self):

        # Create environ with Bearer token instead of Basic auth
        environ = self._create_environ('Bearer some_token_value')

        # Call the method under test and expect exception
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.authenticate(self.test_cid, environ)

        # Assert exception contains correct CID
        self.assertEqual(cm.exception.cid, self.test_cid)

# ################################################################################################################################

    def test_authenticate_preserves_users_dict(self):

        # Store initial users dict
        initial_users = dict(self.rest_server.users)

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)
        environ = self._create_environ(auth_header)

        # Call the method under test
        result = self.rest_server.authenticate(self.test_cid, environ)

        # Assert users dict was not modified
        self.assertEqual(self.rest_server.users, initial_users)
        self.assertEqual(result, self.test_username)

# ################################################################################################################################

    def test_authenticate_after_password_change(self):

        # Create user with initial password
        initial_password = 'initial_password_123'
        self.rest_server.users[self.test_username] = {'sec_name': 'test_sec_def', 'password': initial_password}

        # Verify authentication works with initial password
        auth_header = self._create_basic_auth_header(self.test_username, initial_password)
        environ = self._create_environ(auth_header)
        result = self.rest_server.authenticate(self.test_cid, environ)
        self.assertEqual(result, self.test_username)

        # Change password
        new_password = 'new_password_456'
        self.rest_server.users[self.test_username] = {'sec_name': 'test_sec_def', 'password': new_password}

        # Verify old password no longer works
        old_auth_header = self._create_basic_auth_header(self.test_username, initial_password)
        old_environ = self._create_environ(old_auth_header)
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.authenticate(self.test_cid, old_environ)
        self.assertEqual(cm.exception.cid, self.test_cid)

        # Verify new password works
        new_auth_header = self._create_basic_auth_header(self.test_username, new_password)
        new_environ = self._create_environ(new_auth_header)
        result = self.rest_server.authenticate(self.test_cid, new_environ)
        self.assertEqual(result, self.test_username)

# ################################################################################################################################

    def test_authenticate_after_password_change_to_empty(self):

        # Create user with initial password
        initial_password = 'initial_password_123'
        empty_password_user = 'empty_password_change_user'
        self.rest_server.users[empty_password_user] = {'sec_name': 'empty_sec_def', 'password': initial_password}

        # Change password to empty
        self.rest_server.users[empty_password_user] = {'sec_name': 'empty_sec_def', 'password': ''}

        # Verify old password no longer works
        old_auth_header = self._create_basic_auth_header(empty_password_user, initial_password)
        old_environ = self._create_environ(old_auth_header)

        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.authenticate(self.test_cid, old_environ)

        self.assertEqual(cm.exception.cid, self.test_cid)

        # Verify empty password works
        new_auth_header = self._create_basic_auth_header(empty_password_user, '')
        new_environ = self._create_environ(new_auth_header)

        result = self.rest_server.authenticate(self.test_cid, new_environ)
        self.assertEqual(result, empty_password_user)

# ################################################################################################################################

    def test_authenticate_after_multiple_password_changes(self):

        # Create user with initial password
        password_change_user = 'password_change_user'
        password1 = 'password_1'
        password2 = 'password_2'
        password3 = 'password_3'

        self.rest_server.users[password_change_user] = {'sec_name': 'change_sec_def', 'password': password1}

        # Verify first password works
        auth_header1 = self._create_basic_auth_header(password_change_user, password1)
        environ1 = self._create_environ(auth_header1)

        result = self.rest_server.authenticate(self.test_cid, environ1)
        self.assertEqual(result, password_change_user)

        # Change to second password
        self.rest_server.users[password_change_user] = {'sec_name': 'change_sec_def', 'password': password2}

        # Verify second password works and first doesn't
        auth_header2 = self._create_basic_auth_header(password_change_user, password2)
        environ2 = self._create_environ(auth_header2)

        result = self.rest_server.authenticate(self.test_cid, environ2)
        self.assertEqual(result, password_change_user)

        with self.assertRaises(UnauthorizedException):
            _ = self.rest_server.authenticate(self.test_cid, environ1)

        # Change to third password
        self.rest_server.users[password_change_user] = {'sec_name': 'change_sec_def', 'password': password3}

        # Verify third password works and previous don't
        auth_header3 = self._create_basic_auth_header(password_change_user, password3)
        environ3 = self._create_environ(auth_header3)

        result = self.rest_server.authenticate(self.test_cid, environ3)
        self.assertEqual(result, password_change_user)

        with self.assertRaises(UnauthorizedException):
            _ = self.rest_server.authenticate(self.test_cid, environ1)

        with self.assertRaises(UnauthorizedException):
            _ = self.rest_server.authenticate(self.test_cid, environ2)

# ################################################################################################################################

    def test_authenticate_after_password_change_with_special_characters(self):

        # Create user with initial password
        special_change_user = 'special_change_user'
        initial_password = 'simple_password'
        new_password = r'complex!@#$%^&*()_+{}|:<>?[]\;\',./'

        self.rest_server.users[special_change_user] = {'sec_name': 'special_sec_def', 'password': initial_password}

        # Change to password with special characters
        self.rest_server.users[special_change_user] = {'sec_name': 'special_sec_def', 'password': new_password}

        # Verify old password no longer works
        old_auth_header = self._create_basic_auth_header(special_change_user, initial_password)
        old_environ = self._create_environ(old_auth_header)

        with self.assertRaises(UnauthorizedException):
            _ = self.rest_server.authenticate(self.test_cid, old_environ)

        # Verify new password with special characters works
        new_auth_header = self._create_basic_auth_header(special_change_user, new_password)
        new_environ = self._create_environ(new_auth_header)

        result = self.rest_server.authenticate(self.test_cid, new_environ)
        self.assertEqual(result, special_change_user)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
