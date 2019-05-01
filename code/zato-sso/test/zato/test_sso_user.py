# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
import os
from copy import deepcopy
from datetime import datetime
from itertools import count
from json import dumps, loads
from unittest import TestCase, main

# Bunch
from bunch import bunchify

# sh
import sh

# requests
import requests

# Zato
from base import BaseTest
from zato.sso import const, status_code

# ################################################################################################################################

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ################################################################################################################################

current_app = 'CRM'

super_user_name = 'admin1'
super_user_password = 'hQ9nl93UDqGus'

username_prefix = 'test.{}+{}'

server_location = os.path.expanduser('~/env/z31sqlite/server1')
server_address  = 'http://localhost:17010{}'

class NotGiven:
    pass

class Request:

    login = bunchify({
        'username': NotGiven,
        'password': NotGiven,
        'current_app': NotGiven,
    })

# ################################################################################################################################
# ################################################################################################################################

class UserCreateTestCase(BaseTest):

    def xtest_user_create(self):

        now = datetime.utcnow()
        username = self._get_random_username()

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'current_app': current_app,
            'username': username
        })

        self.assertEquals(response.status, status_code.ok)
        self.assertIsNotNone(response.cid)
        self.assertTrue(response.is_approval_needed)
        self._assert_default_user_data(response, now)

# ################################################################################################################################
# ################################################################################################################################

class UserSignupTestCase(BaseTest):
    def xtest_user_signup(self):
        response = self.post('/zato/sso/user/signup', {
            'username': self._get_random_username(),
            'password': self._get_random_data(),
            'current_app': current_app,
            'app_list': [current_app]
        })

        self.assertEquals(response.status, status_code.ok)
        self.assertIsNotNone(response.cid)
        self.assertIsNotNone(response.confirm_token)

# ################################################################################################################################
# ################################################################################################################################

class UserConfirmSignupTestCase(BaseTest):
    def xtest_confirm_signup(self):

        response = self.post('/zato/sso/user/signup', {
            'username': self._get_random_username(),
            'password': self._get_random_data(),
            'current_app': current_app,
            'app_list': [current_app]
        })

        confirm_token = response.confirm_token

        response = self.patch('/zato/sso/user/signup', {
            'confirm_token': confirm_token,
            'current_app': current_app,
        })

        self.assertEquals(response.status, status_code.ok)
        self.assertIsNotNone(response.cid)

# ################################################################################################################################
# ################################################################################################################################

class UserSearchTestCase(BaseTest):
    def xtest_search(self):

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
            'current_app': current_app,
            'username': username1,
            'display_name': display_name1,
            'email': email1,
        })

        self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'current_app': current_app,
            'username': username2,
            'display_name': display_name2,
            'email': email2,
        })

        response = self.get('/zato/sso/user/search', {
            'ust': self.ctx.super_user_ust,
            'current_app': 'CRM',
            'display_name': random_data,
            'is_name_exact': False,
        })

        self.assertEquals(response.status, status_code.ok)
        self.assertEquals(response.cur_page, 1)
        self.assertEquals(response.num_pages, 1)
        self.assertEquals(response.has_next_page, False)
        self.assertEquals(response.has_prev_page, False)
        self.assertEquals(response.page_size, const.search.page_size)
        self.assertEquals(response.total, 2)
        self.assertEquals(len(response.result), 2)

        user1 = response.result[0]
        self._assert_default_user_data(user1, now)

        user2 = response.result[1]
        self._assert_default_user_data(user2, now)

# ################################################################################################################################
# ################################################################################################################################

class UserApproveTestCase(BaseTest):
    def xtest_approve(self):

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'current_app': current_app,
            'username': self._get_random_username(),
        })

        self.assertEquals(response.status, status_code.ok)
        user_id = response.user_id

        self.post('/zato/sso/user/approve', {
            'ust': self.ctx.super_user_ust,
            'current_app': 'CRM',
            'user_id': user_id
        })

        response = self.get('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'current_app': 'CRM',
            'user_id': user_id
        })

        self.assertEquals(response.approval_status, const.approval_status.approved)

# ################################################################################################################################
# ################################################################################################################################

class UserRejectTestCase(BaseTest):
    def xtest_reject(self):

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'current_app': current_app,
            'username': self._get_random_username(),
        })

        self.assertEquals(response.status, status_code.ok)
        user_id = response.user_id

        self.post('/zato/sso/user/reject', {
            'ust': self.ctx.super_user_ust,
            'current_app': 'CRM',
            'user_id': user_id
        })

        response = self.get('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'current_app': 'CRM',
            'user_id': user_id
        })

        self.assertEquals(response.approval_status, const.approval_status.rejected)

# ################################################################################################################################
# ################################################################################################################################

