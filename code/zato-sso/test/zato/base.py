# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
import os
from datetime import datetime
from itertools import count
from json import dumps, loads
from unittest import TestCase

# Bunch
from bunch import bunchify

# dateutil
from dateutil.parser import parse as dt_parse

# sh
import sh

# requests
import requests

# Zato
from zato.common.crypto import CryptoManager
from zato.sso import const, status_code

# ################################################################################################################################

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ################################################################################################################################

class Config:
    current_app = 'CRM'

    super_user_name = 'admin1'
    super_user_password = 'hQ9nl93UDqGus'
    super_user_totp_key = 'KMCLCWN4YPMD2WO3'

    username_prefix = 'test.{}+{}'
    random_prefix = 'rand.{}+{}'

    server_location = os.path.expanduser('~/env/sso.test/server1')
    server_address  = 'http://localhost:17010{}'

class NotGiven:
    pass

# ################################################################################################################################
# ################################################################################################################################

class TestCtx(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.super_user_ust = None # type: unicode
        self.super_user_id = None # type: unicode
        self.config = Config

# ################################################################################################################################
# ################################################################################################################################

class BaseTest(TestCase):

# ################################################################################################################################

    def setUp(self):
        try:
            # Try to create a super-user ..
            #sh.zato('sso', 'create-super-user', Config.server_location, Config.super_user_name, '--password',
            #    Config.super_user_password, '--verbose')
            #sh.zato('sso', 'reset-totp-key', Config.server_location, Config.super_user_name, '--key',
            #    Config.super_user_totp_key, '--verbose')

            pass
        except Exception as e:
            # .. but ignore it if such a user already exists.
            if not 'User already exists' in e.args[0]:
                if isinstance(e, sh.ErrorReturnCode):
                    logger.warning('Shell exception %s', e.stderr)
                raise

        # Create a new context object for each test
        self.ctx = TestCtx()
        self._login_super_user()

        # A new counter for random data
        self.rand_counter = count()

# ################################################################################################################################

    def tearDown(self):
        self.ctx.reset()

# ################################################################################################################################

    def _get_random(self, prefix, _utcnow=datetime.utcnow):
        return prefix.format(_utcnow().isoformat(), next(self.rand_counter))

# ################################################################################################################################

    def _get_random_username(self):
        return self._get_random(Config.username_prefix)

# ################################################################################################################################

    def _get_random_data(self):
        return self._get_random(Config.random_prefix)

# ################################################################################################################################

    def _invoke(self, func, func_name, url_path, request, expect_ok, auth=None, _not_given='_test_not_given'):
        address = Config.server_address.format(url_path)

        request['current_app'] = Config.current_app
        data = dumps(request)

        logger.info('Invoking %s %s with %s', func_name, address, data)
        response = func(address, data=data, auth=auth)

        logger.info('Response received %s %s', response.status_code, response.text)

        data = loads(response.text)
        data = bunchify(data)

        return data

        # Most tests require status OK and CID
        if expect_ok:
            self.assertNotEquals(data.get('cid', _not_given), _not_given)
            self.assertEquals(data.status, status_code.ok)

        return data

    def get(self, url_path, request, expect_ok=True, auth=None):
        return self._invoke(requests.get, 'GET', url_path, request, expect_ok, auth)

    def post(self, url_path, request, expect_ok=True, auth=None):
        return self._invoke(requests.post, 'POST', url_path, request, expect_ok, auth)

    def patch(self, url_path, request, expect_ok=True, auth=None):
        return self._invoke(requests.patch, 'PATCH', url_path, request, expect_ok, auth)

    def delete(self, url_path, request, expect_ok=True, auth=None):
        return self._invoke(requests.delete, 'DELETE', url_path, request, expect_ok, auth)

# ################################################################################################################################

    def _login_super_user(self):
        response = self.post('/zato/sso/user/login', {
            'username': Config.super_user_name,
            'password': Config.super_user_password,
            'totp_code': CryptoManager.get_current_totp_code(Config.super_user_totp_key),
        })
        self.ctx.super_user_ust = response.ust

        response = self.get('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
        })
        self.ctx.super_user_id = response.user_id

# ################################################################################################################################

    def _assert_default_user_data(self, response, now):

        self.assertEquals(response.approval_status, const.approval_status.before_decision)
        self.assertEquals(response.sign_up_status, const.signup_status.final)

        self.assertTrue(response.is_active)
        self.assertTrue(response.password_is_set)

        self.assertTrue(response.user_id.startswith('zusr'))
        self.assertTrue(response.username.startswith('test.'))

        self.assertFalse(response.is_internal)
        self.assertFalse(response.is_locked)
        self.assertFalse(response.is_super_user)
        self.assertFalse(response.password_must_change)

        self.assertIsNotNone(response.approval_status_mod_by)
        self._assert_user_dates(response, now)

    def _assert_user_dates(self, response, now, is_default_user=False):

        now = now.isoformat()

        func = self.assertGreater if is_default_user else self.assertLess
        func(now, dt_parse(response.approval_status_mod_time).isoformat() + '.999999')
        func(now, dt_parse(response.password_last_set).isoformat() + '.999999')
        func(now, dt_parse(response.sign_up_time).isoformat() + '.999999')
        self.assertLess(now, dt_parse(response.password_expiry).isoformat() + '.999999')

# ################################################################################################################################

    def _approve(self, user_id):
        self.post('/zato/sso/user/approve', {
            'ust': self.ctx.super_user_ust,
            'user_id': user_id
        })

# ################################################################################################################################
# ################################################################################################################################
