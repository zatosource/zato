# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from unittest import main

# ciso8601
try:
    from zato.common.util.api import parse_datetime
except ImportError:
    from dateutil.parser import parse as parse_datetime

# Zato
from base import BaseTest
from zato.sso import status_code

# ################################################################################################################################
# ################################################################################################################################

class SessionVerifyTestCase(BaseTest):

# ################################################################################################################################

    def test_verify_self(self):

        response = self.post('/zato/sso/user/session', {
            'current_ust': self.ctx.super_user_ust,
            'target_ust': self.ctx.super_user_ust,
        })

        self.assertTrue(response.is_valid)

# ################################################################################################################################

    def xtest_verify_another_user(self):

        username = self._get_random_username()
        password = self._get_random_data()

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': username,
            'password': password,
        })

        user_id = response.user_id
        self._approve(user_id)

        response = self.post('/zato/sso/user/login', {
            'username': username,
            'password': password,
        })

        ust = response.ust

        response = self.post('/zato/sso/user/session', {
            'current_ust': self.ctx.super_user_ust,
            'target_ust': ust,
        })

        self.assertTrue(response.is_valid)

        response = self.post('/zato/sso/user/logout', {
            'ust': ust,
        })

        response = self.post('/zato/sso/user/session', {
            'current_ust': self.ctx.super_user_ust,
            'target_ust': ust,
        })

        self.assertFalse(response.is_valid)

# ################################################################################################################################

    def xtest_verify_not_super_user(self):

        username1 = self._get_random_username()
        password1 = self._get_random_data()

        username2 = self._get_random_username()
        password2 = self._get_random_data()

        response1 = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': username1,
            'password': password1,
        })

        response2 = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': username2,
            'password': password2,
        })

        user_id1 = response1.user_id
        user_id2 = response2.user_id

        self._approve(user_id1)
        self._approve(user_id2)

        response1 = self.post('/zato/sso/user/login', {
            'username': username1,
            'password': password1,
        })

        response2 = self.post('/zato/sso/user/login', {
            'username': username1,
            'password': password1,
        })

        ust1 = response1.ust
        ust2 = response2.ust

        response1 = self.post('/zato/sso/user/session', {
            'current_ust': ust1,
            'target_ust': ust2,
        }, False)

        response2 = self.post('/zato/sso/user/session', {
            'current_ust': ust2,
            'target_ust': ust1,
        }, False)

        response3 = self.post('/zato/sso/user/session', {
            'current_ust': ust1,
            'target_ust': ust1,
        }, False)

        response4 = self.post('/zato/sso/user/session', {
            'current_ust': ust2,
            'target_ust': ust2,
        }, False)

        response5 = self.post('/zato/sso/user/session', {
            'current_ust': ust1,
            'target_ust': self.ctx.super_user_ust,
        }, False)

        response6 = self.post('/zato/sso/user/session', {
            'current_ust': ust1,
            'target_ust': self.ctx.super_user_ust,
        }, False)

        self.assertEqual(response1.status, status_code.error)
        self.assertListEqual(response1.sub_status, [status_code.auth.not_allowed])

        self.assertEqual(response2.status, status_code.error)
        self.assertListEqual(response2.sub_status, [status_code.auth.not_allowed])

        self.assertEqual(response3.status, status_code.error)
        self.assertListEqual(response3.sub_status, [status_code.auth.not_allowed])

        self.assertEqual(response4.status, status_code.error)
        self.assertListEqual(response4.sub_status, [status_code.auth.not_allowed])

        self.assertEqual(response5.status, status_code.error)
        self.assertListEqual(response5.sub_status, [status_code.auth.not_allowed])

        self.assertEqual(response6.status, status_code.error)
        self.assertListEqual(response6.sub_status, [status_code.auth.not_allowed])

# ################################################################################################################################
# ################################################################################################################################

class SessionRenewTestCase(BaseTest):

    def xtest_renew(self):

        now = datetime.utcnow()

        response = self.patch('/zato/sso/user/session', {
            'ust': self.ctx.super_user_ust,
        })

        self.assertGreater(parse_datetime(response.expiration_time), now)

# ################################################################################################################################
# ################################################################################################################################

class SessionGetTestCase(BaseTest):

# ################################################################################################################################

    def xtest_get_regular_user(self):

        username = self._get_random_username()
        password = self._get_random_data()

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': username,
            'password': password,
        })

        user_id = response.user_id
        self._approve(user_id)

        response = self.post('/zato/sso/user/login', {
            'username': username,
            'password': password,
        })

        ust = response.ust

        response = self.get('/zato/sso/user/session', {
            'current_ust': ust,
            'target_ust': self.ctx.super_user_ust,
        }, False)

        self.assertEqual(response.status, status_code.error)
        self.assertListEqual(response.sub_status, [status_code.auth.not_allowed])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
