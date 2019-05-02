# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from unittest import main

# Zato
from base import BaseTest, Config
from zato.sso import const, status_code

# ################################################################################################################################
# ################################################################################################################################

class SessionVerifyTestCase(BaseTest):

# ################################################################################################################################

    def xtest_verify_self(self):

        response = self.post('/zato/sso/user/session', {
            'current_ust': self.ctx.super_user_ust,
            'target_ust': self.ctx.super_user_ust,
            'current_app': Config.current_app,
        })

        self.assertTrue(response.is_valid)

# ################################################################################################################################

    def test_verify_another_user(self):

        username = self._get_random_username()
        password = self._get_random_data()

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'current_app': Config.current_app,
            'username': username,
            'password': password,
        })

        user_id = response.user_id

        self.post('/zato/sso/user/approve', {
            'ust': self.ctx.super_user_ust,
            'current_app': 'CRM',
            'user_id': user_id
        })

        self.post('/zato/sso/user/approve', {
            'ust': self.ctx.super_user_ust,
            'current_app': 'CRM',
            'user_id': user_id
        })

        response = self.post('/zato/sso/user/login', {
            'current_app': Config.current_app,
            'username': username,
            'password': password,
        })

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
