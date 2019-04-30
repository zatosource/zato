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
from random import randint
from unittest import TestCase, main

# Bunch
from bunch import bunchify

# sh
import sh

# requests
import requests

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

class TestCtx(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.super_user_ust = None # type: unicode

# ################################################################################################################################
# ################################################################################################################################

class BaseClass(TestCase):

# ################################################################################################################################

    def setUp(self):
        try:
            # Try to create a super-user ..
            sh.zato('sso', 'create-super-user', server_location, super_user_name, '--password', super_user_password, '--verbose')
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

    def _get_random_username(self, _utcnow=datetime.utcnow):
        return username_prefix.format(_utcnow().isoformat(), next(self.rand_counter))

# ################################################################################################################################

    def _invoke(self, func, func_name, url_path, request):
        address = server_address.format(url_path)
        data = dumps(request)

        logger.info('Invoking %s %s with %s', func_name, address, data)
        response = func(address, data=data)

        logger.info('Response received %s %s', response.status_code, response.text)

        data = loads(response.text)
        return bunchify(data)

    def post(self, url_path, request):
        return self._invoke(requests.post, 'POST', url_path, request)

# ################################################################################################################################

    def _login_super_user(self):
        request = deepcopy(Request.login) # type: Bunch
        request.username = super_user_name
        request.password = super_user_password
        request.current_app = current_app

        url_path = '/zato/sso/user/login'
        response = self.post(url_path, request)

        self.ctx.super_user_ust = response.ust

# ################################################################################################################################
# ################################################################################################################################

class UserCreateTestCase(BaseClass):

    def test_default_values(self):
        username = self._get_random_username()

        request = {
            'ust': self.ctx.super_user_ust,
            'current_app': current_app,
            'username': username
        }

        response = self.post('/zato/sso/user', request)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()