class UserLoginTestCase(BaseTest):

    def xtest_user_login(self):

        response = self.post('/zato/sso/user/login', {
            'current_app': current_app,
            'username': super_user_name,
            'password': super_user_password,
        })

        self.assertEquals(response.status, status_code.ok)
        self.assertIsNotNone(response.cid)
        self.assertIsNotNone(response.ust)

# ################################################################################################################################
# ################################################################################################################################

class UserLogoutTestCase(BaseTest):

    def xtest_user_logout(self):

        ust = self.post('/zato/sso/user/login', {
            'current_app': current_app,
            'username': super_user_name,
            'password': super_user_password,
        }).ust

        response = self.post('/zato/sso/user/logout', {
            'ust': ust,
            'current_app': current_app,
        })

        self.assertEquals(response.status, status_code.ok)
        self.assertIsNotNone(response.cid)

# ################################################################################################################################
# ################################################################################################################################

class UserGetTestCase(BaseTest):

    def xtest_user_get_by_user_id(self):

        username = self._get_random_username()
        password_must_change = True
        display_name = self._get_random_data()
        first_name = self._get_random_data()
        middle_name = self._get_random_data()
        last_name = self._get_random_data()
        email = self._get_random_data()
        is_locked = True
        sign_up_status = const.signup_status.before_confirmation

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'current_app': current_app,
            'username': username,
            'password_must_change': password_must_change,
            'display_name': display_name,
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'email': email,
            'is_locked': is_locked,
            'sign_up_status': sign_up_status,
        })

        self.assertEquals(response.status, status_code.ok)
        user_id = response.user_id

        response = self.get('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'current_app': 'CRM',
            'user_id': user_id,
        })

        self.assertEquals(response.status, status_code.ok)
        self.assertEquals(response.username, username)
        self.assertEquals(response.display_name, display_name)
        self.assertEquals(response.first_name, first_name)
        self.assertEquals(response.middle_name, middle_name)
        self.assertEquals(response.last_name, last_name)
        self.assertEquals(response.email, email)
        self.assertEquals(response.sign_up_status, sign_up_status)
        self.assertIs(response.password_must_change, password_must_change)
        self.assertIs(response.is_locked, is_locked)

# ################################################################################################################################

    def xtest_user_get_by_ust(self):

        now = datetime.utcnow()
        response = self.get('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'current_app': 'CRM',
        })

        self.assertEquals(response.status, status_code.ok)
        self.assertEquals(response.approval_status, const.approval_status.approved)
        self.assertEquals(response.approval_status_mod_by, 'auto')
        self.assertEquals(response.username, super_user_name)
        self.assertEquals(response.sign_up_status, const.signup_status.final)

        self.assertTrue(response.is_approval_needed)
        self.assertTrue(response.is_super_user)
        self.assertTrue(response.password_is_set)

        self.assertFalse(response.is_internal)
        self.assertFalse(response.is_locked)
        self.assertFalse(response.password_must_change)

        self._assert_user_dates(response, now, True)

# ################################################################################################################################
# ################################################################################################################################

class UserUpdateTestCase(BaseTest):

    def xtest_user_update_self(self):

        now = datetime.utcnow()
        username = self._get_random_username()
        password = self._get_random_data()

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'current_app': current_app,
            'username': username,
            'password': password,
        })

        self.assertEquals(response.status, status_code.ok)
        user_id = response.user_id

        response = self.post('/zato/sso/user/approve', {
            'ust': self.ctx.super_user_ust,
            'current_app': 'CRM',
            'user_id': user_id
        })

        self.assertEquals(response.status, status_code.ok)

        response = self.post('/zato/sso/user/login', {
            'current_app': current_app,
            'username': username,
            'password': password
        })

        self.assertEquals(response.status, status_code.ok)
        ust = response.ust

        display_name = self._get_random_data()
        first_name = self._get_random_data()
        middle_name = self._get_random_data()
        last_name = self._get_random_data()
        email = self._get_random_data()

        response = self.patch('/zato/sso/user', {
            'ust': ust,
            'current_app': current_app,
            'display_name': display_name,
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'email': email,
        })

        self.assertEquals(response.status, status_code.ok)

        response = self.get('/zato/sso/user', {
            'ust': ust,
            'current_app': current_app,
        })

        self.assertEquals(response.status, status_code.ok)
        self.assertIsNotNone(response.cid)
        self.assertIsNotNone(response.user_id)

        self.assertFalse(response.is_active)
        self.assertFalse(response.is_approval_needed)
        self.assertFalse(response.is_internal)
        self.assertFalse(response.is_locked)
        self.assertFalse(response.is_super_user)

        self.assertEquals(response.display_name, display_name)
        self.assertEquals(response.email, email)
        self.assertEquals(response.first_name, first_name)
        self.assertEquals(response.last_name, last_name)
        self.assertEquals(response.middle_name, middle_name)
        self.assertEquals(response.username, username)

