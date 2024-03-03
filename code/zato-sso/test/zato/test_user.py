# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from unittest import main

# Zato
from base import BaseTest
from zato.common.test.config import TestConfig
from zato.sso import const, status_code

# ################################################################################################################################
# ################################################################################################################################

class UserCreateTestCase(BaseTest):

    def test_user_create(self):

        now = datetime.utcnow()
        username = self._get_random_username()

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': username,
            'email': 'myemail@example.com',
            'is_rate_limit_active': True,
            'rate_limit_def': '*=1/d',
        })

        self.assertTrue(response.is_approval_needed)
        self._assert_default_user_data(response, now)

# ################################################################################################################################

    def test_user_create_with_auto_approve(self):

        now = datetime.utcnow()
        username = self._get_random_username()

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': username,
            'auto_approve': True
        })

        self.assertFalse(response.is_approval_needed)
        self._assert_default_user_data(response, now, const.approval_status.approved)

# ################################################################################################################################
# ################################################################################################################################

class UserSignupTestCase(BaseTest):

    def test_user_signup(self):
        response = self.post('/zato/sso/user/signup', {
            'username': self._get_random_username(),
            'password': self._get_random_data(),
            'app_list': [TestConfig.current_app]
        })

        self.assertIsNotNone(response.confirm_token)

# ################################################################################################################################
# ################################################################################################################################

class UserConfirmSignupTestCase(BaseTest):

    def test_confirm_signup(self):

        response = self.post('/zato/sso/user/signup', {
            'username': self._get_random_username(),
            'password': self._get_random_data(),
            'app_list': [TestConfig.current_app]
        })

        confirm_token = response.confirm_token

        response = self.patch('/zato/sso/user/signup', {
            'confirm_token': confirm_token,
        })

# ################################################################################################################################
# ################################################################################################################################

class UserSearchTestCase(BaseTest):

    def test_search(self):

        username1 = self._get_random_username()
        username2 = self._get_random_username()

        random_data = self._get_random_data()

        display_name1 = 'display' + random_data
        display_name2 = 'display' + random_data

        email1 = self._get_random_data()
        email2 = self._get_random_data()

        now = datetime.utcnow()

        self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': username1,
            'display_name': display_name1,
            'email': email1,
        })

        self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': username2,
            'display_name': display_name2,
            'email': email2,
        })

        response = self.get('/zato/sso/user/search', {
            'ust': self.ctx.super_user_ust,
            'display_name': random_data,
            'is_name_exact': False,
        })

        self.assertEqual(response.cur_page, 1)
        self.assertEqual(response.num_pages, 1)
        self.assertEqual(response.has_next_page, False)
        self.assertEqual(response.has_prev_page, False)
        self.assertEqual(response.page_size, const.search.page_size)
        self.assertEqual(response.total, 2)
        self.assertEqual(len(response.result), 2)

        user1 = response.result[0]
        self._assert_default_user_data(user1, now)

        user2 = response.result[1]
        self._assert_default_user_data(user2, now)

# ################################################################################################################################
# ################################################################################################################################

class UserApproveTestCase(BaseTest):

    def test_approve(self):

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'current_app': TestConfig.current_app,
            'username': self._get_random_username(),
        })

        user_id = response.user_id

        self.post('/zato/sso/user/approve', {
            'ust': self.ctx.super_user_ust,
            'user_id': user_id
        })

        response = self.get('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'user_id': user_id
        })

        self.assertEqual(response.approval_status, const.approval_status.approved)

# ################################################################################################################################
# ################################################################################################################################

class UserRejectTestCase(BaseTest):

    def test_reject(self):

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': self._get_random_username(),
        })

        user_id = response.user_id

        self.post('/zato/sso/user/reject', {
            'ust': self.ctx.super_user_ust,
            'user_id': user_id
        })

        response = self.get('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'user_id': user_id
        })

        self.assertEqual(response.approval_status, const.approval_status.rejected)

# ################################################################################################################################
# ################################################################################################################################

class UserLoginValidTestCase(BaseTest):

    def test_user_login(self):

        self.patch('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'is_totp_enabled': False,
        })

        response = self.post('/zato/sso/user/login', {
            'username': TestConfig.super_user_name,
            'password': TestConfig.super_user_password,
        })

        self.assertIsNotNone(response.ust)

# ################################################################################################################################
# ################################################################################################################################

class UserLoginInvalidUsernameTestCase(BaseTest):

    def test_user_login_invalid_username(self):

        response = self.post('/zato/sso/user/login', {
            'username': self._get_random_username(),
            'password': TestConfig.super_user_password,
        }, expect_ok=False)

        self.assertEqual(response.status, status_code.error)
        self.assertListEqual(response.sub_status, [status_code.auth.not_allowed])
        self.assertNotIn('ust', response)

