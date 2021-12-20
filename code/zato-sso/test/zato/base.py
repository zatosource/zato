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

# ciso8601
from ciso8601 import parse_datetime

# sh
import sh

# Zato
from zato.common.util.api import get_odb_session_from_server_dir
from zato.common.crypto.totp_ import TOTPManager
from zato.common.test.config import TestConfig
from zato.common.test.rest_client import RESTClientTestCase
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

class TestCtx:

    def __init__(self):
        self.reset()

    def reset(self):
        self.super_user_ust = None # type: str
        self.super_user_id = None # type: str
        self.config = Config

# ################################################################################################################################
# ################################################################################################################################

class BaseTest(RESTClientTestCase):

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

# ################################################################################################################################

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

    def _create_and_approve_user(self, username=None, password=None):

        username = username or self._get_random_username()
        password = password or self._get_random_data()

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': username,
            'password': password,
        })

        self.assertEqual(response.status, status_code.ok)

        response = self.post('/zato/sso/user/approve', {
            'ust': self.ctx.super_user_ust,
            'user_id': response.user_id
        })

        self.assertEqual(response.status, status_code.ok)

# ################################################################################################################################
# ################################################################################################################################