# ################################################################################################################################

    def xtest_user_update_by_id(self):

        now = datetime.utcnow()
        username = self._get_random_username()
        password = self._get_random_data()

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'current_app': current_app,
            'username': username,
            'password': password,
        })

        self.assertEquals(response.status, status_code.ok)
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
            'current_app': current_app,
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

        self.assertEquals(response.status, status_code.ok)

        response = self.get('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'current_app': current_app,
            'user_id': user_id,
        })

        self.assertEquals(response.status, status_code.ok)
        self.assertIsNotNone(response.cid)

        self.assertEquals(response.user_id, user_id)
        self.assertEquals(response.display_name, display_name)
        self.assertEquals(response.email, email)
        self.assertEquals(response.first_name, first_name)
        self.assertEquals(response.last_name, last_name)
        self.assertEquals(response.middle_name, middle_name)
        self.assertEquals(response.username, username)

        self.assertEquals(response.is_locked, is_locked)
        self.assertEquals(response.password_expiry, password_expiry)
        self.assertEquals(response.password_must_change, password_must_change)
        self.assertEquals(response.sign_up_status, sign_up_status)
        self.assertEquals(response.approval_status, approval_status)

# ################################################################################################################################
# ################################################################################################################################

class UserDeleteTestCase(BaseTest):

    def xtest_user_delete_by_super_user(self):

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'current_app': current_app,
            'username': self._get_random_username(),
        })

        self.assertEquals(response.status, status_code.ok)
        user_id = response.user_id

        response = self.get('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'current_app': 'CRM',
            'user_id': user_id,
        })

        self.assertEquals(response.status, status_code.ok)

        response = self.delete('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'current_app': 'CRM',
            'user_id': user_id,
        })

        self.assertEquals(response.status, status_code.ok)

        response = self.get('/zato/sso/user/search', {
            'ust': self.ctx.super_user_ust,
            'current_app': 'CRM',
            'user_id': user_id,
        })

        self.assertEquals(response.status, status_code.ok)
        self.assertEquals(response.total, 0)

# ################################################################################################################################

    def xtest_user_delete_by_regular_user(self):

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'current_app': current_app,
            'username': self._get_random_username(),
        })

        self.assertEquals(response.status, status_code.ok)
        user_id1 = response.user_id

        response = self.get('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'current_app': 'CRM',
            'user_id': user_id1,
        })

        self.assertEquals(response.status, status_code.ok)

        username = self._get_random_username()
        password = self._get_random_data()

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'current_app': current_app,
            'username': username,
            'password': password,
        })

        self.assertEquals(response.status, status_code.ok)
        user_id2 = response.user_id

        self.post('/zato/sso/user/approve', {
            'ust': self.ctx.super_user_ust,
            'current_app': 'CRM',
            'user_id': user_id1
        })

        self.post('/zato/sso/user/approve', {
            'ust': self.ctx.super_user_ust,
            'current_app': 'CRM',
            'user_id': user_id2
        })

        response = self.post('/zato/sso/user/login', {
            'current_app': current_app,
            'username': username,
            'password': password,
        })

        self.assertEquals(response.status, status_code.ok)

        ust = response.ust

        response = self.delete('/zato/sso/user', {
            'ust': ust,
            'current_app': 'CRM',
            'user_id': user_id1,
        })

        self.assertEquals(response.status, status_code.error)
        self.assertListEqual(response.sub_status, [status_code.auth.not_allowed])

# ################################################################################################################################
# ################################################################################################################################

class UserChangePasswordTestCase(BaseTest):

    def test_user_change_password_self(self):

        username = self._get_random_username()
        password = self._get_random_data()

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'current_app': current_app,
            'username': username,
            'password': password,
        })

        user_id = response.user_id

        self.post('/zato/sso/user/approve', {
            'ust': self.ctx.super_user_ust,
            'current_app': 'CRM',
            'user_id': user_id
        })

        response = self.post('/zato/sso/user/login', {
            'current_app': current_app,
            'username': username,
            'password': password,
        })

        self.assertEquals(response.status, status_code.ok)
        self.assertIsNotNone(response.ust)

        ust = response.ust
        new_pasword = self._get_random_data()

        response = self.patch('/zato/sso/user/password', {
            'ust': ust,
            'current_app': current_app,
            'old_password': password,
            'new_password': new_pasword
        })

        self.assertEquals(response.status, status_code.ok)

        response = self.post('/zato/sso/user/login', {
            'current_app': current_app,
            'username': username,
            'password': password,
        })

        self.assertEquals(response.status, status_code.error)
        self.assertListEqual(response.sub_status, [status_code.auth.not_allowed])

        response = self.post('/zato/sso/user/login', {
            'current_app': current_app,
            'username': username,
            'password': new_pasword,
        })

        self.assertEquals(response.status, status_code.ok)
        self.assertIsNotNone(response.ust)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