# ################################################################################################################################

    def test_user_login_empty_username_string(self):

        response = self.post('/zato/sso/user/login', {
            'username': '',
            'password': TestConfig.super_user_password,
        }, expect_ok=False)

        self.assertEqual(response.status, status_code.error)
        self.assertListEqual(response.sub_status, [status_code.auth.not_allowed])
        self.assertNotIn('ust', response)

# ################################################################################################################################

    def test_user_login_empty_username_none(self):

        response = self.post('/zato/sso/user/login', {
            'username': None,
            'password': TestConfig.super_user_password,
        }, expect_ok=False)

        self.assertEqual(response.status, status_code.error)
        self.assertListEqual(response.sub_status, [status_code.auth.not_allowed])
        self.assertNotIn('ust', response)

# ################################################################################################################################

    def test_user_login_no_username(self):

        response = self.post('/zato/sso/user/login', {
            'password': TestConfig.super_user_password,
        }, expect_ok=False)

        self.assertEqual(response.result, 'Error')
        self.assertEqual(response.details, 'Bad request')
        self.assertIn('cid', response)
        self.assertNotIn('ust', response)

# ################################################################################################################################
# ################################################################################################################################

class UserLoginInvalidPasswordTestCase(BaseTest):

    def test_user_login_invalid_password(self):

        response = self.post('/zato/sso/user/login', {
            'username': TestConfig.super_user_name,
            'password': self._get_random_data(),
        }, expect_ok=False)

        self.assertEqual(response.status, status_code.error)
        self.assertListEqual(response.sub_status, [status_code.auth.not_allowed])
        self.assertNotIn('ust', response)

# ################################################################################################################################

    def test_user_login_empty_password_string(self):

        response = self.post('/zato/sso/user/login', {
            'username': TestConfig.super_user_name,
            'password': '',
        }, expect_ok=False)

        self.assertEqual(response.status, status_code.error)
        self.assertListEqual(response.sub_status, [status_code.auth.not_allowed])
        self.assertNotIn('ust', response)

# ################################################################################################################################

    def test_user_login_empty_username_none(self):

        response = self.post('/zato/sso/user/login', {
            'username': None,
            'password': TestConfig.super_user_password,
        }, expect_ok=False)

        self.assertEqual(response.status, status_code.error)
        self.assertListEqual(response.sub_status, [status_code.auth.not_allowed])
        self.assertNotIn('ust', response)

# ################################################################################################################################

    def test_user_login_no_password(self):

        response = self.post('/zato/sso/user/login', {
            'username': TestConfig.super_user_name,
        }, expect_ok=False)

        self.assertEqual(response.result, 'Error')
        self.assertEqual(response.details, 'Bad request')
        self.assertIn('cid', response)
        self.assertNotIn('ust', response)

# ################################################################################################################################
# ################################################################################################################################

class UserLogoutTestCase(BaseTest):

    def test_user_logout(self):

        self.patch('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'is_totp_enabled': False,
        })

        ust = self.post('/zato/sso/user/login', {
            'username': TestConfig.super_user_name,
            'password': TestConfig.super_user_password,
        }).ust

        self.post('/zato/sso/user/logout', {
            'ust': ust,
        })

# ################################################################################################################################
# ################################################################################################################################

class UserGetTestCase(BaseTest):

    def test_user_get_by_user_id(self):

        username = self._get_random_username()
        password_must_change = True
        display_name = self._get_random_data()
        first_name = self._get_random_data()
        middle_name = self._get_random_data()
        last_name = self._get_random_data()
        email = self._get_random_data()
        is_locked = True
        is_totp_enabled = True
        totp_label = self._get_random_data()
        sign_up_status = const.signup_status.before_confirmation

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': username,
            'password_must_change': password_must_change,
            'display_name': display_name,
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'email': email,
            'is_locked': is_locked,
            'is_totp_enabled': is_totp_enabled,
            'totp_label': totp_label,
            'sign_up_status': sign_up_status,
        })

        user_id = response.user_id

        response = self.get('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'user_id': user_id,
        })

        self.assertEqual(response.status, status_code.ok)
        self.assertEqual(response.username, username)
        self.assertEqual(response.display_name, display_name)
        self.assertEqual(response.first_name, first_name)
        self.assertEqual(response.middle_name, middle_name)
        self.assertEqual(response.last_name, last_name)
        self.assertEqual(response.email, email)
        self.assertEqual(response.sign_up_status, sign_up_status)
        self.assertIs(response.password_must_change, password_must_change)
        self.assertIs(response.is_locked, is_locked)
        self.assertIs(response.is_totp_enabled, is_totp_enabled)
        self.assertEqual(response.totp_label, totp_label)

