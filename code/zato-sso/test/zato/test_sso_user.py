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

    def test_user_create(self):

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
    def test_user_signup(self):
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
    def test_confirm_signup(self):

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
    def test_approve(self):

        self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'current_app': current_app,
            'username': self._get_random_username(),
        })

        response = self.get('/zato/sso/user/search', {
            'ust': self.ctx.super_user_ust,
            'current_app': 'CRM',
            'approval_status': const.approval_status.before_decision
        })

        self.assertTrue(response.total > 0)
        user = response.result[0]

        self.post('/zato/sso/user/approve', {
            'ust': self.ctx.super_user_ust,
            'current_app': 'CRM',
            'user_id': user.user_id
        })

        response = self.get('/zato/sso/user/search', {
            'ust': self.ctx.super_user_ust,
            'current_app': 'CRM',
            'user_id': user.user_id
        })

        self.assertTrue(response.total > 0)
        user = response.result[0]

        self.assertEquals(user.approval_status, const.approval_status.approved)

# ################################################################################################################################
# ################################################################################################################################

class UserRejectTestCase(BaseTest):
    def test_reject(self):

        self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'current_app': current_app,
            'username': self._get_random_username(),
        })

        response = self.get('/zato/sso/user/search', {
            'ust': self.ctx.super_user_ust,
            'current_app': 'CRM',
            'approval_status': const.approval_status.before_decision
        })

        self.assertTrue(response.total > 0)
        user = response.result[0]

        self.post('/zato/sso/user/reject', {
            'ust': self.ctx.super_user_ust,
            'current_app': 'CRM',
            'user_id': user.user_id
        })

        response = self.get('/zato/sso/user/search', {
            'ust': self.ctx.super_user_ust,
            'current_app': 'CRM',
            'user_id': user.user_id
        })

        self.assertTrue(response.total > 0)
        user = response.result[0]

        self.assertEquals(user.approval_status, const.approval_status.rejected)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
