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
from zato.sso import const, status_code

# ################################################################################################################################

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ################################################################################################################################

class Config:
    current_app = 'CRM'

    super_user_name = 'admin1'
    super_user_password = 'hQ9nl93UDqGus'

    username_prefix = 'test.{}+{}'
    random_prefix = 'rand.{}+{}'

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

class TestCtx(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.super_user_ust = None # type: unicode

# ################################################################################################################################
# ################################################################################################################################

class BaseTest(TestCase):

# ################################################################################################################################

    def setUp(self):
        try:
            # Try to create a super-user ..
            #sh.zato('sso', 'create-super-user', server_location, super_user_name, '--password', super_user_password, '--verbose')
            pass
        except Exception as e:
            # .. but ignore it if such a user already exists.
            if not 'User already exists' in e.args[0]:
                if isinstance(e, sh.ErrorReturnCode):
                    logger.warn('Shell exception %s', e.stderr)
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

    def _invoke(self, func, func_name, url_path, request):
        address = Config.server_address.format(url_path)
        data = dumps(request)

        logger.info('Invoking %s %s with %s', func_name, address, data)
        response = func(address, data=data)

        logger.info('Response received %s %s', response.status_code, response.text)

        data = loads(response.text)
        return bunchify(data)

    def get(self, url_path, request):
        return self._invoke(requests.get, 'GET', url_path, request)

    def post(self, url_path, request):
        return self._invoke(requests.post, 'POST', url_path, request)

    def patch(self, url_path, request):
        return self._invoke(requests.patch, 'PATCH', url_path, request)

    def delete(self, url_path, request):
        return self._invoke(requests.delete, 'DELETE', url_path, request)

# ################################################################################################################################

    def _login_super_user(self):
        request = deepcopy(Request.login) # type: Bunch
        request.username = Config.super_user_name
        request.password = Config.super_user_password
        request.current_app = Config.current_app

        url_path = '/zato/sso/user/login'
        response = self.post(url_path, request)

        self.ctx.super_user_ust = response.ust

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

        func = self.assertGreater if is_default_user else self.assertLess
        func(now, dt_parse(response.approval_status_mod_time))
        func(now, dt_parse(response.password_last_set))
        func(now, dt_parse(response.sign_up_time))
        self.assertLess(now, dt_parse(response.password_expiry))

# ################################################################################################################################
# ################################################################################################################################
