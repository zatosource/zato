# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

"""
Python integration tests for the Rust-side check_basic_auth and check_apikey
methods, exercised through PyO3. These serve as contract tests - they define
the observable behavior from Python's side and must continue to pass unchanged
when broker handler logic migrates to Rust.
"""

# stdlib
import unittest

# Zato
from zato_server_core import ConfigStore

# ################################################################################################################################
# ################################################################################################################################

class TestCheckBasicAuth(unittest.TestCase):

    def setUp(self):
        self.cs = ConfigStore()

    def _set_ba(self, name, username, password, realm=''):
        self.cs.set('security', name, {
            'type': 'basic_auth',
            'name': name,
            'username': username,
            'password': password,
            'realm': realm,
        })

    def test_correct_credentials_return_id(self):
        self._set_ba('ba1', 'admin', 'secret')
        result = self.cs.check_basic_auth('admin', 'secret')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_wrong_password_returns_none(self):
        self._set_ba('ba1', 'admin', 'secret')
        self.assertIsNone(self.cs.check_basic_auth('admin', 'wrong'))

    def test_wrong_username_returns_none(self):
        self._set_ba('ba1', 'admin', 'secret')
        self.assertIsNone(self.cs.check_basic_auth('nobody', 'secret'))

    def test_nonexistent_user_returns_none(self):
        self.assertIsNone(self.cs.check_basic_auth('ghost', 'pass'))

    def test_empty_password_matches(self):
        self._set_ba('ba1', 'admin', '')
        result = self.cs.check_basic_auth('admin', '')
        self.assertIsNotNone(result)

    def test_password_edit_takes_effect_immediately(self):
        self._set_ba('ba1', 'admin', 'old-pass')
        self.assertIsNotNone(self.cs.check_basic_auth('admin', 'old-pass'))

        self._set_ba('ba1', 'admin', 'new-pass')
        self.assertIsNone(self.cs.check_basic_auth('admin', 'old-pass'))
        self.assertIsNotNone(self.cs.check_basic_auth('admin', 'new-pass'))

    def test_username_edit_takes_effect_immediately(self):
        self._set_ba('ba1', 'old-user', 'pass')
        self.assertIsNotNone(self.cs.check_basic_auth('old-user', 'pass'))

        self._set_ba('ba1', 'new-user', 'pass')
        self.assertIsNone(self.cs.check_basic_auth('old-user', 'pass'))
        self.assertIsNotNone(self.cs.check_basic_auth('new-user', 'pass'))

    def test_delete_removes_credentials(self):
        self._set_ba('ba1', 'admin', 'pass')
        self.assertIsNotNone(self.cs.check_basic_auth('admin', 'pass'))

        self.cs.delete('security', 'ba1')
        self.assertIsNone(self.cs.check_basic_auth('admin', 'pass'))

    def test_multiple_basic_auth_defs(self):
        self._set_ba('ba1', 'user1', 'pass1')
        self._set_ba('ba2', 'user2', 'pass2')

        self.assertIsNotNone(self.cs.check_basic_auth('user1', 'pass1'))
        self.assertIsNotNone(self.cs.check_basic_auth('user2', 'pass2'))
        self.assertIsNone(self.cs.check_basic_auth('user1', 'pass2'))

    def test_unicode_credentials(self):
        self._set_ba('ba1', 'użytkownik', 'hasło')
        self.assertIsNotNone(self.cs.check_basic_auth('użytkownik', 'hasło'))
        self.assertIsNone(self.cs.check_basic_auth('użytkownik', 'wrong'))

    def test_returned_id_matches_get(self):
        self._set_ba('ba1', 'admin', 'secret')
        check_id = self.cs.check_basic_auth('admin', 'secret')
        item = self.cs.get('security', 'ba1')
        self.assertEqual(check_id, item['id'])

# ################################################################################################################################
# ################################################################################################################################

class TestCheckApiKey(unittest.TestCase):

    def setUp(self):
        self.cs = ConfigStore()

    def _set_ak(self, name, key_value, username=''):
        self.cs.set('security', name, {
            'type': 'apikey',
            'name': name,
            'username': username,
            'password': key_value,
        })

    def test_correct_key_returns_id(self):
        self._set_ak('ak1', 'my-secret-key')
        result = self.cs.check_apikey('my-secret-key')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)

    def test_wrong_key_returns_none(self):
        self._set_ak('ak1', 'my-secret-key')
        self.assertIsNone(self.cs.check_apikey('wrong-key'))

    def test_nonexistent_key_returns_none(self):
        self.assertIsNone(self.cs.check_apikey('anything'))

    def test_key_edit_takes_effect_immediately(self):
        self._set_ak('ak1', 'old-key')
        self.assertIsNotNone(self.cs.check_apikey('old-key'))

        self._set_ak('ak1', 'new-key')
        self.assertIsNone(self.cs.check_apikey('old-key'))
        self.assertIsNotNone(self.cs.check_apikey('new-key'))

    def test_delete_removes_key(self):
        self._set_ak('ak1', 'my-key')
        self.assertIsNotNone(self.cs.check_apikey('my-key'))

        self.cs.delete('security', 'ak1')
        self.assertIsNone(self.cs.check_apikey('my-key'))

    def test_multiple_apikey_defs(self):
        self._set_ak('ak1', 'key-1')
        self._set_ak('ak2', 'key-2')

        self.assertIsNotNone(self.cs.check_apikey('key-1'))
        self.assertIsNotNone(self.cs.check_apikey('key-2'))
        self.assertIsNone(self.cs.check_apikey('key-3'))

    def test_returned_id_matches_get(self):
        self._set_ak('ak1', 'my-key')
        check_id = self.cs.check_apikey('my-key')
        item = self.cs.get('security', 'ak1')
        self.assertEqual(check_id, item['id'])

# ################################################################################################################################
# ################################################################################################################################

class TestMixedSecurityTypes(unittest.TestCase):
    """Verify basic_auth and apikey indexes don't interfere with each other."""

    def setUp(self):
        self.cs = ConfigStore()

    def test_basic_auth_and_apikey_independent(self):
        self.cs.set('security', 'ba1', {
            'type': 'basic_auth', 'name': 'ba1', 'username': 'admin', 'password': 'pass',
        })
        self.cs.set('security', 'ak1', {
            'type': 'apikey', 'name': 'ak1', 'username': '', 'password': 'the-key',
        })

        self.assertIsNotNone(self.cs.check_basic_auth('admin', 'pass'))
        self.assertIsNotNone(self.cs.check_apikey('the-key'))

        # Cross-check: basic auth password should not match as API key
        self.assertIsNone(self.cs.check_apikey('pass'))
        # Cross-check: API key should not match as basic auth password
        self.assertIsNone(self.cs.check_basic_auth('the-key', 'anything'))

    def test_ntlm_does_not_affect_indexes(self):
        self.cs.set('security', 'nt1', {
            'type': 'ntlm', 'name': 'nt1', 'username': 'domain\\user', 'password': 'ntpass',
        })
        self.assertIsNone(self.cs.check_basic_auth('domain\\user', 'ntpass'))
        self.assertIsNone(self.cs.check_apikey('ntpass'))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    unittest.main()
