# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from datetime import datetime
from itertools import count
from unittest import TestCase

# Bunch
from bunch import bunchify

# ciso8601
from ciso8601 import parse_datetime

# requests
import requests

# sh
import sh

# Zato
from zato.common.util.api import get_odb_session_from_server_dir
from zato.common.json_internal import dumps, loads
from zato.common.crypto.totp_ import TOTPManager
from zato.common.sso import TestConfig
from zato.sso import const, status_code
from zato.sso.odb.query import get_user_by_name

# ################################################################################################################################

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ################################################################################################################################

# Rename for backward compatibility
Config = TestConfig

class NotGiven:
    pass

# ################################################################################################################################
# ################################################################################################################################

class TestCtx(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.super_user_ust = None # type: str
        self.super_user_id = None # type: str
        self.config = Config

# ################################################################################################################################
# ################################################################################################################################

class BaseTest(TestCase):

# ################################################################################################################################

    def setUp(self):
        try:

            # Create the test user if the account does not already exist ..
            odb_session = self.get_odb_session()

            if not get_user_by_name(odb_session, Config.super_user_name, False):

                # .. create the user ..
                sh.zato('sso', 'create-super-user', Config.server_location, Config.super_user_name, '--password',
                  Config.super_user_password, '--verbose')

                # .. and set the TOTP ..
                sh.zato('sso', 'reset-totp-key', Config.server_location, Config.super_user_name, '--key',
                  Config.super_user_totp_key, '--verbose')

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

    def get_odb_session(self):
        return get_odb_session_from_server_dir(Config.server_location)

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

        # Most tests require status OK and CID
        if expect_ok:
            self.assertNotEqual(data.get('cid', _not_given), _not_given)
            self.assertEqual(data.status, status_code.ok)

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
            'totp_code': TOTPManager.get_current_totp_code(Config.super_user_totp_key),
        })
        self.ctx.super_user_ust = response.ust

        response = self.get('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
        })
        self.ctx.super_user_id = response.user_id

# ################################################################################################################################

    def _assert_default_user_data(self, response, now, approval_status=None):

        self.assertEqual(response.approval_status, approval_status or const.approval_status.before_decision)
        self.assertEqual(response.sign_up_status, const.signup_status.final)

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
        func(now, parse_datetime(response.approval_status_mod_time).isoformat() + '.999999')
        func(now, parse_datetime(response.password_last_set).isoformat() + '.999999')
        func(now, parse_datetime(response.sign_up_time).isoformat() + '.999999')
        self.assertLess(now, parse_datetime(response.password_expiry).isoformat() + '.999999')

# ################################################################################################################################

    def _approve(self, user_id):
        self.post('/zato/sso/user/approve', {
            'ust': self.ctx.super_user_ust,
            'user_id': user_id
        })

# ################################################################################################################################
# ################################################################################################################################
