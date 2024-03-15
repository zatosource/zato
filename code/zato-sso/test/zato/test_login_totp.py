# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main

# Zato
from base import BaseTest
from zato.common.api import SEC_DEF_TYPE
from zato.common.crypto.totp_ import TOTPManager
from zato.sso import status_code

# For Pyflakes
SEC_DEF_TYPE = SEC_DEF_TYPE

# ################################################################################################################################

basic_auth_user_name = 'pubapi'

# ################################################################################################################################
# ################################################################################################################################

class TOTPTestCase(BaseTest):

# ################################################################################################################################

    def test_user_login_totp_valid(self):

        self.patch('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'is_totp_enabled': True,
            'totp_key': self.ctx.config.super_user_totp_key,
        })

        response = self.post('/zato/sso/user/login', {
            'username': self.ctx.config.super_user_name,
            'password': self.ctx.config.super_user_password,
            'totp_code': TOTPManager.get_current_totp_code(self.ctx.config.super_user_totp_key),
        })

        self.assertIsNotNone(response.ust)

# ################################################################################################################################

    def test_user_login_totp_invalid(self):

        self.patch('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'is_totp_enabled': True,
            'totp_key': self.ctx.config.super_user_totp_key,
        })

        response = self.post('/zato/sso/user/login', {
            'username': self.ctx.config.super_user_name,
            'password': self.ctx.config.super_user_password,
            'totp_code': 'invalid'
        }, False)

        self.assertEqual(response.status, status_code.error)
        self.assertListEqual(response.sub_status, [status_code.auth.not_allowed])

# ################################################################################################################################

    def test_user_login_totp_missing(self):

        self.patch('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'is_totp_enabled': True,
            'totp_key': self.ctx.config.super_user_totp_key,
        })

        response = self.post('/zato/sso/user/login', {
            'username': self.ctx.config.super_user_name,
            'password': self.ctx.config.super_user_password,
        }, False)

        self.assertEqual(response.status, status_code.error)
        self.assertListEqual(response.sub_status, [status_code.auth.totp_missing])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