# ################################################################################################################################

    def test_user_get_by_ust(self):

        now = datetime.utcnow()
        response = self.get('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
        })

        self.assertEqual(response.approval_status, const.approval_status.approved)
        self.assertEqual(response.approval_status_mod_by, 'auto')
        self.assertEqual(response.username, TestConfig.super_user_name)
        self.assertEqual(response.sign_up_status, const.signup_status.final)

        self.assertFalse(response.is_approval_needed)
        self.assertTrue(response.is_super_user)
        self.assertTrue(response.password_is_set)

        self.assertFalse(response.is_internal)
        self.assertFalse(response.is_locked)
        self.assertFalse(response.password_must_change)

        self._assert_user_dates(response, now, True)

# ################################################################################################################################
# ################################################################################################################################

class UserUpdateTestCase(BaseTest):

    def test_user_update_self(self):

        username = self._get_random_username()
        password = self._get_random_data()

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': username,
            'password': password,
        })

        user_id = response.user_id

        response = self.post('/zato/sso/user/approve', {
            'ust': self.ctx.super_user_ust,
            'user_id': user_id
        })

        self.assertEqual(response.status, status_code.ok)

        response = self.post('/zato/sso/user/login', {
            'username': username,
            'password': password
        })

        ust = response.ust

        display_name = self._get_random_data()
        first_name = self._get_random_data()
        middle_name = self._get_random_data()
        last_name = self._get_random_data()
        email = self._get_random_data()

        response = self.patch('/zato/sso/user', {
            'ust': ust,
            'display_name': display_name,
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'email': email,
        })

        response = self.get('/zato/sso/user', {
            'ust': ust,
        })

        invalid = object()

        # This is a regular user so these attributes should not exist
        self.assertIs(response.get('is_active', invalid), invalid)
        self.assertIs(response.get('is_approval_needed', invalid), invalid)
        self.assertIs(response.get('is_internal', invalid), invalid)
        self.assertIs(response.get('is_locked', invalid), invalid)
        self.assertIs(response.get('is_super_user', invalid), invalid)

        self.assertEqual(response.display_name, display_name)
        self.assertEqual(response.email, email)
        self.assertEqual(response.first_name, first_name)
        self.assertEqual(response.last_name, last_name)
        self.assertEqual(response.middle_name, middle_name)
        self.assertEqual(response.username, username)

# ################################################################################################################################

    def test_user_update_self_username(self):

        # Test data
        username1 = self._get_random_username()
        password1 = self._get_random_data()

        username2 = self._get_random_username()
        password2 = self._get_random_data()

        new_username = self._get_random_username()

        # Create test users
        self._create_and_approve_user(username1, password1)
        self._create_and_approve_user(username2, password2)

        # Log in the first user
        response1 = self.post('/zato/sso/user/login', {
            'username': username1,
            'password': password1
        })

        # The first user should be able to set the new user name
        response = self.patch('/zato/sso/user', {
            'ust': response1.ust,
            'username': new_username,
        })

        self.assertEqual(response.status, status_code.ok)

        # Log in the second user
        response2 = self.post('/zato/sso/user/login', {
            'username': username2,
            'password': password2
        })

        # The second user should be able to use the same username as the first one has already used
        patch_response2 = self.patch('/zato/sso/user', {
            'ust': response2.ust,
            'username': new_username,
        }, expect_ok=False)

        self.assertEqual(patch_response2.status, status_code.error)
        self.assertEqual(patch_response2.sub_status, [status_code.username.exists])

# ################################################################################################################################

    def test_user_update_by_id(self):

        username = self._get_random_username()
        password = self._get_random_data()

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': username,
            'password': password,
        })

        user_id = response.user_id

        display_name = self._get_random_data()
        first_name = self._get_random_data()
        middle_name = self._get_random_data()
        last_name = self._get_random_data()
        email = self._get_random_data()

        is_approved = True
        is_locked = True
        password_expiry = '2345-12-27T11:22:33'
        password_must_change = True
        sign_up_status = const.signup_status.final
        approval_status = const.approval_status.rejected

        response = self.patch('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'user_id': user_id,
            'display_name': display_name,
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'email': email,
            'is_approved': is_approved,
            'is_locked': is_locked,
            'password_expiry': password_expiry,
            'password_must_change': password_must_change,
            'sign_up_status': sign_up_status,
            'approval_status': approval_status,
        })

        response = self.get('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'user_id': user_id,
        })

        self.assertEqual(response.user_id, user_id)
        self.assertEqual(response.display_name, display_name)
        self.assertEqual(response.email, email)
        self.assertEqual(response.first_name, first_name)
        self.assertEqual(response.last_name, last_name)
        self.assertEqual(response.middle_name, middle_name)
        self.assertEqual(response.username, username)

        self.assertEqual(response.is_locked, is_locked)
        self.assertEqual(response.password_expiry, password_expiry)
        self.assertEqual(response.password_must_change, password_must_change)
        self.assertEqual(response.sign_up_status, sign_up_status)
        self.assertEqual(response.approval_status, approval_status)

