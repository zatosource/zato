# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from datetime import datetime
from itertools import count

# Bunch

# ciso8601
try:
    from zato.common.util.api import parse_datetime
except ImportError:
    from dateutil.parser import parse as parse_datetime

# sh
import sh

# Zato
from zato.common.util.api import get_odb_session_from_server_dir
from zato.common.crypto.totp_ import TOTPManager
from zato.common.test.config import TestConfig
from zato.common.test.rest_client import RESTClientTestCase
from zato.common.test import rand_string
from zato.common.typing_ import cast_
from zato.sso import const, status_code
from zato.sso.odb.query import get_user_by_name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

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
        self.config = TestConfig

# ################################################################################################################################
# ################################################################################################################################

class BaseTest(RESTClientTestCase):

# ################################################################################################################################

    def setUp(self):

        # stdlib
        import os

        if not os.environ.get('ZATO_TEST_SSO'):
            self.ctx = cast_('any_', None)
            return

        # Zato
        from zato.common.util.cli import get_zato_sh_command

        try:

            # Create the test user if the account does not already exist ..
            odb_session = self.get_odb_session()

            if not get_user_by_name(odb_session, TestConfig.super_user_name, False):

                command = get_zato_sh_command()

                # .. create the user ..
                command('sso', 'create-super-user', TestConfig.server_location, TestConfig.super_user_name,
                    '--password', TestConfig.super_user_password,
                    '--email', 'test@example.com',
                    '--verbose')

                # .. and set the TOTP ..
                command('sso', 'reset-totp-key', TestConfig.server_location, TestConfig.super_user_name,
                    '--key', TestConfig.super_user_totp_key,
                    '--verbose')

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
        if self.ctx:
            self.ctx.reset()

# ################################################################################################################################

    def get_odb_session(self):
        return get_odb_session_from_server_dir(TestConfig.server_location)

# ################################################################################################################################

    def _get_random(self, prefix, _utcnow=datetime.utcnow):
        return prefix.format(_utcnow().isoformat(), next(self.rand_counter)) + '.' + rand_string()[:10]

# ################################################################################################################################

    def _get_random_username(self):
        return self._get_random(TestConfig.username_prefix)

# ################################################################################################################################

    def _get_random_data(self):
        return self._get_random(TestConfig.random_prefix)

# ################################################################################################################################

    def _login_super_user(self):
        response = self.post('/zato/sso/user/login', {
            'username': TestConfig.super_user_name,
            'password': TestConfig.super_user_password,
            'totp_code': TOTPManager.get_current_totp_code(TestConfig.super_user_totp_key),
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
