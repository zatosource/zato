# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import main

# Zato
from base import BaseTest
from zato.common import SEC_DEF_TYPE

# For Pyflakes
SEC_DEF_TYPE = SEC_DEF_TYPE

# ################################################################################################################################

basic_auth_user_name = 'pubapi'

# ################################################################################################################################
# ################################################################################################################################

class TOTPTestCase(BaseTest):

    def test_user_login_totp(self):

        response = self.post('/zato/sso/user/login', {
            'username': self.ctx.config.super_user_name,
            'password': self.ctx.config.super_user_password,
        })

        self.assertIsNotNone(response.ust)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