# ################################################################################################################################
# ################################################################################################################################

class UserDeleteTestCase(BaseTest):

    def test_user_delete_by_super_user(self):

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': self._get_random_username(),
        })

        user_id = response.user_id

        response = self.get('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'user_id': user_id,
        })

        self.assertEqual(response.status, status_code.ok)

        response = self.delete('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'user_id': user_id,
        })

        self.assertEqual(response.status, status_code.ok)

        response = self.get('/zato/sso/user/search', {
            'ust': self.ctx.super_user_ust,
            'user_id': user_id,
        })

        self.assertEqual(response.total, 0)

# ################################################################################################################################

    def test_user_delete_by_regular_user(self):

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': self._get_random_username(),
        })

        self.assertEqual(response.status, status_code.ok)
        user_id1 = response.user_id

        response = self.get('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'user_id': user_id1,
        })

        username = self._get_random_username()
        password = self._get_random_data()

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': username,
            'password': password,
        })

        user_id2 = response.user_id

        self.post('/zato/sso/user/approve', {
            'ust': self.ctx.super_user_ust,
            'user_id': user_id1
        })

        self.post('/zato/sso/user/approve', {
            'ust': self.ctx.super_user_ust,
            'user_id': user_id2
        })

        response = self.post('/zato/sso/user/login', {
            'username': username,
            'password': password,
        })

        ust = response.ust

        response = self.delete('/zato/sso/user', {
            'ust': ust,
            'user_id': user_id1,
        }, False)

        self.assertEqual(response.status, status_code.error)
        self.assertListEqual(response.sub_status, [status_code.auth.not_allowed])

# ################################################################################################################################
# ################################################################################################################################

class UserChangePasswordTestCase(BaseTest):

    def test_user_change_password_self(self):

        username = self._get_random_username()
        password = self._get_random_data()

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': username,
            'password': password,
        })

        user_id = response.user_id

        self.post('/zato/sso/user/approve', {
            'ust': self.ctx.super_user_ust,
            'user_id': user_id
        })

        response = self.post('/zato/sso/user/login', {
            'username': username,
            'password': password,
        })

        self.assertIsNotNone(response.ust)

        ust = response.ust
        new_pasword = self._get_random_data()

        response = self.patch('/zato/sso/user/password', {
            'ust': ust,
            'user_id': user_id,
            'old_password': password,
            'new_password': new_pasword
        })

        response = self.post('/zato/sso/user/login', {
            'username': username,
            'password': password,
        }, False)

        self.assertEqual(response.status, status_code.error)
        self.assertListEqual(response.sub_status, [status_code.auth.not_allowed])

        response = self.post('/zato/sso/user/login', {
            'username': username,
            'password': new_pasword,
        })

        self.assertEqual(response.status, status_code.ok)
        self.assertIsNotNone(response.ust)

# ################################################################################################################################

    def test_user_change_password_super_user(self):

        username = self._get_random_username()
        password = self._get_random_data()

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': username,
            'password': password,
        })

        user_id = response.user_id

        self.post('/zato/sso/user/approve', {
            'ust': self.ctx.super_user_ust,
            'user_id': user_id
        })

        response = self.post('/zato/sso/user/login', {
            'username': username,
            'password': password,
        })

        self.assertIsNotNone(response.ust)

        new_pasword = self._get_random_data()
        password_expiry = 1
        must_change = True

        response = self.patch('/zato/sso/user/password', {
            'ust': self.ctx.super_user_ust,
            'user_id': user_id,
            'old_password': password,
            'new_password': new_pasword,
            'password_expiry': password_expiry,
            'password_must_change': must_change,
        })

        response = self.post('/zato/sso/user/login', {
            'username': username,
            'password': password,
        }, False)

        self.assertEqual(response.status, status_code.error)
        self.assertListEqual(response.sub_status, [status_code.auth.not_allowed])

        response = self.post('/zato/sso/user/login', {
            'username': username,
            'password': new_pasword,
        }, False)

        self.assertEqual(response.status, status_code.warning)
        self.assertListEqual(response.sub_status, [status_code.password.w_about_to_exp])
        self.assertIsNotNone(response.ust)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
