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

# dateutil
from dateutil.parser import parse as dt_parse

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

    def test(self):

        now = datetime.utcnow()
        username = self._get_random_username()

        request = {
            'ust': self.ctx.super_user_ust,
            'current_app': current_app,
            'username': username
        }

        response = self.post('/zato/sso/user', request)

        self.assertEquals(response.status, status_code.ok)
        self.assertEquals(response.approval_status, const.approval_status.before_decision)
        self.assertEquals(response.sign_up_status, const.signup_status.final)

        self.assertTrue(response.is_active)
        self.assertTrue(response.is_approval_needed)
        self.assertTrue(response.password_is_set)

        self.assertTrue(response.user_id.startswith('zusr'))
        self.assertTrue(response.username.startswith('test.'))

        self.assertFalse(response.is_internal)
        self.assertFalse(response.is_locked)
        self.assertFalse(response.is_super_user)
        self.assertFalse(response.password_must_change)

        self.assertIsNotNone(response.approval_status_mod_by)
        self.assertIsNotNone(response.cid)

        self.assertLess(now, dt_parse(response.approval_status_mod_time))
        self.assertLess(now, dt_parse(response.password_last_set))
        self.assertLess(now, dt_parse(response.sign_up_time))
        self.assertLess(now, dt_parse(response.password_expiry))

# ################################################################################################################################
# ################################################################################################################################

class UserSignupTestCase(BaseTest):
    def test(self):
        response = self.post('/zato/sso/user/signup', {
            'username': self._get_random_username(),
            'password': self._get_random_password(),
            'current_app': current_app,
            'app_list': [current_app]
        })

        self.assertEquals(response.status, status_code.ok)
        self.assertIsNotNone(response.cid)
        self.assertIsNotNone(response.confirm_token)

# ################################################################################################################################
# ################################################################################################################################

class UserConfirmSignupTestCase(BaseTest):
    def test(self):

        response = self.post('/zato/sso/user/signup', {
            'username': self._get_random_username(),
            'password': self._get_random_password(),
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

if __name__ == '__main__':
    main()
